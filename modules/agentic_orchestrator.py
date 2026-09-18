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

import time
import logging
from modules.config import DB_PATH, DOCS_DIR, VECTOR_DIR, CSV_DIR, LOG_DIR, OPENWEATHER_API_KEY, INDIA_CITIES, STRIKE_KEYWORDS
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


def _get_orchestrator_logger() -> logging.Logger:
    orch_logger = logging.getLogger("AgenticOrchestrator")
    orch_logger.setLevel(logging.INFO)
    if not orch_logger.handlers:
        log_file = LOG_DIR / f"orchestrator_{datetime.now():%Y%m%d}.log"
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        orch_logger.addHandler(fh)
    return orch_logger

logger = _get_orchestrator_logger()


class LLMSynthesizer:
    """
    Phase 4 LLM Reasoning & Multi-Agent Orchestration Bridge.
    Coordinates specialist agents and synthesizes the final business decision.
    """

    def __init__(
        self,
        enable_teams_dispatch: bool = False,
        route_agent: Optional[RouteSupervisorAgent] = None,
        contract_agent: Optional[ContractAdjudicatorAgent] = None,
        quality_agent: Optional[QualityMitigationAgent] = None,
        llm_reasoning: Optional[LLMReasoningEngine] = None,
        sap_executor: Optional[SAPActionExecutor] = None,
        teams_dispatcher: Optional[MSTeamsDispatcher] = None,
        clinic_notifier: Optional[ClinicNotificationDispatcher] = None,
        db_manager: Optional[DatabaseManager] = None
    ):
        self.enable_teams_dispatch = enable_teams_dispatch
        self.db = db_manager or DatabaseManager()
        self.route_agent = route_agent or RouteSupervisorAgent()
        self.contract_agent = contract_agent or ContractAdjudicatorAgent()
        self.quality_agent = quality_agent or QualityMitigationAgent()
        self.llm_reasoning = llm_reasoning or LLMReasoningEngine()
        self.sap_executor = sap_executor or SAPActionExecutor(db_manager=self.db)
        self.teams_dispatcher = teams_dispatcher or MSTeamsDispatcher()
        self.clinic_notifier = clinic_notifier or ClinicNotificationDispatcher(db_manager=self.db)

    def _build_consolidated_decision(self, prediction_payload: Dict[str, Any], order_data: Dict[str, Any] = None) -> Dict[str, Any]:
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

        # Fast-Track Triage: Low-risk, on-schedule orders bypass heavy multi-agent RAG/ChromaDB queries
        has_specialty = bool(prediction_payload.get("has_specialty_diet", order_data.get("has_specialty_diet", False)))
        weather_alert = bool(prediction_payload.get("weather_alert"))
        strike_alert = bool(prediction_payload.get("strike_alert"))
        is_fast_track = (not will_delay) and (delay_prob < 0.40) and (not has_specialty) and (not weather_alert) and (not strike_alert)

        if is_fast_track:
            dist_km = float(prediction_payload.get("haversine_distance_km", order_data.get("haversine_distance_km", 500.0)))
            spd_kmh = float(prediction_payload.get("required_transit_speed_kmh", order_data.get("required_transit_speed_kmh", 25.0)))
            route_analysis = {
                "agent_name": "RouteSupervisorAgent",
                "telematics_active": True,
                "telematics_penalty_usd": 0.0,
                "telematics_notes": ["Fast-Track: On schedule, telemetry nominal"],
                "route_hazards": [],
                "corridor_distance_km": dist_km,
                "transit_speed_kmh": spd_kmh,
                "destination_city": dest_city,
                "shipping_mode": shipping_type,
                "weather_hazard_detected": False,
                "strike_disruptions_detected": False,
                "autonomous_reasoning": "Fast-track approved; transit corridor nominal."
            }
            contract_analysis = {
                "agent_name": "ContractAdjudicatorAgent",
                "sla_delay_penalty_usd": 0.0,
                "force_majeure_invoked": False,
                "total_carrier_chargeback_usd": 0.0,
                "applied_clauses": ["Standard Transit (On Schedule)"],
                "notice_given_12h": True,
                "carrier_name": carrier_name,
                "customer_tier": customer_tier
            }
            quality_analysis = {
                "agent_name": "QualityMitigationAgent",
                "qa_hold_required": False,
                "qa_hold_reasons": [],
                "emergency_air_freight_recommended": False,
                "mitigation_cost_usd": 0.0,
                "requires_director_approval": False,
                "approval_status": "AUTONOMOUSLY_APPROVED",
                "ms_teams_escalation_card": None
            }
            sap_actions = {
                "status": "FAST_TRACK_APPROVED",
                "actions_taken": ["STANDARD_TRANSIT_MAINTAINED"]
            }
            exec_brief = (
                f"Order {order_id} destined for {customer_name} ({customer_tier}) is ON SCHEDULE "
                f"(Delay Probability: {delay_prob:.1%}). Fast-track autonomous execution approved; "
                f"standard transit milestones and SAP delivery schedule maintained."
            )
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
                    "is_delayed": False,
                    "predicted_delay_hours": 0.0,
                    "predicted_eta": predicted_eta or datetime.now().strftime("%Y-%m-%d"),
                    "root_causes": ["On schedule; normal transit leeways"]
                },
                "route_and_transit_supervision": route_analysis,
                "legal_and_sla_adjudication": contract_analysis,
                "emergency_mitigation": quality_analysis,
                "executed_sap_actions": sap_actions,
                "executive_decision_brief": exec_brief
            }

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

    def synthesize_with_graph(
        self,
        prediction_payload: Dict[str, Any],
        order_data: Dict[str, Any] = None,
        export_audit_report: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Execute decision synthesis through the full LangGraph state machine in a single pass.
        Eliminates duplicate specialist re-execution and redundant ERP write-backs.
        """
        from modules.agentic_graph import run_order_graph
        order_id = str(prediction_payload.get("order_id", ""))
        graph_state = run_order_graph(order_id, prediction_payload, order_data, export_audit_report=export_audit_report)
        
        od = order_data or {}
        route_analysis = graph_state.get("route_findings", {})
        contract_analysis = graph_state.get("legal_findings", {})
        quality_analysis = graph_state.get("quality_findings", {})
        
        exec_brief = graph_state.get("final_decision") or "Decision synthesized via LangGraph multi-agent state machine."
        req_approval = bool(graph_state.get("requires_human_approval", False))
        cost = float(graph_state.get("total_mitigation_cost", quality_analysis.get("total_mitigation_cost_usd", 0.0)))
        
        decision = {
            "order_id": order_id,
            "synthesis_timestamp": datetime.now().isoformat(),
            "customer_profile": {
                "name": str(prediction_payload.get("customer_name") or od.get("customer_name", "Unknown Clinic")),
                "tier": str(contract_analysis.get("customer_tier") or prediction_payload.get("customer_tier", "Independent"))
            },
            "carrier_profile": {
                "name": str(prediction_payload.get("carrier_name") or od.get("carrier_name", "Unknown Carrier")),
                "shipping_mode": str(route_analysis.get("shipping_mode") or prediction_payload.get("shipping_type", "Road (FTL)"))
            },
            "engine_a_ml_prediction": {
                "delay_probability": float(prediction_payload.get("delay_probability", 0.0)),
                "is_delayed": bool(prediction_payload.get("will_be_delayed", False)),
                "predicted_delay_hours": float(prediction_payload.get("delay_hours", 0.0)),
                "predicted_eta": str(prediction_payload.get("predicted_eta", ""))
            },
            "route_and_telematics_audit": {
                "telematics_active": bool(route_analysis.get("telematics_active", True)),
                "active_hazards": route_analysis.get("route_hazards", []),
                "telematics_notes": route_analysis.get("telematics_notes", []),
                "distance_km": float(route_analysis.get("corridor_distance_km", prediction_payload.get("haversine_distance_km", 0.0))),
                "transit_speed_kmh": float(route_analysis.get("transit_speed_kmh", prediction_payload.get("required_transit_speed_kmh", 0.0)))
            },
            "legal_and_sla_adjudication": {
                "force_majeure_status": contract_analysis.get("force_majeure_status"),
                "sla_delay_penalty_usd": float(contract_analysis.get("sla_delay_penalty_usd", 0.0)),
                "after_hours_redelivery_fee_usd": float(contract_analysis.get("after_hours_redelivery_fee_usd", 0.0)),
                "total_carrier_chargeback_usd": float(contract_analysis.get("total_carrier_chargeback_usd", 0.0)),
                "penalty_breakdown": contract_analysis.get("penalty_clauses", [])
            },
            "emergency_mitigation": {
                "actions": quality_analysis.get("mitigation_actions", []),
                "total_mitigation_cost_usd": cost,
                "approval_status": "DIRECTOR_APPROVAL_REQUIRED" if req_approval else "AUTONOMOUSLY_APPROVED",
                "approval_gate": "MS Teams Escalation Gate" if req_approval else "AI Copilot Auto-Approval",
                "ms_teams_escalation_card": graph_state.get("escalation_payload")
            },
            "executed_enterprise_actions": {
                "sap_writebacks": graph_state.get("executed_erp_actions", [])
            },
            "engine_b_rag_citations": prediction_payload.get("rag_sources", []),
            "executive_decision_brief": exec_brief,
            "langgraph_state": {
                "requires_human_approval": req_approval,
                "approval_reason": graph_state.get("approval_reason", ""),
                "total_mitigation_cost": cost,
                "audit_trail": graph_state.get("audit_trail", []),
                "governance_checkpoint": "human_approval_checkpoint" if req_approval else "action_execution_node"
            }
        }
        return decision

    def synthesize(self, prediction_payload: Dict[str, Any], order_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Unified Cognitive Synthesis Entry Point.
        Mandates 100% graph-native execution through the compiled LangGraph multi-agent state machine.
        """
        return self.synthesize_with_graph(prediction_payload, order_data)


class AgenticOrchestrator:
    """
    Main Autonomous AI Agent Orchestrator.
    Drives the end-to-end daily lifecycle of the O2C Delivery Risk Copilot.
    """

    def __init__(
        self,
        db_manager: Optional[DatabaseManager] = None,
        weather_service: Optional[WeatherService] = None,
        news_service: Optional[NewsService] = None,
        weather_policy_gen: Optional[WeatherPolicyGenerator] = None,
        strike_intel_gen: Optional[StrikeIntelligenceGenerator] = None,
        ml_db_extension: Optional[MLDatabaseExtension] = None,
        rag_engine: Optional[RAGEngine] = None,
        predictive_engine: Optional[PredictiveEngine] = None,
        llm_synthesizer: Optional[LLMSynthesizer] = None,
    ):
        print("\n" + "=" * 80)
        print("🤖 O2C AI MONITOR - AGENTIC ORCHESTRATOR (PHASE 4 & 5)")
        print("=" * 80 + "\n")
        
        self.db = db_manager or DatabaseManager()
        self.weather = weather_service or WeatherService(OPENWEATHER_API_KEY, INDIA_CITIES)
        self.news = news_service or NewsService(STRIKE_KEYWORDS, INDIA_CITIES)
        self.weather_policy_gen = weather_policy_gen or WeatherPolicyGenerator()
        self.strike_intel_gen = strike_intel_gen or StrikeIntelligenceGenerator()
        
        self.ml_db = ml_db_extension or MLDatabaseExtension(db_path=DB_PATH)
        self.rag = rag_engine or RAGEngine()
        self.predictive_engine = predictive_engine
        self.llm_synthesizer = llm_synthesizer or LLMSynthesizer(db_manager=self.db)

    def synthesize_with_graph(self, prediction_payload: Dict[str, Any], order_data: Dict[str, Any] = None, export_audit_report: Optional[bool] = None) -> Dict[str, Any]:
        """Execute decision synthesis through the full LangGraph state machine via LLMSynthesizer."""
        return self.llm_synthesizer.synthesize_with_graph(prediction_payload, order_data=order_data, export_audit_report=export_audit_report)

    def synthesize(self, prediction_payload: Dict[str, Any], order_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Unified Cognitive Synthesis Entry Point via LLMSynthesizer."""
        return self.llm_synthesizer.synthesize(prediction_payload, order_data=order_data)

    def run_daily_agent_cycle(
        self,
        date: str = None,
        order_limit: int = 5,
        target_order: str = None,
        all_orders: bool = False,
        repredict: bool = False,
        rebuild_rag: bool = False,
        enable_teams_dispatch: bool = False,
        use_agent_graph: bool = True
    ) -> Dict[str, Any]:
        """
        Execute the complete autonomous daily cycle:
        1. Ingest real-time Weather & Strike feeds into SQLite (Resilient step execution)
        2. Check & index RAG policy knowledge base
        3. Load SAP tables & train Engine A ML models
        4. Predict delay risks with weather & strike intersection
        5. Concurrently synthesize Phase 4 LLM Decisions & MS Teams Approval Routing
        6. Generate daily executive report & export datasets
        """
        self.llm_synthesizer.enable_teams_dispatch = enable_teams_dispatch
        session_id = self.db.session_start("daily_agentic_cycle")
        daily_reports_dir = PROJECT_ROOT / "india_monitor_data" / "reports"
        daily_reports_dir.mkdir(parents=True, exist_ok=True)
        today_str = date or datetime.now().strftime("%Y-%m-%d")

        print(f"📅 Running Daily Agent Cycle for Date: {today_str}")

        try:
            # ── STEP 1: INGEST REAL-TIME WEATHER & STRIKE FEEDS ────────────
            print("\n[Step 1/6] 📡 REAL-TIME EXTERNAL STREAM INGESTION")
            print("-" * 75)
            
            # 1.1 Weather Ingestion (Resilient with graceful degradation - Critique 1.1)
            w_saved = 0
            try:
                w_data = self.weather.fetch_historical(today_str) if date else self.weather.fetch_current()
                w_saved, _ = self.db.write_weather(w_data, session_id) if w_data else (0, 0)
                print(f"   🌦️  Weather Feed: Ingested {w_saved} new readings into SQLite")
            except Exception as e:
                print(f"   ⚠️  Weather Feed Warning: {e}. Proceeding with cached database records.")

            # 1.2 Strike & Disruption News Ingestion (Resilient with graceful degradation - Critique 1.1)
            s_saved = 0
            try:
                s_data = self.news.fetch(date=date)
                s_saved, _ = self.db.write_strikes(s_data, session_id) if s_data else (0, 0)
                print(f"   📰 News Feed   : Ingested {s_saved} disruption articles into SQLite")
            except Exception as e:
                print(f"   ⚠️  News Feed Warning: {e}. Proceeding with cached database records.")

            # ── STEP 2: RAG KNOWLEDGE BASE VERIFICATION ───────────────
            print("\n[Step 2/6] 📚 RAG KNOWLEDGE BASE VERIFICATION")
            print("-" * 75)
            try:
                self.weather_policy_gen.generate_all_policies()
                self.strike_intel_gen.generate_all_intelligence()
            except Exception as e:
                print(f"   ⚠️  Policy Generation Note: {e}. Utilizing existing verified policy corpus.")
            
            self.rag.initialize(force_rebuild=rebuild_rag)
            print(f"   ✅ RAG Index Verified: {len(self.rag.vector_store.metadata)} vector chunks ready")

            # ── STEP 3: SAP FEATURE STORE & ENGINE A ML TRAINING ───────────
            print("\n[Step 3/6] ⚙️  SAP DATA INGESTION & ENGINE A ML TRAINING")
            print("-" * 75)
            from modules.config import INPUT_FILES_DIR, CSV_DIR
            input_dir = INPUT_FILES_DIR if Path(INPUT_FILES_DIR).exists() else CSV_DIR
            self.ml_db.load_sap_data_from_csv(input_dir)
            ml_df = self.ml_db.get_ml_ready_dataset()
            
            if self.predictive_engine is None:
                self.predictive_engine = PredictiveEngine(
                    ml_db_extension=self.ml_db,
                    rag_engine=self.rag,
                    weather_service=self.weather
                )
            self.predictive_engine.train_models(ml_df)
            from modules.agent_tools import set_shared_predictive_engine
            set_shared_predictive_engine(self.predictive_engine)

            # ── STEP 4 & 5: PREDICT & CONCURRENTLY SYNTHESIZE SAP ORDERS ──
            print("\n[Step 4/6] 📦 DUAL-ENGINE DELAY PREDICTION & CONTEXT RETRIEVAL")
            print("-" * 75)

            orders_to_process = []
            if target_order:
                orders_to_process = [str(target_order)]
            else:
                total_dataset_orders = ml_df['order_id'].drop_duplicates().tolist()
                
                # Check for already predicted orders to skip them unless repredict=True
                if not repredict:
                    already_predicted = self.ml_db.get_predicted_order_ids()
                    unpredicted_df = ml_df[~ml_df['order_id'].astype(str).isin(already_predicted)]
                    
                    if len(already_predicted) > 0:
                        print(f"   ⚡ Order Caching: {len(already_predicted):,} orders already predicted in database (skipping).")
                    
                    if unpredicted_df.empty:
                        print(f"   ✨ All {len(total_dataset_orders):,} active orders have already been predicted.")
                        print(f"   💡 Pass --repredict (or repredict=True) to force re-evaluation of all orders.")
                        orders_to_process = []
                    else:
                        if all_orders or order_limit is None or order_limit <= 0:
                            orders_to_process = [str(oid) for oid in unpredicted_df['order_id'].drop_duplicates()]
                        else:
                            orders_to_process = [str(oid) for oid in unpredicted_df['order_id'].drop_duplicates().head(order_limit)]
                        print(f"   📦 Found {len(orders_to_process):,} NEW unpredicted order(s) to process.")
                else:
                    if all_orders or order_limit is None or order_limit <= 0:
                        orders_to_process = [str(oid) for oid in total_dataset_orders]
                    else:
                        orders_to_process = [str(oid) for oid in total_dataset_orders[:order_limit]]
                    print(f"   🔄 Force Re-Predict Active: Processing {len(orders_to_process):,} order(s)...")

            total_analyzed = 0
            total_delayed = 0
            total_financial_risk = 0.0
            total_carrier_chargebacks = 0.0
            retained_decisions = []

            if orders_to_process:
                print(f"   ⚡ Executing high-performance vectorized prediction across {len(orders_to_process):,} orders...")
                orders_data = [self.ml_db.get_order_details(oid) for oid in orders_to_process]
                pred_results = self.predictive_engine.predict_batch(orders_to_process, orders_data=orders_data)

                # Hardware-Optimized Concurrency Tuning (Ryzen 3 4-Core + Radeon RX 6600 8GB VRAM)
                import torch
                if hasattr(torch, "set_num_threads"):
                    torch.set_num_threads(1)

                from concurrent.futures import ThreadPoolExecutor
                # Ensure at least 2 CPU cores are left completely free for Windows OS, DWM, and input hardware interrupts
                avail_cpus = os.cpu_count() or 2
                synth_workers = 1 if (use_agent_graph or target_order) else min(2, max(1, avail_cpus - 2))

                def _synth_task(args):
                    idx, ord_id, od, pred_res = args
                    try:
                        # Scoped Audit Export: Always for explicit targets, delayed, or high-risk orders; skip disk write for purely nominal batch orders
                        is_critical_audit = (
                            target_order is not None
                            or bool(pred_res.get("will_be_delayed"))
                            or float(pred_res.get("delay_probability", 0.0)) >= 0.40
                            or bool((od or {}).get("has_specialty_diet"))
                            or idx <= 3
                        )
                        if use_agent_graph:
                            decision = self.synthesize_with_graph(pred_res, order_data=od or {}, export_audit_report=is_critical_audit)
                        else:
                            decision = self.llm_synthesizer._build_consolidated_decision(pred_res, order_data=od or {})
                    except Exception as ex:
                        logger.error(f"Error synthesizing decision for order {ord_id}: {ex}", exc_info=True)
                        decision = {
                            "order_id": str(ord_id),
                            "synthesis_timestamp": datetime.now().isoformat(),
                            "customer_profile": {"name": od.get("customer_name", "Unknown"), "tier": od.get("customer_tier", "Independent")},
                            "carrier_profile": {"name": od.get("carrier_name", "Unknown"), "shipping_mode": od.get("shipping_type", "Road")},
                            "engine_a_ml_prediction": {
                                "delay_probability": float(pred_res.get("delay_probability", 0.0)),
                                "is_delayed": bool(pred_res.get("will_be_delayed", False)),
                                "predicted_delay_hours": float(pred_res.get("delay_hours", 0.0)),
                                "predicted_eta": str(pred_res.get("predicted_eta", ""))
                            },
                            "legal_and_sla_adjudication": {"sla_delay_penalty_usd": 0.0, "total_carrier_chargeback_usd": 0.0},
                            "emergency_mitigation": {"approval_status": "AUTONOMOUSLY_APPROVED"},
                            "executive_decision_brief": f"Order {ord_id} processed under fallback: {ex}"
                        }
                    pred_with_decision = dict(pred_res)
                    pred_with_decision["decision_json"] = json.dumps(decision, default=str)
                    
                    # Pacing Guardrail: 50ms pause per order prevents network socket exhaustion,
                    # allows SQLite WAL checkpointing, and prevents GPU/CPU thermal saturation
                    import time
                    time.sleep(0.05)
                    return idx, ord_id, decision, pred_with_decision

                CHUNK_SIZE = 50
                total_orders = len(orders_to_process)
                total_analyzed = 0
                total_delayed = 0
                total_financial_risk = 0.0
                total_carrier_chargebacks = 0.0
                retained_decisions = []
                total_saved_predictions = 0

                synth_start_time = time.time()
                progress_file = LOG_DIR / "pipeline_progress.json"

                def _write_progress(status_str: str, curr_count: int):
                    elapsed = max(0.001, time.time() - synth_start_time)
                    speed = curr_count / elapsed
                    remaining = max(0, total_orders - curr_count)
                    eta_sec = remaining / speed if speed > 0 else 0
                    eta_m, eta_s = divmod(int(eta_sec), 60)
                    eta_h, eta_m = divmod(eta_m, 60)
                    eta_formatted = f"{eta_h}h {eta_m}m {eta_s}s" if eta_h > 0 else f"{eta_m}m {eta_s}s"
                    pct = (curr_count / total_orders) if total_orders > 0 else 1.0

                    payload = {
                        "status": status_str,
                        "date": today_str,
                        "started_at": datetime.fromtimestamp(synth_start_time).isoformat(),
                        "last_updated": datetime.now().isoformat(),
                        "processed_orders": curr_count,
                        "total_orders": total_orders,
                        "progress_percent": round(pct * 100, 1),
                        "orders_per_second": round(speed, 1),
                        "elapsed_seconds": round(elapsed, 1),
                        "estimated_seconds_remaining": round(eta_sec, 1),
                        "eta_formatted": eta_formatted,
                        "delayed_orders_count": total_delayed,
                        "on_time_orders_count": curr_count - total_delayed,
                        "total_financial_risk_usd": round(total_financial_risk, 2),
                        "total_carrier_chargebacks_usd": round(total_carrier_chargebacks, 2),
                        "active_workers": synth_workers
                    }
                    try:
                        with open(progress_file, "w", encoding="utf-8") as pf:
                            json.dump(payload, pf, indent=2)
                    except Exception:
                        pass
                    return pct, speed, eta_formatted

                logger.info(f"Starting batch decision synthesis for {total_orders:,} orders with {synth_workers} workers (Chunk: {CHUNK_SIZE}, Pacing: 50ms).")

                for chunk_start in range(0, total_orders, CHUNK_SIZE):
                    chunk_end = min(chunk_start + CHUNK_SIZE, total_orders)
                    chunk_orders = orders_to_process[chunk_start:chunk_end]
                    chunk_data = orders_data[chunk_start:chunk_end]
                    chunk_preds = pred_results[chunk_start:chunk_end]

                    task_args = [
                        (chunk_start + i, oid, od, pr)
                        for i, (oid, od, pr) in enumerate(zip(chunk_orders, chunk_data, chunk_preds), 1)
                    ]

                    chunk_preds_to_record = []
                    with ThreadPoolExecutor(max_workers=synth_workers) as executor:
                        chunk_results = list(executor.map(_synth_task, task_args))

                    for idx, ord_id, decision, pred_with_decision in chunk_results:
                        is_del = decision['engine_a_ml_prediction']['is_delayed']
                        risk = decision['legal_and_sla_adjudication']['sla_delay_penalty_usd']
                        cb = decision['legal_and_sla_adjudication']['total_carrier_chargeback_usd']

                        total_analyzed += 1
                        if is_del:
                            total_delayed += 1
                            logger.info(
                                f"Order {ord_id} -> ❌ DELAYED ({decision['engine_a_ml_prediction']['delay_probability']:.1%}) | "
                                f"Penalty: ${risk:.2f} | Action: {decision['emergency_mitigation']['approval_status']}"
                            )
                        total_financial_risk += risk
                        total_carrier_chargebacks += cb

                        chunk_preds_to_record.append(pred_with_decision)

                        # Retain detailed decision dossiers for the report (all delayed up to 250, plus 50 on-time samples)
                        if is_del and len(retained_decisions) < 250:
                            retained_decisions.append(decision)
                        elif not is_del and len(retained_decisions) < 300:
                            retained_decisions.append(decision)

                        if idx <= 5 or idx % 25 == 0 or idx == total_orders:
                            pct, speed, eta_str = _write_progress("RUNNING", total_analyzed)
                            print(f"   📊 [{total_analyzed:,}/{total_orders:,} | {pct:.1%}] ⚡ {speed:.1f} ord/s | ⏳ ETA: {eta_str} | "
                                  f"❌ Delayed: {total_delayed:,} | 💸 Risk: ${total_financial_risk:,.2f}")

                    # Commit chunk to SQLite immediately under write lock to free RAM
                    saved_in_chunk = self.ml_db.record_predictions_batch(chunk_preds_to_record)
                    total_saved_predictions += saved_in_chunk
                    _write_progress("RUNNING", total_analyzed)
                    logger.info(f"Chunk committed {saved_in_chunk:,} records to SQLite. Cumulative: {total_analyzed:,}/{total_orders:,}.")
                    del chunk_results
                    del chunk_preds_to_record

                _write_progress("COMPLETED", total_analyzed)
                logger.info(f"Synthesis complete: {total_analyzed:,} evaluated, {total_delayed:,} delayed, ${total_financial_risk:,.2f} risk.")
                print(f"\n   💾 Committed {total_saved_predictions:,} prediction records to SQLite across {total_orders:,} evaluated orders.")

            # ── STEP 6: EXPORT DAILY REPORT & SUMMARY ──────────────────────
            print("\n[Step 5/6] 📊 GENERATING DAILY AGENTIC DECISION REPORT")
            print("-" * 75)

            report_file = daily_reports_dir / f"daily_agent_report_{today_str}.json"
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump({
                    "date": today_str,
                    "generated_at": datetime.now().isoformat(),
                    "total_orders_analyzed": total_analyzed,
                    "delayed_orders_count": total_delayed,
                    "on_time_orders_count": total_analyzed - total_delayed,
                    "total_financial_risk_usd": total_financial_risk,
                    "total_carrier_chargebacks_usd": total_carrier_chargebacks,
                    "detailed_dossiers_retained": len(retained_decisions),
                    "decisions": retained_decisions
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
                "decisions": retained_decisions
            }

        except Exception as e:
            print(f"\n❌ Agentic cycle error: {e}")
            import traceback
            traceback.print_exc()
            self.db.session_end(session_id, status="error", error=str(e))
            raise

    def _export_csvs(self, target_date: str):
        """Export daily CSV summaries with graceful degradation"""
        try:
            w_df = self.db.read_weather(date=target_date)
            if not w_df.empty:
                w_df.to_csv(CSV_DIR / f"weather_{target_date}.csv", index=False)
            s_df = self.db.read_strikes(date=target_date)
            if not s_df.empty:
                s_df.to_csv(CSV_DIR / f"strikes_{target_date}.csv", index=False)
        except Exception as e:
            logger.debug(f"CSV export note: {e}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="O2C AI Agentic Orchestrator")
    parser.add_argument("--date", type=str, default=None, help="Target Date (YYYY-MM-DD)")
    parser.add_argument("--order", type=str, default=None, help="Single Order ID to analyze")
    parser.add_argument("--limit", type=int, default=5, help="Number of active orders to analyze")
    parser.add_argument("--all-orders", "--all", action="store_true", default=False, help="Process ALL active orders in dataset")
    parser.add_argument("--repredict", "--force-repredict", action="store_true", default=False, help="Force re-prediction of already predicted orders (default: skip already processed)")
    parser.add_argument("--rebuild-rag", action="store_true", default=False, help="Rebuild RAG index")
    parser.add_argument("--enable-teams", action="store_true", default=False, help="Enable live Microsoft Teams webhook dispatching")
    args = parser.parse_args()

    agent = AgenticOrchestrator()
    agent.run_daily_agent_cycle(
        date=args.date,
        order_limit=args.limit,
        target_order=args.order,
        all_orders=args.all_orders,
        repredict=args.repredict,
        rebuild_rag=args.rebuild_rag,
        enable_teams_dispatch=args.enable_teams
    )


if __name__ == "__main__":
    main()
