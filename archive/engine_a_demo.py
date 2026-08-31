#!/usr/bin/env python3
"""
Engine A (Predictive ML) & Dual-Engine Demo

Designed to run seamlessly on Databricks Notebooks and Standalone CLI.
Databricks Workspace Path: /Workspace/Users/ayyash.a@tcs.com/O2C_AI

Usage (Databricks Notebook):
    # Run cell directly:
    from engine_a_demo import run_demo
    run_demo()

Usage (CLI / Shell):
    python engine_a_demo.py
    python engine_a_demo.py --train
    python engine_a_demo.py --order 800000000000001
    python engine_a_demo.py --limit 10
    python engine_a_demo.py --rebuild-db
"""

import sys
import os
import argparse
from pathlib import Path
import pandas as pd

# UTF-8 console output for Windows / Linux
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

# ── Databricks Workspace Path Support ─────────────────────────
DATABRICKS_PATH = Path("/Workspace/Users/ayyash.a@tcs.com/O2C_AI")
if DATABRICKS_PATH.exists() or "DATABRICKS_RUNTIME_VERSION" in os.environ:
    BASE_DIR = DATABRICKS_PATH
else:
    try:
        BASE_DIR = Path(__file__).resolve().parent
    except NameError:
        BASE_DIR = DATABRICKS_PATH

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Import modules
from modules.config import DB_PATH, DOCS_DIR
from modules.ml_db_extension import MLDatabaseExtension
from modules.predictive_engine import PredictiveEngine
from modules.weather_service import WeatherService
from modules.rag_engine import RAGEngine

# Helper for Databricks display()
def show_table(df):
    """Render table via Databricks display() if available, otherwise print"""
    if 'display' in globals() or 'display' in __builtins__:
        try:
            display(df)
            return
        except Exception:
            pass
    print(df.to_string())


def run_demo(train_models: bool = True, order_id: str = None, limit: int = 5, rebuild_db: bool = False):
    print("=" * 80)
    print("🚀 O2C AI MONITOR - DUAL ENGINE (ENGINE A + ENGINE B) DEMO")
    print(f"📍 Project Base: {BASE_DIR}")
    print("=" * 80)

    # 1. Initialize ML Database
    db_path = BASE_DIR / "india_monitor_data" / "database" / "india_monitor.db"
    ml_db = MLDatabaseExtension(db_path)
    input_dir = BASE_DIR / "Input Files"

    # 2. Ingest SAP tables from Input Files
    print(f"\n📂 Ingesting SAP table data from: {input_dir}")
    stats = ml_db.load_sap_data_from_csv(input_dir)
    print(f"✅ Ingested {len(stats)} SAP tables into SQLite database")

    # 3. Generate ML Features
    print("\n⚙️  Engineering ML Features from joined tables...")
    df = ml_db.get_ml_ready_dataset()
    print(f"✅ ML-Ready Dataset prepared: {len(df):,} rows, {len(df.columns)} columns")

    # 4. Optional RAG Engine initialization (Engine B)
    rag = None
    try:
        rag = RAGEngine()
        if rag.initialize(force_rebuild=False):
            print("✅ Engine B (RAG Knowledge Base) connected")
        else:
            print("⚠️  Engine B (RAG) index unavailable, running Engine A standalone")
            rag = None
    except Exception as e:
        print(f"ℹ️  Engine B (RAG) bypassed ({e})")
        rag = None

    # 5. Initialize Engine A
    engine_a = PredictiveEngine(
        ml_db_extension=ml_db,
        rag_engine=rag,
        weather_service=None
    )

    # 6. Train Models if requested or default
    if train_models or len(df) > 0:
        print("\n🤖 Training Predictive Machine Learning Models (RandomForest + GradientBoosting)...")
        trained = engine_a.train_models(df, train_size=0.8)
        if trained:
            print("   Features by Importance:")
            top_feats = sorted(engine_a.feature_importances.items(), key=lambda x: x[1], reverse=True)[:5]
            for feat, imp in top_feats:
                print(f"     • {feat:<28}: {imp:.1%}")

    # 7. Single Order Prediction or Batch Predictions
    if order_id:
        print(f"\n📦 PREDICTING SINGLE ORDER: {order_id}")
        print("-" * 80)
        pred = engine_a.predict_delivery_delay(order_id)
        if "error" in pred:
            print(f"❌ {pred['error']}")
        else:
            _print_prediction_card(pred)
    else:
        print(f"\n📦 RUNNING BATCH PREDICTIONS (Limit: {limit} orders)")
        print("-" * 80)
        predictions = engine_a.predict_all_active_orders(limit=limit)
        
        for idx, pred in enumerate(predictions, 1):
            print(f"\n[{idx}/{len(predictions)}] ORDER #{pred['order_id']}")
            _print_prediction_card(pred)

        # Summary KPIs
        summary = engine_a.get_summary_stats(predictions)
        print("\n" + "=" * 80)
        print("📊 AGGREGATE LOGISTICS RISK SUMMARY")
        print("=" * 80)
        print(f"  • Total Orders Analyzed   : {summary['total_orders']}")
        print(f"  • Predicted Delays        : {summary['predicted_delays']} ({summary['delay_rate']:.1%})")
        print(f"  • Avg Delay Duration      : {summary['avg_delay_hours']:.1f} hours")
        print(f"  • Total Financial Risk    : ${summary['total_financial_risk_usd']:,.2f}")
        print(f"  • High Risk Orders (>$500): {summary['high_risk_orders']}")

    ml_db.close()
    print("\n" + "=" * 80)
    print("✅ DEMO EXECUTION COMPLETE")
    print("=" * 80)


def _print_prediction_card(pred: dict):
    delay_status = "❌ DELAYED" if pred['will_be_delayed'] else "✅ ON TIME"
    print(f"   Customer   : {pred['customer_name']} (Tier: {pred['customer_tier']})")
    print(f"   Carrier    : {pred['carrier_name']} | Mode: {pred['shipping_type']}")
    print(f"   Status     : {delay_status} (Prob: {pred['delay_probability']:.1%}) | Delay: {pred['delay_hours']:.1f} hrs")
    print(f"   Target ETA : {pred['predicted_eta']}")
    print(f"   Root Cause : {pred['root_cause']}")
    print(f"   Risk ($)   : ${pred['financial_risk_usd']:,.2f} (Order Val: ${pred['order_value_usd']:,.2f})")
    
    if pred.get('applied_clauses'):
        print(f"   Clauses    :")
        for cl in pred['applied_clauses']:
            print(f"     • {cl}")
            
    if pred.get('rag_sources'):
        print(f"   RAG Policy : {', '.join(pred['rag_sources'])}")


def main():
    is_databricks = hasattr(sys, 'ps1') or 'DATABRICKS_RUNTIME_VERSION' in os.environ
    if is_databricks or len(sys.argv) == 1:
        run_demo(train_models=True, order_id=None, limit=5, rebuild_db=False)
    else:
        parser = argparse.ArgumentParser(description="Engine A (Predictive ML) Demo")
        parser.add_argument("--train", action="store_true", default=True, help="Train ML models")
        parser.add_argument("--order", type=str, default=None, help="Specific Order ID to predict")
        parser.add_argument("--limit", type=int, default=5, help="Number of orders to evaluate")
        parser.add_argument("--rebuild-db", action="store_true", help="Force reload SAP CSV data")
        args = parser.parse_args()

        run_demo(
            train_models=args.train,
            order_id=args.order,
            limit=args.limit,
            rebuild_db=args.rebuild_db
        )


if __name__ == "__main__":
    main()
