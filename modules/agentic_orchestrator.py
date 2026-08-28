"""
Agentic Orchestrator & LLM Synthesis (Phase 4 / Phase 5 Core)

Implements:
1. Daily Autonomous Agent Lifecycle:
   - Live Weather (OpenWeather) & News Ingestion -> SQLite
   - Incremental Policy Detection & RAG Index Verification
   - ML Delivery Delay Prediction (SAP + Live Weather + Strike News + History)
   - Dynamic RAG Knowledge Retrieval (SLAs, Contracts, QA Policies, Tickets)
2. Agentic LLM Synthesis Engine:
   - Force Majeure conditionality (12h notification rule & telematics verification)
   - Financial risk quantification ($500/day Platinum vs 5%/day Gold capped at 25%)
   - Emergency Air Freight replacement authorizations ($1,000 cap for Specialty Diets)
   - Receiving window violation ($150 redelivery fee waiver)
   - Carrier chargeback debit memos vs Enterprise net liability
   - Approval routing: Auto-Approve (<= $500) vs Regional Director MS Teams Escalation (> $500, 2h SLA)
3. Structured JSON decision artifact generation & Executive Briefing
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import numpy as np
import pandas as pd

# UTF-8 encoding support
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

# Dynamic Project Root Resolution
try:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
except Exception:
    PROJECT_ROOT = Path.cwd()

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from modules.config import DB_PATH, DOCS_DIR, VECTOR_DIR, CSV_DIR, OPENWEATHER_API_KEY, INDIA_CITIES, STRIKE_KEYWORDS
from modules.database_manager import DatabaseManager
from modules.weather_service import WeatherService
from modules.news_service import NewsService
from modules.weather_policy_generator import WeatherPolicyGenerator
from modules.strike_intelligence_generator import StrikeIntelligenceGenerator
from modules.ml_db_extension import MLDatabaseExtension
from modules.predictive_engine import PredictiveEngine
from modules.rag_engine import RAGEngine


from modules.agent_specialists import RouteSupervisorAgent, ContractAdjudicatorAgent, QualityMitigationAgent, LLMReasoningEngine
from modules.action_execution_engine import SAPActionExecutor, MSTeamsDispatcher, ClinicNotificationDispatcher


class LLMSynthesizer:
    """
    Phase 4 LLM Reasoning & Multi-Agent Orchestration Bridge.
    Coordinates specialist agents and synthesizes the final business decision.
    """

    def __init__(self, enable_teams_dispatch: bool = False):
        self.enable_teams_dispatch = enable_teams_dispatch
        self.route_agent = RouteSupervisorAgent()
        self.contract_agent = ContractAdjudicatorAgent()
        self.quality_agent = QualityMitigationAgent()
        self.llm_reasoning = LLMReasoningEngine()
        self.sap_executor = SAPActionExecutor(DB_PATH)
        self.teams_dispatcher = MSTeamsDispatcher()
        self.clinic_notifier = ClinicNotificationDispatcher(DB_PATH)

    def synthesize(self, prediction_payload: Dict[str, Any], order_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Coordinate the 4 specialist agents, execute physical ERP/Teams actions,
        and generate structured executive decision briefs.
        """
        order_data = order_data or {}
        order_id = str(prediction_payload.get("order_id", ""))
        customer_name = str(prediction_payload.get("customer_name", "Unknown Clinic"))
        customer_tier = str(prediction_payload.get("customer_tier", "Independent"))
        carrier_name = str(prediction_payload.get("carrier_name", "Unknown Carrier"))
        shipping_type = str(prediction_payload.get("shipping_type", "Road (FTL)"))
        dest_city = str(prediction_payload.get("dest_city", "Unknown"))
        order_val = float(prediction_payload.get("order_value_usd", 2500.0))
        delay_prob = float(prediction_payload.get("delay_probability", 0.0))
        will_delay = bool(prediction_payload.get("will_be_delayed", delay_prob >= 0.50))
        delay_hours = float(prediction_payload.get("delay_hours", 0.0))
        predicted_eta = str(prediction_payload.get("predicted_eta", ""))
        root_causes = prediction_payload.get("root_causes", prediction_payload.get("root_cause", []))
        if isinstance(root_causes, str):
            root_causes = [r.strip() for r in root_causes.split(";")]

        # ── 1. ROUTE & TELEMATICS SPECIALIST AGENT ─────────────────────────
        route_analysis = self.route_agent.analyze_route(prediction_payload, order_data)

        # ── 2. PROACTIVE 12-HOUR CLINIC EARLY WARNING DISPATCHER ───────────
        clinic_notice = self.clinic_notifier.send_proactive_12h_notice(
            order_id=order_id,
            clinic_name=customer_name,
            dest_city=dest_city,
            predicted_eta=predicted_eta,
            delay_reasons=root_causes
        )

        # ── 3. CONTRACT & SLA LEGAL ADJUDICATOR AGENT ──────────────────────
        contract_analysis = self.contract_agent.adjudicate_contract(
            prediction_payload=prediction_payload,
            order_data=order_data,
            route_analysis=route_analysis,
            notice_given_12h=clinic_notice.get("force_majeure_compliant", True)
        )

        # ── 4. QUALITY ASSURANCE & MITIGATION PLANNER AGENT ────────────────
        quality_analysis = self.quality_agent.plan_mitigation(
            prediction_payload=prediction_payload,
            order_data=order_data,
            contract_analysis=contract_analysis
        )

        # ── 5. PHASE 5 ACTION EXECUTION (SAP WRITE-BACKS & MS TEAMS CARDS) ──
        sap_actions = self.sap_executor.execute_sap_writebacks(
            order_id=order_id,
            predicted_eta=predicted_eta,
            qa_hold_required=quality_analysis.get("qa_hold_required", False),
            qa_reasons=quality_analysis.get("qa_hold_reasons", []),
            carrier_chargeback_usd=contract_analysis.get("total_carrier_chargeback_usd", 0.0),
            carrier_name=carrier_name,
            penalty_clauses=contract_analysis.get("penalty_clauses", [])
        )

        teams_dispatch_info = None
        if self.enable_teams_dispatch and quality_analysis.get("ms_teams_escalation_card"):
            teams_dispatch_info = self.teams_dispatcher.dispatch_card(
                quality_analysis["ms_teams_escalation_card"]
            )
        elif quality_analysis.get("ms_teams_escalation_card"):
            teams_dispatch_info = {"dispatch_status": "DISABLED_BY_CONFIGURATION (MSTeamsDispatcher turned off)"}

        # ── 6. LLM LEGAL & OPERATIONAL REASONING SYNTHESIS ──────────────────
        exec_brief = self.llm_reasoning.synthesize_executive_decision(
            order_id=order_id,
            customer_name=customer_name,
            customer_tier=customer_tier,
            carrier_name=carrier_name,
            shipping_type=shipping_type,
            delay_prob=delay_prob,
            will_delay=will_delay,
            delay_hours=delay_hours,
            predicted_eta=predicted_eta,
            route_analysis=route_analysis,
            contract_analysis=contract_analysis,
            quality_analysis=quality_analysis,
            rag_citations=prediction_payload.get("rag_sources", [])
        )

        # Build consolidated decision JSON artifact
        return {
            "order_id": order_id,
            "synthesis_timestamp": datetime.now().isoformat(),
            "customer_profile": {
                "name": customer_name,
                "tier": customer_tier,
                "destination_city": dest_city,
                "order_value_usd": order_val
            },
            "carrier_profile": {
                "name": carrier_name,
                "shipping_mode": shipping_type
            },
            "engine_a_ml_prediction": {
                "delay_probability": delay_prob,
                "is_delayed": will_delay,
                "predicted_delay_hours": delay_hours,
                "predicted_eta": predicted_eta,
                "haversine_distance_km": float(prediction_payload.get("haversine_distance_km", 0.0)),
                "required_transit_speed_kmh": float(prediction_payload.get("required_transit_speed_kmh", 0.0)),
                "root_causes": root_causes,
                "feature_attributions": prediction_payload.get("feature_attributions", [])
            },
            "specialist_agents_analysis": {
                "route_supervisor": route_analysis,
                "contract_adjudication": contract_analysis,
                "quality_mitigation": {
                    "qa_hold_required": quality_analysis.get("qa_hold_required", False),
                    "qa_hold_reasons": quality_analysis.get("qa_hold_reasons", []),
                    "mitigation_actions": quality_analysis.get("mitigation_actions", []),
                    "mitigation_cost_usd": quality_analysis.get("total_mitigation_cost_usd", 0.0)
                }
            },
            "legal_and_sla_adjudication": {
                "force_majeure_status": contract_analysis.get("force_majeure_status"),
                "sla_delay_penalty_usd": contract_analysis.get("sla_delay_penalty_usd"),
                "after_hours_redelivery_fee_usd": contract_analysis.get("after_hours_redelivery_fee_usd"),
                "total_carrier_chargeback_usd": contract_analysis.get("total_carrier_chargeback_usd"),
                "penalty_breakdown": contract_analysis.get("penalty_clauses", [])
            },
            "emergency_mitigation": {
                "actions": quality_analysis.get("mitigation_actions", []),
                "total_mitigation_cost_usd": quality_analysis.get("total_mitigation_cost_usd", 0.0),
                "approval_status": quality_analysis.get("approval_status"),
                "approval_gate": quality_analysis.get("approval_gate"),
                "ms_teams_escalation_card": quality_analysis.get("ms_teams_escalation_card"),
                "teams_card_dispatch": teams_dispatch_info
            },
            "executed_enterprise_actions": {
                "clinic_12h_notice": clinic_notice,
                "sap_writebacks": sap_actions
            },
            "engine_b_rag_citations": prediction_payload.get("rag_sources", []),
            "executive_decision_brief": exec_brief
        }


