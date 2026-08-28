# Databricks Daily AI Agent Runner
# Workspace Path: /Workspace/Users/ayyash.a@tcs.com/O2C_AI
#
# This script executes the autonomous O2C Daily AI Agent lifecycle directly on Databricks Runtime.
#
# To run on Databricks:
# 1. As a Databricks Job / Task:
#    python databricks_daily_job.py --all-orders
#
# 2. Or from a Databricks Notebook cell:
#    %run ./databricks_daily_job

import os
import sys
from pathlib import Path

# Dynamic Project Root Resolution
try:
    PROJECT_ROOT = Path(__file__).resolve().parent
except Exception:
    PROJECT_ROOT = Path.cwd()

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from modules.agentic_orchestrator import AgenticOrchestrator


def run_databricks_agent(
    date: str = None,
    order_limit: int = None,
    target_order: str = None,
    all_orders: bool = True,
    rebuild_rag: bool = False,
    enable_teams_dispatch: bool = False
):
    """Entry point for Databricks execution"""
    print("=" * 80)
    print("🚀 LAUNCHING O2C AI AGENT ON DATABRICKS RUNTIME")
    print(f"📍 Project Root: {PROJECT_ROOT}")
    print("=" * 80)

    agent = AgenticOrchestrator()
    result = agent.run_daily_agent_cycle(
        date=date,
        order_limit=order_limit,
        target_order=target_order,
        all_orders=all_orders,
        rebuild_rag=rebuild_rag,
        enable_teams_dispatch=enable_teams_dispatch
    )
    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Databricks O2C AI Agent Job")
    parser.add_argument("--date", type=str, default=None, help="Target execution date (YYYY-MM-DD)")
    parser.add_argument("--order", type=str, default=None, help="Single target order ID")
    parser.add_argument("--limit", type=int, default=None, help="Max orders to process")
    parser.add_argument("--all-orders", "--all", action="store_true", default=True, help="Process all orders in dataset")
    parser.add_argument("--rebuild-rag", action="store_true", default=False, help="Rebuild RAG index")
    parser.add_argument("--enable-teams", action="store_true", default=False, help="Enable Teams dispatcher")
    args = parser.parse_args()

    run_databricks_agent(
        date=args.date,
        order_limit=args.limit,
        target_order=args.order,
        all_orders=args.all_orders,
        rebuild_rag=args.rebuild_rag,
        enable_teams_dispatch=args.enable_teams
    )
