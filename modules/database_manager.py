"""Database Manager for O2C AI Monitor"""
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
import pandas as pd

from .config import DB_PATH, LOG_DIR


class DatabaseManager:
    """
    Single responsibility: talk to SQLite database.
    All other classes use this — nothing talks to DB directly.
    """

    def __init__(self, db_path=str(DB_PATH)):
        self.db_path = db_path
        self.logger = self._make_logger()
        self._build_schema()
        print(f"✅ DatabaseManager ready → {self.db_path}")

    def _make_logger(self):
        log_file = LOG_DIR / f"monitor_{datetime.now():%Y%m%d}.log"
        logger = logging.getLogger("IndiaMonitor")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            fh = logging.FileHandler(log_file)
            fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
            logger.addHandler(fh)
        return logger

    @contextmanager
    def connection(self):
        """Safe auto-commit / auto-rollback connection"""
        conn = sqlite3.connect(
            self.db_path,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.logger.error(f"DB error: {e}")
            raise
        finally:
            conn.close()

    def _build_schema(self):
        schema = """
        CREATE TABLE IF NOT EXISTS scrape_sessions (
            session_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            session_type     TEXT    NOT NULL,
            started_at       TEXT    NOT NULL,
            completed_at     TEXT,
            status           TEXT    DEFAULT 'running',
            cities_fetched   INTEGER DEFAULT 0,
            articles_found   INTEGER DEFAULT 0,
            error_message    TEXT
        );

        CREATE TABLE IF NOT EXISTS weather_readings (
            reading_id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id          INTEGER,
            city_name           TEXT    NOT NULL,
            state               TEXT,
            recorded_at         TEXT    NOT NULL,
            date_only           TEXT    NOT NULL,
            hour_of_day         INTEGER NOT NULL,
            temperature         REAL,
            feels_like          REAL,
            temp_min            REAL,
            temp_max            REAL,
            humidity            INTEGER,
            pressure            REAL,
            visibility_km       REAL,
            cloudiness          INTEGER,
            weather_main        TEXT,
            weather_description TEXT,
            wind_speed          REAL,
            wind_direction      INTEGER,
            rain_1h             REAL DEFAULT 0,
            snow_1h             REAL DEFAULT 0,
            data_source         TEXT DEFAULT 'OpenWeatherMap',
            UNIQUE(city_name, date_only, hour_of_day)
        );

        CREATE TABLE IF NOT EXISTS strike_news (
            news_id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id       INTEGER,
            title            TEXT    NOT NULL,
            description      TEXT,
            url              TEXT,
            source_name      TEXT,
            keyword_matched  TEXT,
            city_mentioned   TEXT,
            state_mentioned  TEXT,
            severity         TEXT,
            strike_type      TEXT,
            published_date   TEXT,
            scraped_at       TEXT    NOT NULL,
            UNIQUE(title, source_name)
        );

        CREATE TABLE IF NOT EXISTS weather_alerts (
            alert_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id    INTEGER,
            city_name     TEXT NOT NULL,
            state         TEXT,
            alert_type    TEXT NOT NULL,
            alert_message TEXT NOT NULL,
            severity      TEXT,
            triggered_at  TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS daily_summaries (
            summary_id          INTEGER PRIMARY KEY AUTOINCREMENT,
            summary_date        TEXT NOT NULL,
            city_name           TEXT NOT NULL,
            state               TEXT,
            avg_temperature     REAL,
            max_temperature     REAL,
            min_temperature     REAL,
            avg_humidity        REAL,
            total_rainfall      REAL DEFAULT 0,
            avg_wind_speed      REAL,
            dominant_weather    TEXT,
            strike_count        INTEGER DEFAULT 0,
            high_severity_count INTEGER DEFAULT 0,
            weather_alert_count INTEGER DEFAULT 0,
            updated_at          TEXT,
            UNIQUE(summary_date, city_name)
        );

        CREATE TABLE IF NOT EXISTS rag_analyses (
            analysis_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            news_id         INTEGER,
            strike_title    TEXT NOT NULL,
            question        TEXT NOT NULL,
            answer          TEXT NOT NULL,
            sources         TEXT,
            confidence      REAL,
            analyzed_at     TEXT NOT NULL,
            FOREIGN KEY(news_id) REFERENCES strike_news(news_id)
        );

        CREATE INDEX IF NOT EXISTS idx_wr_city_date ON weather_readings(city_name, date_only);
        CREATE INDEX IF NOT EXISTS idx_wr_date      ON weather_readings(date_only);
        CREATE INDEX IF NOT EXISTS idx_sn_date      ON strike_news(published_date);
        CREATE INDEX IF NOT EXISTS idx_sn_city      ON strike_news(city_mentioned);
        CREATE INDEX IF NOT EXISTS idx_ds_date      ON daily_summaries(summary_date);
        CREATE INDEX IF NOT EXISTS idx_rag_news     ON rag_analyses(news_id);
        """
        with self.connection() as conn:
            conn.executescript(schema)
        self.logger.info("Schema ready")

    # ── Session Management ─────────────────────────────────
    
    def session_start(self, session_type="full"):
        with self.connection() as conn:
            cur = conn.execute(
                "INSERT INTO scrape_sessions (session_type, started_at, status) VALUES (?,?,?)",
                (session_type, datetime.now().isoformat(), "running")
            )
            sid = cur.lastrowid
        self.logger.info(f"Session {sid} started [{session_type}]")
        return sid

    def session_end(self, sid, status="success", cities=0, articles=0, error=None):
        with self.connection() as conn:
            conn.execute("""
                UPDATE scrape_sessions
                SET completed_at=?, status=?, cities_fetched=?,
                    articles_found=?, error_message=?
                WHERE session_id=?
            """, (datetime.now().isoformat(), status, cities, articles, error, sid))
        self.logger.info(f"Session {sid} ended [{status}]")

    # ── Write Operations ───────────────────────────────────

    def write_weather(self, records: list, session_id: int) -> tuple:
        """Insert weather records. Returns (saved, skipped)"""
        saved = skipped = 0
        with self.connection() as conn:
            for r in records:
                try:
                    ts_raw = r.get("recorded_at") or r.get("timestamp") or datetime.now().isoformat()
                    try:
                        ts = datetime.strptime(str(ts_raw), "%Y-%m-%d %H:%M:%S")
                    except:
                        ts = datetime.fromisoformat(str(ts_raw)[:19])

                    conn.execute("""
                        INSERT OR IGNORE INTO weather_readings (
                            session_id, city_name, state, recorded_at, date_only, hour_of_day,
                            temperature, feels_like, temp_min, temp_max, humidity, pressure,
                            visibility_km, cloudiness, weather_main, weather_description,
                            wind_speed, wind_direction, rain_1h, snow_1h, data_source
                        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """, (
                        session_id, r.get("city_name") or r.get("city"), r.get("state"),
                        ts.isoformat(), ts.strftime("%Y-%m-%d"), ts.hour,
                        r.get("temperature"), r.get("feels_like"), r.get("temp_min"), r.get("temp_max"),
                        r.get("humidity"), r.get("pressure"), r.get("visibility_km") or r.get("visibility"),
                        r.get("cloudiness"), r.get("weather_main"),
                        r.get("weather_description") or r.get("description"),
                        r.get("wind_speed"), r.get("wind_direction") or r.get("wind_deg"),
                        r.get("rain_1h", 0), r.get("snow_1h", 0),
                        r.get("data_source", "OpenWeatherMap"),
                    ))
                    chg = conn.execute("SELECT changes()").fetchone()[0]
                    if chg:
                        saved += 1
                    else:
                        skipped += 1
                except Exception as e:
                    self.logger.error(f"write_weather error [{r.get('city_name')}]: {e}")
        return saved, skipped

    def write_strikes(self, articles: list, session_id: int) -> tuple:
        """Insert strike news. Returns (saved, skipped)"""
        saved = skipped = 0
        with self.connection() as conn:
            for a in articles:
                try:
                    sev = str(a.get("severity", "LOW")).replace("🔴 ", "").replace("🟡 ", "").replace("🟢 ", "")
                    pub_date = None
                    raw = a.get("published_date") or a.get("published", "")
                    if raw:
                        try:
                            pub_date = pd.to_datetime(raw).strftime("%Y-%m-%d")
                        except:
                            pub_date = datetime.now().strftime("%Y-%m-%d")

                    conn.execute("""
                        INSERT OR IGNORE INTO strike_news (
                            session_id, title, description, url, source_name, keyword_matched,
                            city_mentioned, state_mentioned, severity, strike_type,
                            published_date, scraped_at
                        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                    """, (
                        session_id, str(a.get("title", ""))[:500],
                        str(a.get("description", ""))[:2000], str(a.get("url", ""))[:500],
                        str(a.get("source_name") or a.get("source", "Unknown"))[:100],
                        str(a.get("keyword_matched") or a.get("keyword", ""))[:100],
                        str(a.get("city_mentioned") or a.get("city", "Unknown"))[:100],
                        str(a.get("state_mentioned", ""))[:100], sev,
                        str(a.get("strike_type", "general"))[:50],
                        pub_date, datetime.now().isoformat()
                    ))
                    chg = conn.execute("SELECT changes()").fetchone()[0]
                    if chg:
                        saved += 1
                    else:
                        skipped += 1
                except Exception as e:
                    self.logger.error(f"write_strikes error: {e}")
        return saved, skipped

    def write_rag_analysis(self, news_id: int, strike_title: str, question: str, 
                          answer: str, sources: list, confidence: float = None) -> int:
        """Store RAG analysis result. Returns analysis_id."""
        import json
        with self.connection() as conn:
            cur = conn.execute("""
                INSERT INTO rag_analyses (
                    news_id, strike_title, question, answer, sources, confidence, analyzed_at
                ) VALUES (?,?,?,?,?,?,?)
            """, (
                news_id, strike_title, question, answer, 
                json.dumps(sources), confidence, datetime.now().isoformat()
            ))
            return cur.lastrowid

    # ── Read Operations ────────────────────────────────────

    def read_weather(self, date: str = None, city: str = None) -> pd.DataFrame:
        """Read weather records"""
        with self.connection() as conn:
            where = []
            params = []
            if date:
                where.append("date_only = ?")
                params.append(date)
            if city:
                where.append("city_name = ?")
                params.append(city)
            
            sql = "SELECT * FROM weather_readings"
            if where:
                sql += " WHERE " + " AND ".join(where)
            sql += " ORDER BY recorded_at DESC"
            
            return pd.read_sql_query(sql, conn, params=params)

    def read_strikes(self, date: str = None, city: str = None) -> pd.DataFrame:
        """Read strike news"""
        with self.connection() as conn:
            where = []
            params = []
            if date:
                where.append("published_date = ?")
                params.append(date)
            if city:
                where.append("city_mentioned = ?")
                params.append(city)
            
            sql = "SELECT * FROM strike_news"
            if where:
                sql += " WHERE " + " AND ".join(where)
            sql += " ORDER BY scraped_at DESC"
            
            return pd.read_sql_query(sql, conn, params=params)

    def read_rag_analyses(self, news_id: int = None) -> pd.DataFrame:
        """Read RAG analysis results"""
        with self.connection() as conn:
            if news_id:
                return pd.read_sql_query(
                    "SELECT * FROM rag_analyses WHERE news_id = ? ORDER BY analyzed_at DESC",
                    conn, params=[news_id]
                )
            else:
                return pd.read_sql_query(
                    "SELECT * FROM rag_analyses ORDER BY analyzed_at DESC",
                    conn
                )

    def get_stats(self) -> dict:
        """Get database statistics"""
        with self.connection() as conn:
            stats = {}
            stats["weather_records"] = conn.execute("SELECT COUNT(*) FROM weather_readings").fetchone()[0]
            stats["strike_articles"] = conn.execute("SELECT COUNT(*) FROM strike_news").fetchone()[0]
            stats["rag_analyses"] = conn.execute("SELECT COUNT(*) FROM rag_analyses").fetchone()[0]
            stats["sessions"] = conn.execute("SELECT COUNT(*) FROM scrape_sessions").fetchone()[0]
            return stats