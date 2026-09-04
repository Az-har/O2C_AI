"""Database Manager for O2C AI Monitor"""
import sqlite3
import logging
import queue
import threading
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
import pandas as pd

from .config import DB_PATH, LOG_DIR


class DatabaseManager:
    """
    Single responsibility: talk to SQLite database.
    Central repository for all data access across the O2C AI system.
    Equipped with thread-safe connection pooling to prevent connection thrashing.
    """

    def __init__(self, db_path=str(DB_PATH), pool_size: int = 8):
        self.db_path = str(db_path)
        self.pool_size = pool_size
        self._pool = queue.Queue(maxsize=pool_size)
        self.logger = self._make_logger()
        self._build_schema()
        self._apply_migrations()
        print(f"✅ DatabaseManager ready (Connection Pool: {self.pool_size}) → {self.db_path}")

    def _make_logger(self):
        log_file = LOG_DIR / f"monitor_{datetime.now():%Y%m%d}.log"
        logger = logging.getLogger("IndiaMonitor")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            fh = logging.FileHandler(log_file)
            fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
            logger.addHandler(fh)
        return logger

    def _create_raw_connection(self) -> sqlite3.Connection:
        """Create an optimized SQLite connection with WAL mode and memory-mapping"""
        conn = sqlite3.connect(
            self.db_path,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            check_same_thread=False
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=-64000")
        conn.execute("PRAGMA mmap_size=268435456")
        return conn

    def _get_connection(self) -> sqlite3.Connection:
        """Fetch a connection from pool or create a new one if pool is empty"""
        try:
            return self._pool.get_nowait()
        except queue.Empty:
            return self._create_raw_connection()

    def _release_connection(self, conn: sqlite3.Connection):
        """Return connection to pool or close if pool is full"""
        try:
            self._pool.put_nowait(conn)
        except queue.Full:
            try:
                conn.close()
            except Exception:
                pass

    @contextmanager
    def connection(self):
        """Safe auto-commit / auto-rollback pooled connection context manager"""
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.logger.error(f"DB error: {e}")
            raise
        finally:
            self._release_connection(conn)

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

        CREATE TABLE IF NOT EXISTS sap_action_audit_log (
            action_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            action_type TEXT NOT NULL,
            sap_table TEXT NOT NULL,
            sap_field TEXT NOT NULL,
            previous_value TEXT,
            new_value TEXT,
            reason TEXT,
            executed_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS carrier_debit_memos (
            memo_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            carrier_name TEXT NOT NULL,
            debit_amount_usd REAL NOT NULL,
            penalty_reason TEXT NOT NULL,
            created_at TEXT NOT NULL,
            status TEXT DEFAULT 'POSTED_TO_AP_LEDGER'
        );

        CREATE TABLE IF NOT EXISTS clinic_early_warnings (
            notice_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            clinic_name TEXT NOT NULL,
            destination_city TEXT NOT NULL,
            predicted_eta TEXT NOT NULL,
            delay_reason TEXT NOT NULL,
            force_majeure_compliant INTEGER DEFAULT 1,
            sent_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS schema_migrations (
            migration_id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL,
            applied_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_wr_city_date ON weather_readings(city_name, date_only);
        CREATE INDEX IF NOT EXISTS idx_wr_date      ON weather_readings(date_only);
        CREATE INDEX IF NOT EXISTS idx_sn_date      ON strike_news(published_date);
        CREATE INDEX IF NOT EXISTS idx_sn_city      ON strike_news(city_mentioned);
        CREATE INDEX IF NOT EXISTS idx_ds_date      ON daily_summaries(summary_date);
        CREATE INDEX IF NOT EXISTS idx_rag_news     ON rag_analyses(news_id);
        CREATE INDEX IF NOT EXISTS idx_sap_audit_order ON sap_action_audit_log(order_id);
        CREATE INDEX IF NOT EXISTS idx_carrier_memo_order ON carrier_debit_memos(order_id);
        CREATE INDEX IF NOT EXISTS idx_clinic_warn_order ON clinic_early_warnings(order_id);
        """
        with self.connection() as conn:
            conn.executescript(schema)
        self.logger.info("Schema ready")

    def _apply_migrations(self):
        """Standardized, non-destructive schema migrations tracked in schema_migrations table"""
        migrations = [
            ("v1.1_action_indexes", "Add B-tree indexes for SAP action and clinic audit tables", [
                "CREATE INDEX IF NOT EXISTS idx_sap_audit_order ON sap_action_audit_log(order_id);",
                "CREATE INDEX IF NOT EXISTS idx_carrier_memo_order ON carrier_debit_memos(order_id);",
                "CREATE INDEX IF NOT EXISTS idx_clinic_warn_order ON clinic_early_warnings(order_id);"
            ]),
        ]

        with self.connection() as conn:
            for version, desc, sql_list in migrations:
                applied = conn.execute("SELECT 1 FROM schema_migrations WHERE version = ?", (version,)).fetchone()
                if not applied:
                    for stmt in sql_list:
                        try:
                            conn.execute(stmt)
                        except Exception as e:
                            self.logger.warning(f"Migration {version} statement note: {e}")
                    conn.execute(
                        "INSERT INTO schema_migrations (version, description, applied_at) VALUES (?, ?, ?)",
                        (version, desc, datetime.now().isoformat())
                    )
                    self.logger.info(f"Applied database migration: {version} - {desc}")

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

    # ── Phase 5 Action Execution & Audit Repository ────────

    def record_sap_action(
        self,
        order_id: str,
        action_type: str,
        sap_table: str,
        sap_field: str,
        previous_value: str,
        new_value: str,
        reason: str,
        executed_at: str = None
    ) -> int:
        """Centralized write-back for SAP ERP action audit trails"""
        ts = executed_at or datetime.now().isoformat()
        with self.connection() as conn:
            cur = conn.execute("""
                INSERT INTO sap_action_audit_log (
                    order_id, action_type, sap_table, sap_field, previous_value, new_value, reason, executed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (str(order_id), action_type, sap_table, sap_field, previous_value, new_value, reason, ts))
            return cur.lastrowid

    def record_carrier_debit_memo(
        self,
        order_id: str,
        carrier_name: str,
        debit_amount_usd: float,
        penalty_reason: str,
        created_at: str = None,
        status: str = "POSTED_TO_AP_LEDGER"
    ) -> int:
        """Centralized write-back for carrier accounts-payable debit memos"""
        ts = created_at or datetime.now().isoformat()
        with self.connection() as conn:
            cur = conn.execute("""
                INSERT INTO carrier_debit_memos (
                    order_id, carrier_name, debit_amount_usd, penalty_reason, created_at, status
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (str(order_id), carrier_name, float(debit_amount_usd), penalty_reason, ts, status))
            return cur.lastrowid

    def record_clinic_notice(
        self,
        order_id: str,
        clinic_name: str,
        destination_city: str,
        predicted_eta: str,
        delay_reason: str,
        force_majeure_compliant: bool = True,
        sent_at: str = None
    ) -> int:
        """Centralized write-back for 12-hour proactive clinic early warnings"""
        ts = sent_at or datetime.now().isoformat()
        with self.connection() as conn:
            cur = conn.execute("""
                INSERT INTO clinic_early_warnings (
                    order_id, clinic_name, destination_city, predicted_eta, delay_reason, force_majeure_compliant, sent_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (str(order_id), clinic_name, destination_city, predicted_eta, delay_reason, 1 if force_majeure_compliant else 0, ts))
            return cur.lastrowid

    def get_sap_audit_log(self, order_id: str) -> List[Dict[str, Any]]:
        """Retrieve audit log of executed actions for a specific order"""
        with self.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM sap_action_audit_log WHERE order_id = ? ORDER BY executed_at DESC",
                (str(order_id),)
            ).fetchall()
            return [dict(r) for r in rows]

    def get_clinic_notices(self, order_id: str = None) -> List[Dict[str, Any]]:
        """Retrieve clinic early warning notifications"""
        with self.connection() as conn:
            if order_id:
                rows = conn.execute(
                    "SELECT * FROM clinic_early_warnings WHERE order_id = ? ORDER BY sent_at DESC",
                    (str(order_id),)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM clinic_early_warnings ORDER BY sent_at DESC"
                ).fetchall()
            return [dict(r) for r in rows]