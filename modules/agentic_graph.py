"""
LangGraph Multi-Agent Orchestration State Machine (Phase 4)
Implements a collaborative, goal-driven multi-agent graph with Pydantic typing,
autonomous specialist nodes, trade-off consensus debate, and conditional governance routing:
- Safe Auto-Execution (mitigation <= $500) -> ERP Action Executor
- Human-in-the-Loop Gate (mitigation > $500 or QA Quarantine) -> MS Teams Adaptive Card Checkpoint
"""

import sys
import os
import json
import logging
from typing import Dict, List, Any, Optional, TypedDict, Annotated
import operator
from datetime import datetime
from pathlib import Path

# Windows encoding safety
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from modules.config import DB_PATH, BASE_DIR
from modules.database_manager import DatabaseManager
from modules.agent_specialists import (
    RouteSupervisorAgent,
    ContractAdjudicatorAgent,
    QualityMitigationAgent,
    LLMReasoningEngine
)
from modules.action_execution_engine import (
    SAPActionExecutor,
    MSTeamsDispatcher,
    SQLiteSAPMockAdapter
)

logger = logging.getLogger("AgenticGraph")


# ============================================================================
# Shared Multi-Agent Graph State (LangGraph Schema)
# ============================================================================

class O2CAgentState(TypedDict):
    """Immutable shared state flowing through the multi-agent graph"""
    order_id: str
    order_data: Dict[str, Any]
    prediction_payload: Dict[str, Any]
    route_findings: Dict[str, Any]
    legal_findings: Dict[str, Any]
    quality_findings: Dict[str, Any]
    proposed_actions: List[Dict[str, Any]]
    total_mitigation_cost: float
    requires_human_approval: bool
    approval_reason: str
    escalation_payload: Optional[Dict[str, Any]]
    executed_erp_actions: List[Dict[str, Any]]
    final_decision: Optional[str]
    audit_trail: Annotated[List[str], operator.add]


# ============================================================================
# Multi-Agent Node Implementations
# ============================================================================

def supervisor_router_node(state: O2CAgentState) -> Dict[str, Any]:
    """Node 1: Supervisor Router - Inspects order context and initiates multi-agent assessment"""
    order_id = state["order_id"]
    pred = state.get("prediction_payload", {})
    customer = pred.get("customer_name", "Valued Customer")
    tier = pred.get("customer_tier", "Tier 1")
    will_delay = pred.get("will_be_delayed", False)
    delay_hrs = pred.get("delay_hours", 0.0)

    log_entry = (
        f"[{datetime.now().strftime('%H:%M:%S')}] SupervisorRouter: Order {order_id} ({customer}, {tier}) "
        f"queued. Predicted status: {'DELAYED by ' + f'{delay_hrs:.1f}h' if will_delay else 'ON SCHEDULE'}."
    )
    return {
        "audit_trail": [log_entry]
    }


def route_specialist_node(state: O2CAgentState) -> Dict[str, Any]:
    """Node 2: Route & Telematics Supervisor - Evaluates weather, velocity, and transit corridor hazards"""
    agent = RouteSupervisorAgent()
    route_res = agent.analyze_route(state["prediction_payload"], state["order_data"])
    
    hazards = route_res.get("route_hazards", [])
    hazard_str = f"Hazards: {', '.join(hazards)}" if hazards else "Corridor clear"
    log_entry = (
        f"[{datetime.now().strftime('%H:%M:%S')}] RouteSupervisor: Corridor to {route_res.get('destination_city')} "
        f"analyzed. Telematics={'ACTIVE' if route_res.get('telematics_active') else 'DISCONNECTED'}. {hazard_str}."
    )
    return {
        "route_findings": route_res,
        "audit_trail": [log_entry]
    }


def contract_adjudicator_node(state: O2CAgentState) -> Dict[str, Any]:
    """Node 3: Contract & Legal Adjudicator - Applies customer SLA, notice relief, and Force Majeure"""
    agent = ContractAdjudicatorAgent()
    legal_res = agent.adjudicate_contract(
        prediction_payload=state["prediction_payload"],
        order_data=state["order_data"],
        route_analysis=state["route_findings"],
        notice_given_12h=True
    )
    
    fm_str = "Act of God Waiver Granted" if legal_res.get("force_majeure_waived") else legal_res.get("force_majeure_status")
    log_entry = (
        f"[{datetime.now().strftime('%H:%M:%S')}] ContractAdjudicator: {legal_res.get('customer_tier')} SLA. "
        f"SLA Penalty=${legal_res.get('sla_delay_penalty_usd', 0):.2f}. Force Majeure={fm_str}."
    )
    return {
        "legal_findings": legal_res,
        "audit_trail": [log_entry]
    }