class AgenticOrchestrator:
    """
    Main Autonomous AI Agent Orchestrator.
    Drives the end-to-end daily lifecycle of the O2C Delivery Risk Copilot.
    """

    def __init__(self):
        print("\n" + "=" * 80)
        print("🤖 O2C AI MONITOR - AGENTIC ORCHESTRATOR (PHASE 4 & 5)")
        print("=" * 80 + "\n")
        
        self.db = DatabaseManager()
        self.weather = WeatherService(OPENWEATHER_API_KEY, INDIA_CITIES)
        self.news = NewsService(STRIKE_KEYWORDS, INDIA_CITIES)
        self.weather_policy_gen = WeatherPolicyGenerator()
        self.strike_intel_gen = StrikeIntelligenceGenerator()
        
        self.ml_db = MLDatabaseExtension(db_path=DB_PATH)
        self.rag = RAGEngine()
        self.predictive_engine = None
        self.llm_synthesizer = LLMSynthesizer()

    def run_daily_agent_cycle(
        self,
        date: str = None,
        order_limit: int = 5,
        target_order: str = None,
        all_orders: bool = False,
        rebuild_rag: bool = False,
        enable_teams_dispatch: bool = False
    ) -> Dict[str, Any]:
        """
        Execute the complete autonomous daily cycle:
        1. Ingest real-time Weather & Strike feeds into SQLite
        2. Check & index RAG policy knowledge base
        3. Load SAP tables & train Engine A ML models
        4. Predict delay risks with weather & strike intersection
        5. Retrieve RAG SLA clauses & contract addenda
        6. Execute Phase 4 LLM Decision Synthesis & MS Teams Approval Routing
        7. Generate daily executive report & export datasets
        """
        self.llm_synthesizer = LLMSynthesizer(enable_teams_dispatch=enable_teams_dispatch)
        session_id = self.db.session_start("daily_agentic_cycle")
        daily_reports_dir = PROJECT_ROOT / "india_monitor_data" / "reports"
        daily_reports_dir.mkdir(parents=True, exist_ok=True)
        today_str = date or datetime.now().strftime("%Y-%m-%d")

        print(f"📅 Running Daily Agent Cycle for Date: {today_str}")

        try:
            # ── STEP 1: INGEST REAL-TIME WEATHER & STRIKE FEEDS ────────────
            print("\n[Step 1/6] 📡 REAL-TIME EXTERNAL STREAM INGESTION")
            print("-" * 75)
            
            # 1.1 Weather Ingestion
            w_data = self.weather.fetch_historical(today_str) if date else self.weather.fetch_current()
            w_saved, _ = self.db.write_weather(w_data, session_id) if w_data else (0, 0)
            print(f"   🌦️  Weather Feed: Ingested {w_saved} new readings into SQLite")

            # 1.2 Strike & Disruption News Ingestion
            s_data = self.news.fetch(date=date)
            s_saved, _ = self.db.write_strikes(s_data, session_id) if s_data else (0, 0)
            print(f"   📰 News Feed   : Ingested {s_saved} disruption articles into SQLite")

            # ── STEP 2: RAG KNOWLEDGE VERIFICATION & REBUILD ───────────────
            print("\n[Step 2/6] 📚 RAG KNOWLEDGE BASE VERIFICATION")
            print("-" * 75)
            # Re-generate policy docs from fresh weather/news if needed
            self.weather_policy_gen.generate_all_policies()
            self.strike_intel_gen.generate_all_intelligence()
            self.rag.initialize(force_rebuild=rebuild_rag)
            print(f"   ✅ RAG Index Verified: {len(self.rag.vector_store.metadata)} vector chunks ready")

            # ── STEP 3: SAP FEATURE STORE & ENGINE A ML TRAINING ───────────
            print("\n[Step 3/6] ⚙️  SAP DATA INGESTION & ENGINE A ML TRAINING")
            print("-" * 75)
            from modules.config import INPUT_FILES_DIR, CSV_DIR
            input_dir = INPUT_FILES_DIR if Path(INPUT_FILES_DIR).exists() else CSV_DIR
            self.ml_db.load_sap_data_from_csv(input_dir)
            ml_df = self.ml_db.get_ml_ready_dataset()
            
            self.predictive_engine = PredictiveEngine(
                ml_db_extension=self.ml_db,
                rag_engine=self.rag,
                weather_service=self.weather
            )
            self.predictive_engine.train_models(ml_df)

            # ── STEP 4 & 5: PREDICT & SYNTHESIZE ACTIVE SAP ORDERS ─────────
            print("\n[Step 4/6] 📦 DUAL-ENGINE DELAY PREDICTION & CONTEXT RETRIEVAL")
            print("-" * 75)

            orders_to_process = []
            if target_order:
                orders_to_process = [str(target_order)]
            elif all_orders or order_limit is None or order_limit <= 0:
                orders_to_process = [str(oid) for oid in ml_df['order_id'].drop_duplicates()]
            else:
                orders_to_process = [str(oid) for oid in ml_df['order_id'].drop_duplicates().head(order_limit)]

            print(f"   Analyzing {len(orders_to_process)} order(s)...")

            synthesized_decisions = []
            for idx, ord_id in enumerate(orders_to_process, 1):
                # Predict via Engine A + retrieve Engine B RAG context
                order_data = self.ml_db.get_order_details(ord_id) or {}
                pred_result = self.predictive_engine.predict_delivery_delay(ord_id)
                
                # Synthesize via Phase 4 Multi-Agent Specialists & Phase 5 Executors
                decision = self.llm_synthesizer.synthesize(pred_result, order_data=order_data)
                synthesized_decisions.append(decision)

                print(f"\n   [{idx}/{len(orders_to_process)}] Order {ord_id} -> "
                      f"Status: {'❌ DELAYED' if decision['engine_a_ml_prediction']['is_delayed'] else '✅ ON TIME'} "
                      f"({decision['engine_a_ml_prediction']['delay_probability']:.1%}) | "
                      f"Penalty: ${decision['legal_and_sla_adjudication']['sla_delay_penalty_usd']:.2f} | "
                      f"Approval: {decision['emergency_mitigation']['approval_status']}")

            # ── STEP 6: EXPORT DAILY REPORT & SUMMARY ──────────────────────
            print("\n[Step 5/6] 📊 GENERATING DAILY AGENTIC DECISION REPORT")
            print("-" * 75)

            report_file = daily_reports_dir / f"daily_agent_report_{today_str}.json"
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump({
                    "date": today_str,
                    "generated_at": datetime.now().isoformat(),
                    "total_orders_analyzed": len(synthesized_decisions),
                    "delayed_orders_count": sum(1 for d in synthesized_decisions if d['engine_a_ml_prediction']['is_delayed']),
                    "total_financial_risk_usd": sum(d['legal_and_sla_adjudication']['sla_delay_penalty_usd'] for d in synthesized_decisions),
                    "total_carrier_chargebacks_usd": sum(d['legal_and_sla_adjudication']['total_carrier_chargeback_usd'] for d in synthesized_decisions),
                    "decisions": synthesized_decisions
                }, f, indent=2, ensure_ascii=False)

            print(f"   💾 Saved daily report: {report_file.name}")

            # Export CSV datasets
            self._export_csvs(today_str)

            print("\n[Step 6/6] 🏆 DAILY AGENTIC CYCLE COMPLETE")
            print("-" * 75)
            self.db.session_end(session_id, status="success", cities=w_saved, articles=s_saved)

            print("\n" + "=" * 80)
            print(f"✅ O2C AI Agent finished daily execution for {today_str} successfully!")
            print("=" * 80 + "\n")

            return {
                "status": "success",
                "date": today_str,
                "report_file": str(report_file),
                "decisions": synthesized_decisions
            }

        except Exception as e:
            print(f"\n❌ Agentic cycle error: {e}")
            import traceback
            traceback.print_exc()
            self.db.session_end(session_id, status="error", error=str(e))
            raise

    def _export_csvs(self, target_date: str):
        """Export daily CSV summaries"""
        w_df = self.db.read_weather(date=target_date)
        if not w_df.empty:
            w_df.to_csv(CSV_DIR / f"weather_{target_date}.csv", index=False)
        s_df = self.db.read_strikes(date=target_date)
        if not s_df.empty:
            s_df.to_csv(CSV_DIR / f"strikes_{target_date}.csv", index=False)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="O2C AI Agentic Orchestrator")
    parser.add_argument("--date", type=str, default=None, help="Target Date (YYYY-MM-DD)")
    parser.add_argument("--order", type=str, default=None, help="Single Order ID to analyze")
    parser.add_argument("--limit", type=int, default=5, help="Number of active orders to analyze")
    parser.add_argument("--all-orders", "--all", action="store_true", default=False, help="Process ALL active orders in dataset")
    parser.add_argument("--rebuild-rag", action="store_true", default=False, help="Rebuild RAG index")
    parser.add_argument("--enable-teams", action="store_true", default=False, help="Enable live Microsoft Teams webhook dispatching")
    args = parser.parse_args()

    agent = AgenticOrchestrator()
    agent.run_daily_agent_cycle(
        date=args.date,
        order_limit=args.limit,
        target_order=args.order,
        all_orders=args.all_orders,
        rebuild_rag=args.rebuild_rag,
        enable_teams_dispatch=args.enable_teams
    )


if __name__ == "__main__":
    main()
