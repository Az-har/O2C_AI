#!/usr/bin/env python3
"""
O2C AI Monitor - Master Daily AI Agent Pipeline

Executes the complete end-to-end daily operational lifecycle:
1. Fetch live or historical weather data -> Store in SQLite
2. Fetch transportation disruption news -> Store in SQLite
3. Verify / generate dynamic policy documents -> Incremental RAG Vectorization
4. Ingest SAP tables & execute Engine A ML delay prediction (combining SAP + Live Weather + Strike disruptions + History)
5. Retrieve exact SLA, vendor contract, and QA rules via Engine B RAG
6. Execute Phase 4 Agentic Orchestrator & LLM Synthesis:
   - Force Majeure conditionality (Act of God 72h waiver vs 12h notification mandate)
   - Exact SLA financial penalty calculation ($500/day Platinum vs 5%/day Gold)
   - Emergency Air Freight replacement authorizations ($1,000 cap for Specialty Diets)
   - Receiving window violation ($150 redelivery fee waiver)
   - Approval routing (Auto-Approve <= $500 vs Regional Director MS Teams Escalation > $500)
7. Generate daily executive decision JSON report and export CSV datasets

Usage:
    python main_pipeline.py
    python main_pipeline.py --order 800000000000001
    python main_pipeline.py --limit 10
    python main_pipeline.py --date 2026-08-25
    python main_pipeline.py --rebuild-rag
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

# UTF-8 console output for Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

# Databricks Workspace Path Support
DATABRICKS_PATH = Path("/Workspace/Users/ayyash.a@tcs.com/O2C_AI")
if DATABRICKS_PATH.exists() or "DATABRICKS_RUNTIME_VERSION" in os.environ:
    project_root = DATABRICKS_PATH
else:
    try:
        project_root = Path(__file__).resolve().parent
    except NameError:
        project_root = DATABRICKS_PATH

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from modules.agentic_orchestrator import AgenticOrchestrator


def main():
    """Main CLI entry point for daily AI Agent execution"""
    parser = argparse.ArgumentParser(description="O2C Delivery Risk Copilot - Daily Agent Pipeline")
    parser.add_argument("--date", type=str, default=None, help="Target Date (YYYY-MM-DD)")
    parser.add_argument("--order", type=str, default=None, help="Specific SAP Sales Order ID to analyze")
    parser.add_argument("--limit", type=int, default=5, help="Number of active SAP orders to process (default: 5)")
    parser.add_argument("--all-orders", "--all", action="store_true", default=False, help="Process ALL active SAP orders in dataset")
    parser.add_argument("--rebuild-rag", action="store_true", default=False, help="Force rebuild RAG vector store")
    parser.add_argument("--enable-teams", action="store_true", default=False, help="Enable live Microsoft Teams webhook dispatching")
    args = parser.parse_args()

    orchestrator = AgenticOrchestrator()
    orchestrator.run_daily_agent_cycle(
        date=args.date,
        order_limit=args.limit,
        target_order=args.order,
        all_orders=args.all_orders,
        rebuild_rag=args.rebuild_rag,
        enable_teams_dispatch=args.enable_teams
    )


if __name__ == "__main__":
    main()