def quality_mitigation_node(state: O2CAgentState) -> Dict[str, Any]:
    """Node 4: Quality & Cold-Chain Mitigation Planner - Evaluates perishable shelf-life & air freight"""
    agent = QualityMitigationAgent()
    qa_res = agent.plan_mitigation(
        prediction_payload=state["prediction_payload"],
        order_data=state["order_data"],
        contract_analysis=state["legal_findings"]
    )
    
    cost = qa_res.get("total_mitigation_cost_usd", 0.0)
    qa_hold = qa_res.get("qa_hold_required", False)
    log_entry = (
        f"[{datetime.now().strftime('%H:%M:%S')}] QualityMitigation: Evaluated {qa_res.get('material_description')}. "
        f"Mitigation Cost=${cost:,.2f}. QA Hold={qa_hold}."
    )
    return {
        "quality_findings": qa_res,
        "total_mitigation_cost": cost,
        "audit_trail": [log_entry]
    }


def consensus_debate_node(state: O2CAgentState) -> Dict[str, Any]:
    """
    Node 5: Multi-Agent Consensus & Trade-Off Debate Node
    Balances Contract SLA liabilities, Air Freight costs, and Quality holds
    to synthesize a unified executive brief and determine governance routing.
    """
    reasoner = LLMReasoningEngine()
    pred = state["prediction_payload"]
    route = state["route_findings"]
    legal = state["legal_findings"]
    quality = state["quality_findings"]
    cost = state["total_mitigation_cost"]
    qa_hold = quality.get("qa_hold_required", False)

    # Synthesize unified executive decision
    brief = reasoner.synthesize_executive_decision(
        order_id=state["order_id"],
        customer_name=pred.get("customer_name", "Valued Customer"),
        customer_tier=legal.get("customer_tier", "Tier 1"),
        carrier_name=pred.get("carrier_name", "Carrier"),
        shipping_type=route.get("shipping_mode", "Road (FTL)"),
        delay_prob=pred.get("delay_probability", 0.0),
        will_delay=pred.get("will_be_delayed", False),
        delay_hours=pred.get("delay_hours", 0.0),
        predicted_eta=pred.get("predicted_eta", ""),
        route_analysis=route,
        contract_analysis=legal,
        quality_analysis=quality,
        rag_citations=pred.get("rag_citations", ["Master Service Agreement"])
    )

    # Governance Gate Check: Expense > $500 or QA Quarantine requires Director sign-off
    requires_approval = (cost > 500.0) or qa_hold or (legal.get("sla_delay_penalty_usd", 0.0) > 1000.0)
    approval_reason = ""
    if cost > 500.0:
        approval_reason = f"Emergency freight upgrade expense (${cost:,.2f}) exceeds $500 threshold"
    elif qa_hold:
        approval_reason = f"Clinical quality quarantine hold required: {'; '.join(quality.get('qa_hold_reasons', []))}"
    elif legal.get("sla_delay_penalty_usd", 0.0) > 1000.0:
        approval_reason = f"Contract SLA late liability (${legal.get('sla_delay_penalty_usd'):,.2f}) exceeds $1,000 threshold"

    log_entry = (
        f"[{datetime.now().strftime('%H:%M:%S')}] ConsensusDebate: Decision synthesized. "
        f"Approval Required={requires_approval} ({approval_reason or 'Auto-Approved'})."
    )

    return {
        "final_decision": brief,
        "requires_human_approval": requires_approval,
        "approval_reason": approval_reason,
        "audit_trail": [log_entry]
    }


def action_execution_node(state: O2CAgentState) -> Dict[str, Any]:
    """Node 6A: Safe Auto-Execution Node - Executes simulated ERP write-backs (Expense <= $500)"""
    db = DatabaseManager()
    adapter = SQLiteSAPMockAdapter(db_manager=db)
    executor = SAPActionExecutor(erp_adapter=adapter, db_manager=db)
    
    order_id = state["order_id"]
    pred = state["prediction_payload"]
    quality = state["quality_findings"]
    legal = state["legal_findings"]

    actions = executor.execute_sap_writebacks(
        order_id=order_id,
        predicted_eta=pred.get("predicted_eta", ""),
        qa_hold_required=quality.get("qa_hold_required", False),
        qa_reasons=quality.get("qa_hold_reasons", []),
        carrier_chargeback_usd=legal.get("total_carrier_chargeback_usd", 0.0),
        carrier_name=pred.get("carrier_name", "Unknown Carrier"),
        penalty_clauses=legal.get("penalty_clauses", [])
    )

    log_entry = (
        f"[{datetime.now().strftime('%H:%M:%S')}] ActionExecutor: Executed {len(actions)} SAP ERP write-backs "
        f"(Delivery Block, Confirmed ETA, Carrier Chargeback)."
    )
    return {
        "executed_erp_actions": actions,
        "audit_trail": [log_entry]
    }


