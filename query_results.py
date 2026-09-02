"""
Query & Export Tool for O2C AI Monitor Stored Results
Allows querying SQLite database and Daily JSON Reports with Markdown/CSV export.
"""
import sqlite3
import json
import argparse
import sys
from pathlib import Path
from datetime import datetime

# Windows encoding safety
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Resolve project root dynamically
try:
    from modules.config import DB_PATH, PROJECT_ROOT
except Exception:
    PROJECT_ROOT = Path(__file__).parent
    DB_PATH = PROJECT_ROOT / "india_monitor_data" / "database" / "india_monitor.db"


def get_db_connection():
    if not DB_PATH.exists():
        print(f"❌ Database not found at: {DB_PATH}")
        print("💡 Run 'python main_pipeline.py' first to generate predictions.")
        sys.exit(1)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def show_summary():
    """Display overall executive metrics of stored predictions"""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM ml_predictions")
    total = c.fetchone()[0]
    
    if total == 0:
        print("ℹ️ No predictions stored in database yet.")
        conn.close()
        return

    c.execute("SELECT COUNT(*) FROM ml_predictions WHERE will_be_delayed = 1")
    delayed = c.fetchone()[0]
    ontime = total - delayed

    c.execute("SELECT AVG(delay_probability), AVG(delay_hours), SUM(financial_risk_usd) FROM ml_predictions")
    avg_prob, avg_hrs, total_risk = c.fetchone()

    c.execute("SELECT COUNT(*) FROM weather_readings")
    weather_count = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM strike_news")
    strike_count = c.fetchone()[0]

    print("\n" + "=" * 80)
    print("📊 O2C AI MONITOR - STORED PREDICTIONS SUMMARY")
    print("=" * 80)
    print(f"📦 Total Orders Predicted     : {total:,}")
    print(f"   • ❌ Delayed Orders        : {delayed:,} ({delayed/total:.1%})")
    print(f"   • ✅ On-Time Orders        : {ontime:,} ({ontime/total:.1%})")
    print(f"📈 Average Delay Probability  : {avg_prob:.1%}")
    print(f"⏱️  Average Predicted Delay    : {avg_hrs:.1f} hours")
    print(f"💰 Total Financial Risk ($)   : ${total_risk:,.2f}")
    print("-" * 80)
    print(f"🌤️  Weather Stream Records     : {weather_count:,}")
    print(f"📰 Disruption News Records    : {strike_count:,}")
    print("=" * 80 + "\n")
    conn.close()


