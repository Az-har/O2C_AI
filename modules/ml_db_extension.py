"""ML Database Extension for O2C AI Monitor

Handles:
- Ingestion of 10 SAP tables (VBAK, VBAP, LIKP, LIPS, VTTK, VTTP, KNA1, KNVV, LFA1, MARA)
- Relational joins across logistics, sales, materials, customers, and carriers
- Feature engineering for delivery delay machine learning
- Unified ML-ready dataset preparation and query APIs
"""

import os
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np

try:
    from .config import DB_PATH, BASE_DIR
except ImportError:
    from config import DB_PATH, BASE_DIR


class MLDatabaseExtension:
    """
    Manages SAP data ingestion, relational schema creation,
    feature engineering, and retrieval for Engine A (Predictive ML).
    """

    TABLES = [
        "vbak", "vbap", "likp", "lips",
        "vttk", "vttp", "kna1", "knvv",
        "lfa1", "mara"
    ]

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            self.db_path = Path(db_path or (BASE_DIR / "database" / "india_monitor.db"))
        else:
            self.db_path = Path(db_path)
        
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        try:
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.execute("PRAGMA synchronous=NORMAL;")
        except Exception:
            pass
        self._cached_ml_df = None
        self._order_lookup_dict = {}
        self._build_sap_schema()

    def _build_sap_schema(self):
        """Create normalized relational tables for SAP ERP data"""
        cursor = self.conn.cursor()
        
        schema = """
        -- 1. Sales Order Header
        CREATE TABLE IF NOT EXISTS sap_vbak (
            vbeln TEXT PRIMARY KEY,
            kunnr TEXT,
            erdat TEXT,
            ernam TEXT,
            vdatu TEXT,
            auart TEXT,
            netwr REAL,
            waerk TEXT
        );

        -- 2. Sales Order Item
        CREATE TABLE IF NOT EXISTS sap_vbap (
            vbeln TEXT,
            posnr TEXT,
            matnr TEXT,
            werks TEXT,
            kwmeng REAL,
            netpr REAL,
            waerk TEXT,
            PRIMARY KEY (vbeln, posnr)
        );

        -- 3. Delivery Header
        CREATE TABLE IF NOT EXISTS sap_likp (
            vbeln TEXT PRIMARY KEY,
            kunnr TEXT,
            vstel TEXT,
            lfzin TEXT,
            wadat TEXT,
            erdat TEXT
        );

        -- 4. Delivery Item
        CREATE TABLE IF NOT EXISTS sap_lips (
            vbeln TEXT,
            posnr TEXT,
            vgbel TEXT,
            werks TEXT,
            brgew REAL,
            vrkme TEXT,
            PRIMARY KEY (vbeln, posnr)
        );

        -- 5. Shipment Header
        CREATE TABLE IF NOT EXISTS sap_vttk (
            tknum TEXT PRIMARY KEY,
            lifnr TEXT,
            tplst TEXT,
            vsart TEXT,
            dpabf TEXT,
            status TEXT,
            erdat TEXT
        );

        -- 6. Shipment Item (Bridge)
        CREATE TABLE IF NOT EXISTS sap_vttp (
            tknum TEXT,
            tpnum TEXT,
            vbeln TEXT,
            PRIMARY KEY (tknum, tpnum, vbeln)
        );

        -- 7. Customer Master General
        CREATE TABLE IF NOT EXISTS sap_kna1 (
            kunnr TEXT PRIMARY KEY,
            name1 TEXT,
            ort01 TEXT,
            regio TEXT,
            land1 TEXT,
            pstlz TEXT
        );

        -- 8. Customer Master Sales
        CREATE TABLE IF NOT EXISTS sap_knvv (
            kunnr TEXT PRIMARY KEY,
            vkorg TEXT,
            vtweg TEXT,
            customer_tier TEXT,
            close_time TEXT
        );

        -- 9. Vendor / Carrier Master
        CREATE TABLE IF NOT EXISTS sap_lfa1 (
            lifnr TEXT PRIMARY KEY,
            name1 TEXT,
            ort01 TEXT,
            land1 TEXT,
            telf1 TEXT
        );

        -- 10. Material Master
        CREATE TABLE IF NOT EXISTS sap_mara (
            matnr TEXT PRIMARY KEY,
            maktx TEXT,
            matkl TEXT,
            meins TEXT,
            specialty_diet_flag TEXT,
            shelf_life_mos INTEGER
        );

        -- Predictions Table
        CREATE TABLE IF NOT EXISTS ml_predictions (
            prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            delivery_id TEXT,
            shipment_id TEXT,
            customer_name TEXT,
            carrier_name TEXT,
            predicted_eta TEXT,
            delay_probability REAL,
            delay_hours REAL,
            will_be_delayed INTEGER,
            root_cause TEXT,
            financial_risk_usd REAL,
            predicted_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_vbak_kunnr ON sap_vbak(kunnr);
        CREATE INDEX IF NOT EXISTS idx_lips_vgbel ON sap_lips(vgbel);
        CREATE INDEX IF NOT EXISTS idx_lips_vbeln ON sap_lips(vbeln);
        CREATE INDEX IF NOT EXISTS idx_vttp_vbeln ON sap_vttp(vbeln);
        CREATE INDEX IF NOT EXISTS idx_vttp_tknum ON sap_vttp(tknum);
        CREATE INDEX IF NOT EXISTS idx_vttk_lifnr ON sap_vttk(lifnr);
        CREATE INDEX IF NOT EXISTS idx_vbap_vbeln ON sap_vbap(vbeln);
        CREATE INDEX IF NOT EXISTS idx_vbap_matnr ON sap_vbap(matnr);
        """
        cursor.executescript(schema)
        self.conn.commit()

    def load_sap_data_from_csv(self, input_dir: Path) -> Dict[str, int]:
        """
        Load all 10 SAP CSV files into SQLite database.
        Returns dict with row counts per table.
        """
        input_path = Path(input_dir)
        stats = {}
        
        table_file_map = {
            "sap_vbak": "VBAK.csv",
            "sap_vbap": "VBAP.csv",
            "sap_likp": "LIKP.csv",
            "sap_lips": "LIPS.csv",
            "sap_vttk": "VTTK.csv",
            "sap_vttp": "VTTP.csv",
            "sap_kna1": "KNA1.csv",
            "sap_knvv": "KNVV.csv",
            "sap_lfa1": "LFA1.csv",
            "sap_mara": "MARA.csv"
        }

        for table_name, csv_name in table_file_map.items():
            csv_path = input_path / csv_name
            if not csv_path.exists():
                matched = [p for p in input_path.glob("*.csv") if p.name.lower() == csv_name.lower()]
                if matched:
                    csv_path = matched[0]
                else:
                    stats[table_name] = 0
                    continue

            df = pd.read_csv(csv_path)
            df.columns = [c.strip().lower() for c in df.columns]
            
            for col in df.columns:
                if df[col].dtype == object:
                    df[col] = df[col].astype(str).str.strip()

            df.to_sql(table_name, self.conn, if_exists="replace", index=False)
            stats[table_name] = len(df)

        self.conn.commit()
        self._cached_ml_df = None
        self._order_lookup_dict = {}
        return stats

    def get_ml_ready_dataset(self, force_refresh: bool = False) -> pd.DataFrame:
        """
        Execute full relational join across all SAP tables and apply
        feature engineering for Engine A ML models.
        Results are cached in-memory for sub-millisecond lookups.
        """
        if self._cached_ml_df is not None and not force_refresh:
            return self._cached_ml_df
        sql = """
        SELECT 
            vbak.vbeln AS order_id,
            vbak.erdat AS order_date,
            vbak.vdatu AS requested_delivery_date,
            vbak.auart AS order_type,
            vbak.netwr AS order_value,
            vbak.waerk AS currency,
            
            kna1.kunnr AS customer_id,
            COALESCE(kna1.name1, 'Unknown Customer') AS customer_name,
            kna1.ort01 AS dest_city,
            kna1.regio AS dest_region,
            kna1.pstlz AS dest_zip,
            COALESCE(knvv.customer_tier, 'Independent') AS customer_tier,
            COALESCE(knvv.close_time, '17:00') AS close_time,
            
            likp.vbeln AS delivery_id,
            likp.wadat AS planned_goods_issue_date,
            likp.vstel AS shipping_point,
            
            vttk.tknum AS shipment_id,
            vttk.dpabf AS planned_departure,
            vttk.status AS shipment_status,
            COALESCE(vttk.vsart, 'Road (FTL)') AS shipping_type,
            COALESCE(lfa1.name1, 'Unknown Carrier') AS carrier_name,
            lfa1.lifnr AS carrier_id,
            
            -- Aggregations from items
            COALESCE(agg_vbap.total_quantity, 1.0) AS total_quantity,
            COALESCE(agg_vbap.item_count, 1) AS item_count,
            COALESCE(agg_vbap.has_specialty_diet, 0) AS has_specialty_diet,
            COALESCE(agg_vbap.min_shelf_life, 12) AS min_shelf_life,
            COALESCE(agg_lips.total_weight, 500.0) AS total_weight
            
        FROM sap_vbak vbak
        LEFT JOIN sap_kna1 kna1 ON vbak.kunnr = kna1.kunnr
        LEFT JOIN sap_knvv knvv ON vbak.kunnr = knvv.kunnr
        LEFT JOIN (
            SELECT 
                vgbel AS order_id, 
                vbeln AS delivery_id,
                SUM(brgew) AS total_weight
            FROM sap_lips
            GROUP BY vgbel
        ) agg_lips ON vbak.vbeln = agg_lips.order_id
        LEFT JOIN sap_likp likp ON agg_lips.delivery_id = likp.vbeln
        LEFT JOIN sap_vttp vttp ON likp.vbeln = vttp.vbeln
        LEFT JOIN sap_vttk vttk ON vttp.tknum = vttk.tknum
        LEFT JOIN sap_lfa1 lfa1 ON vttk.lifnr = lfa1.lifnr
        LEFT JOIN (
            SELECT 
                vbap.vbeln,
                COUNT(vbap.posnr) AS item_count,
                SUM(vbap.kwmeng) AS total_quantity,
                MAX(CASE WHEN UPPER(mara.specialty_diet_flag) IN ('TRUE', '1', 'YES') THEN 1 ELSE 0 END) AS has_specialty_diet,
                MIN(COALESCE(mara.shelf_life_mos, 12)) AS min_shelf_life
            FROM sap_vbap vbap
            LEFT JOIN sap_mara mara ON vbap.matnr = mara.matnr
            GROUP BY vbap.vbeln
        ) agg_vbap ON vbak.vbeln = agg_vbap.vbeln
        """
        
        df = pd.read_sql_query(sql, self.conn)
        if df.empty:
            return df

        # --- Feature Engineering ---
        now = datetime.now()
        
        order_dates = pd.to_datetime(df['order_date'], errors='coerce')
        rdd_dates = pd.to_datetime(df['requested_delivery_date'], errors='coerce')
        dep_dates = pd.to_datetime(df['planned_departure'], errors='coerce')

        df['order_to_delivery_days'] = (rdd_dates - order_dates).dt.total_seconds() / (24 * 3600)
        df['order_to_departure_days'] = (dep_dates - order_dates).dt.total_seconds() / (24 * 3600)
        df['days_since_order'] = (now - order_dates).dt.total_seconds() / (24 * 3600)
        df['days_until_delivery'] = (rdd_dates - now).dt.total_seconds() / (24 * 3600)

        df['order_to_delivery_days'] = df['order_to_delivery_days'].fillna(4.0).clip(lower=0.5, upper=60.0)
        df['order_to_departure_days'] = df['order_to_departure_days'].fillna(1.0).clip(lower=0.1, upper=30.0)
        df['days_since_order'] = df['days_since_order'].fillna(2.0).clip(lower=0.0)
        df['days_until_delivery'] = df['days_until_delivery'].fillna(2.0)

        df['total_weight'] = df['total_weight'].fillna(500.0)
        df['total_quantity'] = df['total_quantity'].fillna(10.0)
        df['weight_per_unit'] = (df['total_weight'] / np.maximum(df['total_quantity'], 1.0)).fillna(50.0)
        df['is_heavy_shipment'] = (df['total_weight'] > 1000.0).astype(int)

        # --- Geospatial & Route Modeling ---
        city_coords = {
            "mumbai": (19.0760, 72.8777),
            "delhi": (28.6139, 77.2090),
            "bangalore": (12.9716, 77.5946),
            "chennai": (13.0827, 80.2707),
            "kolkata": (22.5726, 88.3639),
            "hyderabad": (17.3850, 78.4867),
            "pune": (18.5204, 73.8567),
            "ahmedabad": (23.0225, 72.5714),
            "jaipur": (26.9124, 75.7873),
            "lucknow": (26.8467, 80.9462),
            "austin": (30.2672, -97.7431),
            "dallas": (32.7767, -96.7970),
            "houston": (29.7604, -95.3698),
            "chicago": (41.8781, -87.6298),
            "atlanta": (33.7490, -84.3880)
        }

        # Origin hub default based on shipping point or major depot
        origin_lat = 19.0760  # Default Mumbai central DC
        origin_lon = 72.8777

        def calc_haversine(city_name: str) -> float:
            c_clean = str(city_name).lower().strip()
            if c_clean in city_coords:
                lat2, lon2 = city_coords[c_clean]
            else:
                # Deterministic synthetic distance based on hash for unmapped cities
                return float(350.0 + (abs(hash(c_clean)) % 900))
            
            import math
            R = 6371.0  # Earth radius in km
            dlat = math.radians(lat2 - origin_lat)
            dlon = math.radians(lon2 - origin_lon)
            a = (math.sin(dlat / 2.0) ** 2 +
                 math.cos(math.radians(origin_lat)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2)
            c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
            return float(R * c)

        df['haversine_distance_km'] = df['dest_city'].apply(calc_haversine)
        df['required_transit_speed_kmh'] = np.round(
            df['haversine_distance_km'] / np.maximum(1.0, df['order_to_delivery_days'] * 24.0), 1
        )
        df['is_unrealistic_speed'] = (df['required_transit_speed_kmh'] > 55.0).astype(int)

        # --- Calendar & Operational Congestion Signals ---
        df['order_day_of_week'] = order_dates.dt.dayofweek.fillna(2).astype(int)
        df['is_weekend_order'] = (df['order_day_of_week'] >= 4).astype(int)  # Fri/Sat/Sun order
        df['is_month_end'] = (order_dates.dt.day.fillna(15) >= 26).astype(int)  # Month-end shipping surge

        tier_map = {"platinum": 3, "gold": 2, "independent": 2, "silver": 1, "standard": 1}
        df['customer_tier_code'] = df['customer_tier'].str.lower().map(lambda x: tier_map.get(x, 1))

        type_map = {
            "road (ftl)": 1, "ftl": 1, "road (ltl)": 2, "ltl": 2,
            "air": 0, "rail": 1, "intermodal": 1, "rush": 3
        }
        df['shipping_risk_code'] = df['shipping_type'].str.lower().map(lambda x: type_map.get(x, 1))

        status_map = {"delayed": 2, "in transit": 1, "planned": 0, "completed": 0}
        df['status_code'] = df['shipment_status'].astype(str).str.lower().map(lambda x: status_map.get(x, 0))

        status_delayed = df['shipment_status'].astype(str).str.lower() == 'delayed'
        rush_tight = (df['order_type'].astype(str).str.upper() == 'RUSH') & (df['order_to_delivery_days'] < 2.5)
        heavy_ltl = (df['is_heavy_shipment'] == 1) & (df['shipping_risk_code'] == 2)
        
        delay_prob_heuristic = (
            status_delayed.astype(float) * 0.50 +
            heavy_ltl.astype(float) * 0.20 +
            rush_tight.astype(float) * 0.15 +
            df['is_unrealistic_speed'].astype(float) * 0.15 +
            df['is_weekend_order'].astype(float) * 0.10 +
            df['is_month_end'].astype(float) * 0.08 +
            (df['customer_tier_code'] == 3).astype(float) * 0.05
        ).clip(0.0, 0.98)

        df['is_delayed'] = (delay_prob_heuristic > 0.40).astype(int)
        
        np.random.seed(42)
        base_delay_hours = np.where(
            df['is_delayed'] == 1,
            24.0 + delay_prob_heuristic * 48.0 + (df['total_weight'] / 500.0) + (df['haversine_distance_km'] / 100.0),
            np.maximum(0.0, np.random.normal(1.5, 1.0, len(df)))
        )
        df['delay_hours'] = np.round(base_delay_hours, 1)
        df['order_value_usd'] = df['order_value'].fillna(2500.0)

        # Cache dataset and pre-index dictionary for O(1) instantaneous lookups
        self._cached_ml_df = df
        try:
            self._order_lookup_dict = {str(row['order_id']): row for row in df.to_dict(orient='records')}
        except Exception:
            self._order_lookup_dict = {}

        return df

    def get_order_details(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve full joined record for a specific sales order in O(1) time"""
        if not self._order_lookup_dict:
            self.get_ml_ready_dataset()

        ord_key = str(order_id).strip()
        if ord_key in self._order_lookup_dict:
            return self._order_lookup_dict[ord_key]

        # Suffix matching fallback if short ID passed
        for k, v in self._order_lookup_dict.items():
            if k.endswith(ord_key):
                return v

        return None

    def record_prediction(self, prediction: Dict[str, Any]) -> int:
        """Store an Engine A prediction in ml_predictions table"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO ml_predictions (
                order_id, delivery_id, shipment_id, customer_name, carrier_name,
                predicted_eta, delay_probability, delay_hours, will_be_delayed,
                root_cause, financial_risk_usd, predicted_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(prediction.get("order_id")),
            str(prediction.get("delivery_id", "")),
            str(prediction.get("shipment_id", "")),
            str(prediction.get("customer_name", "")),
            str(prediction.get("carrier_name", "")),
            str(prediction.get("predicted_eta", "")),
            float(prediction.get("delay_probability", 0.0)),
            float(prediction.get("delay_hours", 0.0)),
            1 if prediction.get("will_be_delayed") else 0,
            str(prediction.get("root_cause", "")),
            float(prediction.get("financial_risk_usd", 0.0)),
            datetime.now().isoformat()
        ))
        self.conn.commit()
        return cursor.lastrowid

    def record_predictions_batch(self, predictions: List[Dict[str, Any]]) -> int:
        """Store multiple Engine A predictions in a single high-performance SQLite transaction"""
        if not predictions:
            return 0
        cursor = self.conn.cursor()
        now_str = datetime.now().isoformat()
        rows = [
            (
                str(p.get("order_id")),
                str(p.get("delivery_id", "")),
                str(p.get("shipment_id", "")),
                str(p.get("customer_name", "")),
                str(p.get("carrier_name", "")),
                str(p.get("predicted_eta", "")),
                float(p.get("delay_probability", 0.0)),
                float(p.get("delay_hours", 0.0)),
                1 if p.get("will_be_delayed") else 0,
                str(p.get("root_cause", "")),
                float(p.get("financial_risk_usd", 0.0)),
                now_str
            )
            for p in predictions
        ]
        cursor.executemany("""
            INSERT INTO ml_predictions (
                order_id, delivery_id, shipment_id, customer_name, carrier_name,
                predicted_eta, delay_probability, delay_hours, will_be_delayed,
                root_cause, financial_risk_usd, predicted_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, rows)
        self.conn.commit()
        return len(rows)

    def get_predicted_order_ids(self) -> set:
        """Return a set of order_id strings that have already been predicted in ml_predictions"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT DISTINCT order_id FROM ml_predictions")
            rows = cursor.fetchall()
            return {str(r[0]) for r in rows if r[0]}
        except Exception:
            return set()

    def close(self):
        """Close SQLite database connection"""
        if self.conn:
            self.conn.close()