def human_approval_checkpoint(state: O2CAgentState) -> Dict[str, Any]:
    """Node 6B: Human-in-the-Loop Checkpoint - Formats MS Teams Adaptive Card (Expense > $500)"""
    order_id = state["order_id"]
    cost = state["total_mitigation_cost"]
    reason = state["approval_reason"]
    actions = state["quality_findings"].get("mitigation_actions", ["Authorize expedited freight"])
    
    dispatcher = MSTeamsDispatcher()
    card_res = dispatcher.dispatch_card({
        "order_id": order_id,
        "customer": state["prediction_payload"].get("customer_name", "Clinic"),
        "carrier": state["prediction_payload"].get("carrier_name", "Carrier"),
        "mitigation_expense_usd": cost,
        "recommended_action": actions[0] if actions else "Review mitigation plan",
        "urgency": "CRITICAL" if cost > 1000.0 or state["quality_findings"].get("qa_hold_required") else "HIGH",
        "sla_response_hours": 2.0
    })

    log_entry = (
        f"[{datetime.now().strftime('%H:%M:%S')}] HumanApprovalCheckpoint: MS Teams Adaptive Card generated "
        f"for Regional Director review. Escalation: {reason}."
    )
    return {
        "escalation_payload": card_res,
        "audit_trail": [log_entry]
    }


# ============================================================================
# Conditional Edge Router
# ============================================================================

def route_by_governance(state: O2CAgentState) -> str:
    """Routes state based on financial and clinical risk thresholds"""
    if state.get("requires_human_approval", False):
        return "human_approval_checkpoint"
    return "action_execution_node"


# ============================================================================
# Graph Builder & Compilation
# ============================================================================

def create_o2c_agentic_graph() -> StateGraph:
    """Build the LangGraph multi-agent state machine"""
    workflow = StateGraph(O2CAgentState)

    # 1. Add Nodes
    workflow.add_node("supervisor_router", supervisor_router_node)
    workflow.add_node("route_specialist", route_specialist_node)
    workflow.add_node("contract_adjudicator", contract_adjudicator_node)
    workflow.add_node("quality_mitigation", quality_mitigation_node)
    workflow.add_node("consensus_debate", consensus_debate_node)
    workflow.add_node("action_execution_node", action_execution_node)
    workflow.add_node("human_approval_checkpoint", human_approval_checkpoint)

    # 2. Add Deterministic Sequence Edges
    workflow.add_edge(START, "supervisor_router")
    workflow.add_edge("supervisor_router", "route_specialist")
    workflow.add_edge("route_specialist", "contract_adjudicator")
    workflow.add_edge("contract_adjudicator", "quality_mitigation")
    workflow.add_edge("quality_mitigation", "consensus_debate")

    # 3. Add Conditional Edge for Governance Gate
    workflow.add_conditional_edges(
        "consensus_debate",
        route_by_governance,
        {
            "action_execution_node": "action_execution_node",
            "human_approval_checkpoint": "human_approval_checkpoint"
        }
    )

    # 4. Terminal Edges
    workflow.add_edge("action_execution_node", END)
    workflow.add_edge("human_approval_checkpoint", END)

    return workflow


# Compiled LangGraph instance with thread-safe memory checkpointer
_memory_saver = MemorySaver()
compiled_o2c_graph = create_o2c_agentic_graph().compile(checkpointer=_memory_saver)


def run_order_graph(
    order_id: str,
    prediction_payload: Dict[str, Any],
    order_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Execute the compiled LangGraph multi-agent workflow for a single sales order.
    Returns the complete terminal state including specialist findings, executive brief,
    and governance action results.
    """
    initial_state: O2CAgentState = {
        "order_id": str(order_id),
        "order_data": order_data or {},
        "prediction_payload": prediction_payload,
        "route_findings": {},
        "legal_findings": {},
        "quality_findings": {},
        "proposed_actions": [],
        "total_mitigation_cost": 0.0,
        "requires_human_approval": False,
        "approval_reason": "",
        "escalation_payload": None,
        "executed_erp_actions": [],
        "final_decision": None,
        "audit_trail": [f"[{datetime.now().strftime('%H:%M:%S')}] Workflow initialized for Order {order_id}"]
    }

    config = {"configurable": {"thread_id": f"order_{order_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"}}
    final_state = compiled_o2c_graph.invoke(initial_state, config=config)
    return final_state