def query_order(order_id: str):
    """Retrieve in-depth prediction and multi-agent analysis for a specific order ID"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM ml_predictions WHERE order_id = ? ORDER BY prediction_id DESC LIMIT 1", (str(order_id),))
    row = c.fetchone()
    conn.close()

    if not row:
        print(f"❌ Order '{order_id}' not found in database.")
        return

    # Check for in-depth decision analysis in daily reports
    report_decision = None
    reports_dir = PROJECT_ROOT / "india_monitor_data" / "reports"
    if reports_dir.exists():
        # Look through reports in reverse chronological order
        for rpath in sorted(reports_dir.glob("daily_agent_report_*.json"), reverse=True):
            try:
                with open(rpath, "r", encoding="utf-8") as rf:
                    rdata = json.load(rf)
                for d in rdata.get("decisions", []):
                    if str(d.get("order_id")) == str(order_id):
                        report_decision = d
                        break
                if report_decision:
                    break
            except Exception:
                continue

    print("\n" + "=" * 90)
    print(f"📦 IN-DEPTH ORDER ANALYSIS & ROOT CAUSE REPORT: {row['order_id']}")
    print("=" * 90)
    print(f"• Customer Name       : {row['customer_name']}")
    print(f"• Carrier Name        : {row['carrier_name']}")
    print(f"• Delivery ID         : {row['delivery_id']}")
    print(f"• Shipment ID         : {row['shipment_id']}")
    print(f"• Predicted Status    : {'❌ DELAYED' if row['will_be_delayed'] else '✅ ON TIME'}")
    print(f"• Delay Probability   : {row['delay_probability']:.1%}")
    print(f"• Predicted Delay     : {row['delay_hours']:.1f} hours")
    print(f"• Predicted ETA       : {row['predicted_eta']}")
    print(f"• Financial Risk ($)  : ${row['financial_risk_usd']:,.2f}")

    if report_decision:
        pred = report_decision.get("engine_a_ml_prediction", {})
        agents = report_decision.get("specialist_agents_analysis", {})
        contract = report_decision.get("legal_and_sla_adjudication", {})
        mitigation = report_decision.get("emergency_mitigation", {})
        sap_actions = report_decision.get("executed_enterprise_actions", {}).get("sap_writebacks", [])
        citations = report_decision.get("engine_b_rag_citations", [])

        print("-" * 90)
        print("🧠 EXPLAINABLE AI (XAI) ATTRIBUTION BREAKDOWN:")
        attributions = pred.get("feature_attributions", [])
        if attributions:
            for a in attributions:
                print(f"   • {a['contribution_pct']:>5.1f}%  ->  {a['factor']}")
        else:
            print("   • Baseline statistical transit variance")

        print("-" * 90)
        print("🔍 IDENTIFIED ROOT CAUSE BOTTLENECKS:")
        causes = pred.get("root_causes", [])
        if causes:
            for rc in causes:
                print(f"   • ⚠️  {rc}")
        else:
            print(f"   • {row['root_cause']}")

        print("-" * 90)
        print("🤖 SPECIALIST MULTI-AGENT ADJUDICATION:")
        print(f"   • Route Supervisor    : Telematics Active={agents.get('route_supervisor', {}).get('telematics_active', True)} | Speed={agents.get('route_supervisor', {}).get('transit_speed_kmh', 0.0):.1f} km/h")
        print(f"   • Contract Lawyer     : {contract.get('force_majeure_status', 'Standard Evaluation')}")
        print(f"   • SLA Penalty Total   : ${contract.get('sla_delay_penalty_usd', 0.0):,.2f}")
        print(f"   • QA & Mitigation     : {mitigation.get('approval_status', 'N/A')} (Cost: ${mitigation.get('total_mitigation_cost_usd', 0.0):,.2f})")

        if sap_actions:
            print("-" * 90)
            print("⚡ SIMULATED SAP ERP ACTIONS EXECUTED:")
            for act in sap_actions:
                print(f"   • {act['action']} on {act['table']}.{act['field']} = {act['value']} ({act['reason'][:70]}...)")

        if citations:
            print("-" * 90)
            print("📚 GOVERNING RAG POLICY CITATIONS:")
            for cit in citations:
                print(f"   • 📄 {cit}")

        print("-" * 90)
        print("📝 EXECUTIVE SYNTHESIS BRIEF:")
        print(f"   {report_decision.get('executive_decision_brief', 'N/A')}")
    else:
        print("-" * 90)
        print(f"• Root Cause Factors  : {row['root_cause']}")
    print("=" * 90 + "\n")


def list_orders(delayed_only: bool = False, limit: int = 20):
    """List stored orders in a clean tabular format"""
    conn = get_db_connection()
    c = conn.cursor()
    
    query = "SELECT order_id, customer_name, carrier_name, will_be_delayed, delay_probability, delay_hours, financial_risk_usd, predicted_at FROM ml_predictions"
    if delayed_only:
        query += " WHERE will_be_delayed = 1"
    query += f" ORDER BY prediction_id DESC LIMIT {limit}"
    
    c.execute(query)
    rows = c.fetchall()
    conn.close()

    if not rows:
        print("ℹ️ No matching records found.")
        return

    print("\n" + "=" * 105)
    print(f"{'Order ID':<18} {'Customer':<24} {'Status':<10} {'Prob':<8} {'Delay (h)':<10} {'Risk ($)':<12} {'Predicted At':<20}")
    print("-" * 105)
    for r in rows:
        status = "❌ DELAY" if r["will_be_delayed"] else "✅ ONTIME"
        cust = (r["customer_name"] or "Unknown")[:22]
        print(f"{r['order_id']:<18} {cust:<24} {status:<10} {r['delay_probability']:>5.1%}  {r['delay_hours']:>7.1f}h  ${r['financial_risk_usd']:>10.2f}  {r['predicted_at'][:19]}")
    print("=" * 105 + "\n")


def export_markdown(out_file: Path = None, limit: int = None):
    """Export stored predictions to a formatted Markdown report"""
    conn = get_db_connection()
    c = conn.cursor()
    query = "SELECT * FROM ml_predictions ORDER BY will_be_delayed DESC, delay_probability DESC"
    if limit and limit > 0:
        query += f" LIMIT {limit}"
    c.execute(query)
    rows = c.fetchall()
    conn.close()

    if not rows:
        print("ℹ️ No records to export.")
        return

    if out_file is None:
        out_file = PROJECT_ROOT / "PREDICTIONS_REPORT.md"

    limit_str = f" (Top {limit:,} by Risk)" if limit else " (All Stored Records)"
    md = []
    md.append(f"# 📊 O2C AI Monitor - Order Predictions Report{limit_str}\n")
    md.append(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    md.append(f"**Total Orders Included in Report:** {len(rows):,}\n\n")
    md.append("| Order ID | Customer | Carrier | Status | Delay Prob | Delay (Hours) | Risk ($) | Root Cause Diagnosis |\n")
    md.append("|---|---|---|---|---|---|---|---|\n")

    for r in rows:
        status = "❌ **DELAYED**" if r["will_be_delayed"] else "✅ **ON-TIME**"
        cust = r["customer_name"] or "Unknown"
        carr = r["carrier_name"] or "Unknown"
        cause = (r["root_cause"] or "Normal transit conditions").replace("|", "-")
        md.append(f"| `{r['order_id']}` | {cust} | {carr} | {status} | {r['delay_probability']:.1%} | {r['delay_hours']:.1f}h | ${r['financial_risk_usd']:,.2f} | {cause} |\n")

    with open(out_file, "w", encoding="utf-8") as f:
        f.writelines(md)

    print(f"✅ Exported {len(rows):,} order predictions to Markdown: {out_file}")


def export_csv(out_file: Path = None, limit: int = None):
    """Export stored predictions to CSV"""
    import pandas as pd
    conn = get_db_connection()
    query = "SELECT * FROM ml_predictions ORDER BY will_be_delayed DESC, delay_probability DESC"
    if limit and limit > 0:
        query += f" LIMIT {limit}"
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        print("ℹ️ No records to export.")
        return

    if out_file is None:
        out_file = PROJECT_ROOT / "india_monitor_data" / "reports" / "predictions_export.csv"
        out_file.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(out_file, index=False)
    print(f"✅ Exported {len(df):,} order predictions to CSV: {out_file}")


def main():
    parser = argparse.ArgumentParser(description="Query & Export O2C AI Stored Results")
    parser.add_argument("--summary", action="store_true", help="Display overall metrics summary")
    parser.add_argument("--order", type=str, help="Look up a specific Order ID")
    parser.add_argument("--list", action="store_true", help="List recent order predictions")
    parser.add_argument("--delayed", action="store_true", help="List only delayed orders")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of rows displayed or exported")
    parser.add_argument("--export-md", action="store_true", help="Export predictions to PREDICTIONS_REPORT.md")
    parser.add_argument("--export-csv", action="store_true", help="Export predictions to CSV")
    args = parser.parse_args()

    # Default action if no arguments provided
    if not any([args.summary, args.order, args.list, args.delayed, args.export_md, args.export_csv]):
        show_summary()
        list_orders(limit=args.limit or 10)
        return

    if args.summary:
        show_summary()
    if args.order:
        query_order(args.order)
    if args.list or args.delayed:
        list_orders(delayed_only=args.delayed, limit=args.limit or 20)
    if args.export_md:
        export_markdown(limit=args.limit)
    if args.export_csv:
        export_csv(limit=args.limit)


if __name__ == "__main__":
    main()
