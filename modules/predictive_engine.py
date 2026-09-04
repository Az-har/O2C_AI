"""Predictive Engine for O2C AI Monitor (Dual Engine: Engine A + Engine B)

Implements:
- Engine A (Predictive ML): Supervised ML models for delay probability and delay hours
- Feature importance analysis & rule-based fallback heuristics
- Root cause diagnosis (Weather hazards, LTL terminal dwell, Rush order timing)
- Financial risk & SLA penalty calculations based on Reference specifications
- Seamless integration with Engine B (RAG) for policy & contract retrieval
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd

from modules.config import BASE_DIR

try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, mean_absolute_error
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class PredictiveEngine:
    """
    Engine A + Engine B Orchestration Core.
    Combines machine learning delivery delay predictions with RAG business context.
    """

    FEATURE_COLS = [
        'order_to_delivery_days',
        'order_to_departure_days',
        'days_since_order',
        'days_until_delivery',
        'total_quantity',
        'total_weight',
        'weight_per_unit',
        'is_heavy_shipment',
        'has_specialty_diet',
        'min_shelf_life',
        'customer_tier_code',
        'shipping_risk_code',
        'status_code',
        'haversine_distance_km',
        'required_transit_speed_kmh',
        'is_unrealistic_speed',
        'order_day_of_week',
        'is_weekend_order',
        'is_month_end',
    ]

    def __init__(
        self,
        ml_db_extension=None,
        rag_engine=None,
        weather_service=None
    ):
        self.ml_db = ml_db_extension
        self.rag = rag_engine
        self.weather = weather_service
        
        self.clf_model = None
        self.reg_model = None
        self.is_trained = False
        self.feature_importances = {}
        self._weather_cache = {}
        self._strike_cache = []

    def _preload_environmental_caches(self):
        """Pre-load latest weather and strike alerts in memory to avoid per-order disk queries"""
        if self.ml_db is None:
            return
        try:
            conn = self.ml_db.conn
            # 1. Weather cache across all cities
            w_rows = conn.execute("""
                SELECT LOWER(city_name) as city, temperature, rain_1h, wind_speed, visibility_km, weather_description
                FROM weather_readings
                GROUP BY LOWER(city_name)
                ORDER BY recorded_at DESC
            """).fetchall()
            self._weather_cache = {r["city"]: dict(r) for r in w_rows}

            # 2. Strike cache
            s_rows = conn.execute("""
                SELECT LOWER(COALESCE(city_mentioned, '')) as city, title, strike_type
                FROM strike_news
                ORDER BY published_date DESC
                LIMIT 50
            """).fetchall()
            self._strike_cache = [dict(r) for r in s_rows]
        except Exception:
            pass

    def clear_environmental_caches(self):
        """Reset environmental caches to enforce pure statelessness (Critique 1.3)"""
        self._weather_cache.clear()
        self._strike_cache.clear()

    def get_city_weather(self, city_name: str, force_fresh_lookup: bool = False) -> Optional[Dict[str, Any]]:
        """Stateless / indexed query for latest city weather reading"""
        city_clean = city_name.lower().strip()
        if not force_fresh_lookup and city_clean in self._weather_cache:
            return self._weather_cache[city_clean]
        if self.ml_db is not None:
            try:
                conn = self.ml_db.conn
                w_row = conn.execute("""
                    SELECT temperature, rain_1h, wind_speed, visibility_km, weather_description
                    FROM weather_readings
                    WHERE LOWER(city_name) = ?
                    ORDER BY recorded_at DESC LIMIT 1
                """, (city_clean,)).fetchone()
                if w_row:
                    res = dict(w_row)
                    if not force_fresh_lookup:
                        self._weather_cache[city_clean] = res
                    return res
            except Exception:
                pass
        return None

    def save_models(self, model_dir: Path = None) -> bool:
        """Persist trained model artifacts for instant zero-latency loading"""
        import pickle
        if not self.is_trained or self.clf_model is None:
            return False
        
        target_dir = Path(model_dir) if model_dir else (BASE_DIR / "models")
        target_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(target_dir / "rf_classifier.pkl", "wb") as f:
                pickle.dump(self.clf_model, f)
            with open(target_dir / "gb_regressor.pkl", "wb") as f:
                pickle.dump(self.reg_model, f)
            with open(target_dir / "feature_importances.json", "w", encoding="utf-8") as f:
                json.dump(self.feature_importances, f, indent=2)
            return True
        except Exception as e:
            print(f"⚠️ Could not save models: {e}")
            return False

    def load_models(self, model_dir: Path = None) -> bool:
        """Load persisted model artifacts from disk"""
        import pickle
        target_dir = Path(model_dir) if model_dir else (BASE_DIR / "models")
        clf_file = target_dir / "rf_classifier.pkl"
        reg_file = target_dir / "gb_regressor.pkl"
        
        if not clf_file.exists() or not reg_file.exists():
            return False
        
        try:
            with open(clf_file, "rb") as f:
                self.clf_model = pickle.load(f)
            with open(reg_file, "rb") as f:
                self.reg_model = pickle.load(f)
            imp_file = target_dir / "feature_importances.json"
            if imp_file.exists():
                with open(imp_file, "r", encoding="utf-8") as f:
                    self.feature_importances = json.load(f)
            self.is_trained = True
            return True
        except Exception:
            return False

    def explain_prediction(self, order_data: Dict[str, Any], delay_prob: float) -> List[Dict[str, Any]]:
        """
        Explainable AI: Calculate feature attribution percentages
        quantifying why the model predicted a delivery delay.
        """
        attributions = []
        if not self.feature_importances:
            return attributions

        # Human-readable labels & positive risk conditions
        feature_labels = {
            "status_code": ("Shipment In-Transit / Delayed Status", lambda d: d.get("status_code", 0) > 0),
            "is_unrealistic_speed": (f"High Transit Velocity Demand ({order_data.get('required_transit_speed_kmh', 0):.1f} km/h)", lambda d: d.get("is_unrealistic_speed", 0) == 1),
            "is_weekend_order": ("Weekend Dispatch / Receiving Dock Closure", lambda d: d.get("is_weekend_order", 0) == 1),
            "is_month_end": ("Month-End Warehouse Surge Congestion", lambda d: d.get("is_month_end", 0) == 1),
            "is_heavy_shipment": (f"Heavy Pallet Weight ({order_data.get('total_weight', 0):.0f} kg)", lambda d: d.get("is_heavy_shipment", 0) == 1),
            "shipping_risk_code": ("LTL Multi-Stop Consolidation Dwell", lambda d: d.get("shipping_risk_code", 1) == 2),
            "order_to_delivery_days": (f"Tight SLA Turnaround ({order_data.get('order_to_delivery_days', 0):.1f} days)", lambda d: d.get("order_to_delivery_days", 4.0) < 2.5),
            "has_specialty_diet": ("Prescription Specialty Diet Fragility", lambda d: d.get("has_specialty_diet", 0) == 1),
            "haversine_distance_km": (f"Long-Haul Corridor ({order_data.get('haversine_distance_km', 0):.0f} km)", lambda d: d.get("haversine_distance_km", 0) > 800.0)
        }

        total_active_weight = 0.0
        active_features = []
        for feat_name, (label, cond_fn) in feature_labels.items():
            if cond_fn(order_data):
                imp = self.feature_importances.get(feat_name, 0.05)
                total_active_weight += imp
                active_features.append((label, imp))

        if total_active_weight > 0:
            for label, imp in sorted(active_features, key=lambda x: x[1], reverse=True)[:4]:
                contrib_pct = (imp / total_active_weight) * min(100.0, delay_prob * 100.0)
                attributions.append({
                    "factor": label,
                    "contribution_pct": round(contrib_pct, 1)
                })

        return attributions

    def train_models(self, df: pd.DataFrame, train_size: float = 0.8) -> bool:
        """
        Train classification model for delay probability and
        regression model for delay duration in hours.
        """
        if not SKLEARN_AVAILABLE:
            print("⚠️ scikit-learn is not installed. Using rule-based heuristics.")
            return False

        if df is None or len(df) < 5:
            print("⚠️ Insufficient data to train ML models (minimum 5 samples required).")
            return False

        # Prepare X and y
        valid_cols = [c for c in self.FEATURE_COLS if c in df.columns]
        X = df[valid_cols].fillna(0.0)
        y_cls = df['is_delayed'] if 'is_delayed' in df.columns else (df['status_code'] == 2).astype(int)
        y_reg = df['delay_hours'] if 'delay_hours' in df.columns else np.where(y_cls == 1, 36.0, 1.0)

        try:
            if len(df) >= 10:
                X_train, X_test, y_train_cls, y_test_cls, y_train_reg, y_test_reg = train_test_split(
                    X, y_cls, y_reg, train_size=train_size, random_state=42, stratify=y_cls
                )
            else:
                X_train, X_test = X, X
                y_train_cls, y_test_cls = y_cls, y_cls
                y_train_reg, y_test_reg = y_reg, y_reg

            # --- Stage 1: Classification Model (Full Population) ---
            self.clf_model = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
            self.clf_model.fit(X_train, y_train_cls)
            
            y_prob_test = self.clf_model.predict_proba(X_test)[:, 1]
            y_pred_cls = (y_prob_test >= 0.40).astype(int)
            acc = accuracy_score(y_test_cls, y_pred_cls)

            # --- Stage 2: Conditional Hurdle Regressor (Trained STRICTLY on Delayed Population) ---
            delayed_mask_train = (y_train_cls == 1)
            X_train_delayed = X_train[delayed_mask_train]
            y_train_reg_delayed = y_train_reg[delayed_mask_train]

            self.reg_model = GradientBoostingRegressor(
                loss='huber', n_estimators=100, max_depth=5, learning_rate=0.08, random_state=42
            )
            self.reg_model.fit(X_train_delayed, y_train_reg_delayed)

            # Two-Stage Gated Test Evaluation
            y_pred_reg_conditional = self.reg_model.predict(X_test)
            y_pred_reg_twostage = np.where(y_pred_cls == 1, np.maximum(12.0, y_pred_reg_conditional), 0.0)
            mae = mean_absolute_error(y_test_reg, y_pred_reg_twostage)

            # Feature importance mapping from Stage 1 Classifier
            importances = self.clf_model.feature_importances_
            self.feature_importances = {col: float(imp) for col, imp in zip(valid_cols, importances)}

            self.is_trained = True
            self.save_models()
            print(f"✅ Two-Stage Hurdle Models trained & persisted successfully! (Classifier Accuracy: {acc:.1%}, Two-Stage MAE: {mae:.1f} hrs)")
            return True
        except Exception as e:
            print(f"❌ Error during model training: {e}")
            return False

    def predict_delivery_delay(
        self,
        order_id: str,
        order_data: Optional[Dict[str, Any]] = None,
        precomputed_prob: Optional[float] = None,
        precomputed_delay_hours: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Execute prediction pipeline for a single order using Two-Stage Hurdle architecture:
        1. Query ERP features
        2. Stage 1: Predict Delay Probability (Engine A Classifier)
        3. Stage 2: Predict Delay Hours if gated as delayed (Engine A Conditional Regressor)
        4. Determine Root Cause & XAI feature attributions
        5. Calculate Financial Risk & Contractual SLA Penalties
        6. Retrieve SLA & Policy context via RAG (Engine B)
        """
        if order_data is None:
            if self.ml_db is None:
                raise ValueError("MLDatabaseExtension instance required for prediction.")
            order_data = self.ml_db.get_order_details(order_id)

        if not order_data:
            return {"error": f"Order ID {order_id} not found in SAP database."}

        # --- Engine A: Two-Stage Hurdle ML Prediction ---
        if precomputed_prob is not None:
            # Leverage batch vectorized predictions (Critique 3.2 optimization)
            delay_prob = float(precomputed_prob)
            will_delayed = bool(delay_prob >= 0.40)
            delay_hours = float(precomputed_delay_hours or 0.0) if will_delayed else 0.0
        elif self.is_trained and self.clf_model is not None and self.reg_model is not None:
            # Extract features as DataFrame with feature names to preserve schema
            feat_dict = {col: [float(order_data.get(col, 0.0))] for col in self.FEATURE_COLS}
            X_single = pd.DataFrame(feat_dict)
            delay_prob = float(self.clf_model.predict_proba(X_single)[0][1])
            will_delayed = bool(delay_prob >= 0.40)
            if will_delayed:
                raw_delay_hours = float(self.reg_model.predict(X_single)[0])
                delay_hours = float(np.maximum(12.0, round(raw_delay_hours, 1)))
            else:
                delay_hours = 0.0
        else:
            # Rule-based fallback
            status = str(order_data.get('shipment_status', '')).lower()
            is_heavy = order_data.get('is_heavy_shipment', 0) == 1
            is_rush = str(order_data.get('order_type', '')).upper() == 'RUSH'
            lead_days = float(order_data.get('order_to_delivery_days', 4.0))

            base_prob = 0.75 if status == 'delayed' else (0.45 if status == 'in transit' else 0.15)
            if is_rush and lead_days < 2.0:
                base_prob += 0.20
            if is_heavy and order_data.get('shipping_risk_code', 1) == 2:
                base_prob += 0.15
            
            delay_prob = min(0.98, max(0.02, base_prob))
            will_delayed = delay_prob >= 0.40
            delay_hours = (24.0 + delay_prob * 36.0) if will_delayed else 0.0

        # ETA Calculation
        now = datetime.now()
        rdd_str = str(order_data.get('requested_delivery_date', ''))
        try:
            rdd = datetime.strptime(rdd_str[:10], "%Y-%m-%d")
        except:
            rdd = now + timedelta(days=2)

        if will_delayed and delay_hours > 0:
            predicted_eta_dt = rdd + timedelta(hours=delay_hours)
        else:
            predicted_eta_dt = rdd
        predicted_eta = predicted_eta_dt.strftime("%Y-%m-%d %H:%M")

        # --- Root Cause Analysis ---
        root_causes = []
        dest_city_raw = order_data.get('dest_city')
        if dest_city_raw is None or (isinstance(dest_city_raw, float) and np.isnan(dest_city_raw)):
            dest_city = 'Unknown'
        else:
            dest_city = str(dest_city_raw).strip()
            if dest_city.lower() in ('nan', 'none', ''):
                dest_city = 'Unknown'

        shipping_type = str(order_data.get('shipping_type') or 'Road (FTL)')
        customer_tier = str(order_data.get('customer_tier') or 'Independent')
        if customer_tier.lower() in ('nan', 'none', ''):
            customer_tier = 'Independent'
        has_specialty = int(order_data.get('has_specialty_diet', 0) or 0) == 1
        order_val = float(order_data.get('order_value', 2500.0) or 2500.0)

        if str(order_data.get('shipment_status', '')).lower() == 'delayed':
            root_causes.append("Carrier route delay / in-transit bottleneck")
        if "LTL" in shipping_type:
            root_causes.append("LTL multi-stop terminal consolidation dwell")
        if order_data.get('is_heavy_shipment', 0) == 1:
            root_causes.append(f"Heavy pallet freight handling restriction ({order_data.get('total_weight', 0):.0f} kg)")
        if str(order_data.get('order_type', '')).upper() == 'RUSH':
            root_causes.append("Tight expedited turnaround window (<48h)")
        if order_data.get('is_unrealistic_speed', 0) == 1:
            root_causes.append(f"High transit velocity demand ({order_data.get('required_transit_speed_kmh', 0):.1f} km/h required over corridor)")
        if order_data.get('is_weekend_order', 0) == 1:
            root_causes.append("Weekend dispatch / receiving dock closure window")
        if order_data.get('is_month_end', 0) == 1:
            root_causes.append("Month-end shipping surge & warehouse dock congestion")
        
        # Check weather from in-memory cache (instant lookup) or fallback to DB
        weather_alert = None
        city_clean = dest_city.lower().strip()
        w_row = self._weather_cache.get(city_clean)
        if w_row is None and self.ml_db is not None:
            try:
                conn = self.ml_db.conn
                w_db = conn.execute("""
                    SELECT temperature, rain_1h, wind_speed, visibility_km, weather_description
                    FROM weather_readings
                    WHERE LOWER(city_name) = ?
                    ORDER BY recorded_at DESC LIMIT 1
                """, (city_clean,)).fetchone()
                if w_db:
                    w_row = dict(w_db)
                    self._weather_cache[city_clean] = w_row
            except Exception:
                pass

        if w_row:
            temp = float(w_row.get('temperature', 25.0) or 25.0)
            rain = float(w_row.get('rain_1h', 0.0) or 0.0)
            wind = float(w_row.get('wind_speed', 0.0) or 0.0)
            vis = float(w_row.get('visibility_km', 10.0) or 10.0)
            if temp > 40.0:
                root_causes.append(f"Thermal degradation risk ({temp:.1f}°C heatwave in {dest_city})")
                weather_alert = f"Extreme Heat ({temp:.1f}°C)"
            elif rain > 20.0:
                root_causes.append(f"Severe precipitation & moisture risk ({rain:.1f}mm/hr in {dest_city})")
                weather_alert = f"Heavy Rain ({rain:.1f}mm)"
            elif wind > 15.0:
                root_causes.append(f"High wind transport advisory ({wind:.1f}m/s in {dest_city})")
                weather_alert = f"High Wind ({wind:.1f}m/s)"
            elif vis < 1.0:
                root_causes.append(f"Low visibility fog hazard ({vis:.1f}km in {dest_city})")
                weather_alert = "Low Visibility Fog"

        # Check strikes & transport disruptions from in-memory cache or fallback
        strike_alert = None
        s_matched = next((s for s in self._strike_cache if s.get("city") == city_clean or city_clean in s.get("title", "").lower()), None)
        if s_matched:
            stype = s_matched.get('strike_type') or 'Transport'
            root_causes.append(f"Active transport disruption ({stype} strike in {dest_city})")
            strike_alert = f"{stype} Strike: {s_matched.get('title', '')[:60]}"
            if will_delayed:
                delay_hours += 12.0
                delay_prob = min(0.99, delay_prob + 0.10)

        if not root_causes:
            root_causes.append("Standard transit variability")
        root_cause_str = "; ".join(root_causes)

        # Feature Attribution Breakdown (Explainable AI)
        feature_attributions = self.explain_prediction(order_data, delay_prob)

        # --- Financial Risk & SLA Calculation (Reference Specs) ---
        # 1. Grace period: 24h allowed past PDD
        delay_days = max(0.0, (delay_hours - 24.0) / 24.0) if delay_hours > 24.0 else 0.0
        
        financial_risk = 0.0
        applied_clauses = []

        if will_delayed and delay_days > 0:
            if customer_tier.lower() == 'platinum':
                # Scenario 1: $500 flat per calendar day
                penalty = np.ceil(delay_days) * 500.0
                financial_risk += penalty
                applied_clauses.append(f"Platinum SLA: ${penalty:.2f} penalty ({np.ceil(delay_days):.0f} days @ $500/day)")
            else:
                # Scenario 2: 5% of invoice value per day, capped at 25%
                daily_rate = 0.05 * order_val
                penalty = min(0.25 * order_val, np.ceil(delay_days) * daily_rate)
                financial_risk += penalty
                applied_clauses.append(f"Independent/Gold SLA: ${penalty:.2f} penalty (5%/day capped at 25%)")

        # After-hours arrival check (Scenario 3)
        close_time_str = str(order_data.get('close_time', '17:00'))
        try:
            close_hour = int(close_time_str.split(':')[0])
            if predicted_eta_dt.hour >= close_hour:
                financial_risk += 150.0
                applied_clauses.append("Receiving Window Violation: $150.00 redelivery fee")
        except Exception:
            pass

        # Specialty diet emergency air freight authorization (>48h delay) (Scenario 6)
        if has_specialty and delay_hours > 48.0:
            applied_clauses.append("Specialty Diet Alert: Authorized $1,000 emergency replacement Air Freight")

        # Force Majeure evaluation (Scenario 9/10)
        force_majeure_applicable = False
        if weather_alert:
            force_majeure_applicable = True
            applied_clauses.append(f"Force Majeure Candidate: Act of God {weather_alert} detected")

        # --- Engine B: RAG Semantic Context Retrieval ---
        rag_context = None
        rag_sources = []
        if self.rag:
            try:
                # Normalized query pattern maximizes vector cache hit rate (sub-millisecond RAG)
                rag_query = f"Late delivery SLA penalty and Force Majeure waiver policy for {customer_tier} tier with {shipping_type}"
                rag_res = self.rag.ask(rag_query)
                rag_context = rag_res.get('answer')
                rag_sources = [s.get('filename') for s in rag_res.get('sources', [])[:3]]
            except Exception as e:
                rag_context = f"RAG query skipped: {e}"

        result_payload = {
            "order_id": str(order_id),
            "delivery_id": str(order_data.get("delivery_id", "")),
            "shipment_id": str(order_data.get("shipment_id", "")),
            "customer_name": str(order_data.get("customer_name", "Unknown")),
            "customer_tier": customer_tier,
            "carrier_name": str(order_data.get("carrier_name", "Unknown")),
            "dest_city": dest_city,
            "shipping_type": shipping_type,
            "order_value_usd": float(order_val),
            "has_specialty_diet": bool(has_specialty),
            "haversine_distance_km": float(order_data.get("haversine_distance_km", 0.0)),
            "required_transit_speed_kmh": float(order_data.get("required_transit_speed_kmh", 0.0)),
            
            # Predictive outputs
            "delay_probability": float(delay_prob),
            "will_be_delayed": bool(will_delayed),
            "delay_hours": float(delay_hours),
            "predicted_eta": predicted_eta,
            "root_cause": root_cause_str,
            "feature_attributions": feature_attributions,
            "financial_risk_usd": float(financial_risk),
            "applied_clauses": applied_clauses,
            "force_majeure_applicable": force_majeure_applicable,
            
            # Engine B RAG Output
            "rag_business_context": rag_context,
            "rag_sources": rag_sources,
            "predicted_at": datetime.now().isoformat()
        }

        return result_payload

    def predict_batch(
        self,
        order_ids: List[str],
        orders_data: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        High-performance vectorized batch prediction for Engine A & B.
        Vectorizes feature matrix extraction, scikit-learn model inference,
        and in-memory rule processing across thousands of orders in seconds.
        """
        if not order_ids:
            return []

        self._preload_environmental_caches()

        if orders_data is None:
            if self.ml_db is None:
                raise ValueError("MLDatabaseExtension instance required for batch prediction.")
            orders_data = [self.ml_db.get_order_details(oid) for oid in order_ids]

        valid_entries = [(oid, od) for oid, od in zip(order_ids, orders_data) if od is not None]
        if not valid_entries:
            return []

        v_order_ids, v_orders_data = zip(*valid_entries)

        # 1. Vectorized Feature Matrix Construction
        feat_rows = [{col: float(od.get(col, 0.0)) for col in self.FEATURE_COLS} for od in v_orders_data]
        X_batch = pd.DataFrame(feat_rows)

        # 2. Vectorized Model Inference
        if self.is_trained and self.clf_model is not None and self.reg_model is not None:
            delay_probs = self.clf_model.predict_proba(X_batch)[:, 1].tolist()
            raw_hrs = self.reg_model.predict(X_batch)
            delay_hours_arr = [float(np.maximum(12.0, round(h, 1))) if p >= 0.40 else 0.0 for p, h in zip(delay_probs, raw_hrs)]
        else:
            delay_probs = [0.15] * len(v_order_ids)
            delay_hours_arr = [0.0] * len(v_order_ids)

        # 3. Assemble full predictions leveraging precomputed vectorized batch inference (Critique 3.2)
        results = [
            self.predict_delivery_delay(
                ord_id,
                order_data=od,
                precomputed_prob=prob,
                precomputed_delay_hours=hrs
            )
            for ord_id, od, prob, hrs in zip(v_order_ids, v_orders_data, delay_probs, delay_hours_arr)
        ]

        return results

    def predict_all_active_orders(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Run delay predictions across all active SAP sales orders"""
        if self.ml_db is None:
            return []

        df = self.ml_db.get_ml_ready_dataset()
        if df.empty:
            return []

        order_ids = df['order_id'].unique().tolist()
        if limit:
            order_ids = order_ids[:limit]

        predictions = []
        for oid in order_ids:
            pred = self.predict_delivery_delay(oid)
            if "error" not in pred:
                predictions.append(pred)

        return predictions

    def get_summary_stats(self, predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute aggregate delivery risk KPIs across batch predictions"""
        if not predictions:
            return {
                "total_orders": 0,
                "predicted_delays": 0,
                "delay_rate": 0.0,
                "avg_delay_hours": 0.0,
                "total_financial_risk_usd": 0.0,
                "high_risk_orders": 0
            }

        total = len(predictions)
        delays = sum(1 for p in predictions if p.get('will_be_delayed'))
        delay_hours = [p.get('delay_hours', 0.0) for p in predictions]
        financial_risks = [p.get('financial_risk_usd', 0.0) for p in predictions]
        high_risk = sum(1 for r in financial_risks if r > 500.0)

        return {
            "total_orders": total,
            "predicted_delays": delays,
            "delay_rate": float(delays / max(total, 1)),
            "avg_delay_hours": float(np.mean(delay_hours)),
            "total_financial_risk_usd": float(np.sum(financial_risks)),
            "high_risk_orders": high_risk
        }
