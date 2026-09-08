"""
Event-Driven Agent Daemon API (Phase 6 / Level 4 Architecture)
FastAPI REST microservice providing webhook endpoints for ERP events,
IoT telematics telemetry, and Human-in-the-Loop approval callbacks.

Endpoints:
1. POST /api/v1/order-event       - Triggers dynamic multi-agent pipeline for new or updated orders
2. POST /api/v1/approval/{order_id} - Callback endpoint for Director approval from MS Teams cards
3. GET  /api/v1/health             - System health, ChromaDB episodic memory, & LLM status
4. GET  /api/v1/orders/{order_id}/audit - Full multi-agent audit trail and ERP write-backs
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import urllib.request
import json

from fastapi import FastAPI, HTTPException, BackgroundTasks, status
from pydantic import BaseModel, Field

# Windows encoding safety
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from modules.database_manager import DatabaseManager
from modules.incident_memory import get_incident_memory_store
from modules.agentic_graph import run_order_graph
from modules.action_execution_engine import (
    SQLiteSAPMockAdapter,
    SAPActionExecutor
)

logger = logging.getLogger("AgentDaemon")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

# Initialize FastAPI application
app = FastAPI(
    title="O2C AI Delivery Risk Copilot - Agent Daemon",
    description="Level 4 Event-Driven Autonomous Multi-Agent State Machine & Webhook API",
    version="4.0.0"
)

_daemon_start_time = time.time()


# ============================================================================
# Request & Response Schemas
# ============================================================================

class OrderEventRequest(BaseModel):
    event_type: str = Field(
        default="ORDER_CREATED",
        description="Event type: ORDER_CREATED, TELEMATICS_PING, WEATHER_ALERT, MANUAL_TRIGGER"
    )
    order_id: str = Field(description="SAP Sales Order Number (VBELN)")
    prediction_payload: Optional[Dict[str, Any]] = Field(
        default=None,
        description="ML Engine A prediction payload (delay probability, root causes, ETA)"
    )
    order_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="SAP Sales Order line-item context (tier, net value, perishable flags)"
    )
    async_mode: bool = Field(
        default=False,
        description="Whether to execute in the background and return immediately"
    )


class OrderEventResponse(BaseModel):
    status: str
    order_id: str
    execution_route: str
    governance_status: str
    approval_reason: Optional[str] = None
    final_decision: Optional[str] = None
    total_mitigation_cost_usd: float = 0.0
    executed_erp_actions: List[Dict[str, Any]] = []
    escalation_payload: Optional[Dict[str, Any]] = None
    audit_trail: List[str] = []
    negotiation_summary: Optional[str] = None
    precedents_consulted: List[Dict[str, Any]] = []


class ApprovalCallbackRequest(BaseModel):
    approver_id: str = Field(description="Identity of the approving manager (e.g. Regional Logistics Director)")
    decision: str = Field(description="Decision: APPROVED, REJECTED, or MODIFIED")
    comments: Optional[str] = Field(default="", description="Optional managerial notes or justification")
    authorized_budget_usd: Optional[float] = Field(default=None, description="Authorized emergency freight budget")


class ApprovalCallbackResponse(BaseModel):
    order_id: str
    decision: str
    status: str
    erp_writeback_status: str
    actions_executed: List[Dict[str, Any]]
    timestamp: str


class HealthCheckResponse(BaseModel):
    status: str
    uptime_seconds: float
    chromadb_status: str
    chromadb_record_count: int
    database_status: str
    ollama_status: str
    agent_pipeline_version: str
    timestamp: str


class AuditTrailResponse(BaseModel):
    order_id: str
    total_events: int
    audit_events: List[Dict[str, Any]]


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/api/v1/health", response_model=HealthCheckResponse, tags=["System Health"])
def health_check():
    """
    Returns live health of ChromaDB episodic incident memory, SQLite database,
    Ollama LLM inference daemon, and agent pipeline state.
    """
    db = DatabaseManager()
    db_status = "CONNECTED"
    try:
        with db.connection() as conn:
            conn.execute("SELECT 1").fetchone()
    except Exception as e:
        db_status = f"ERROR: {e}"

    # Check ChromaDB episodic memory
    chroma_status = "ONLINE"
    record_count = 0
    try:
        mem_store = get_incident_memory_store()
        stats = mem_store.get_collection_stats()
        record_count = stats.get("record_count", 0)
    except Exception as e:
        chroma_status = f"DEGRADED: {e}"

    # Check local Ollama daemon
    ollama_status = "OFFLINE (Resilient Deterministic Specialist Fallbacks Active)"
    try:
        req = urllib.request.Request("http://127.0.0.1:11434/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            if resp.status == 200:
                ollama_status = "ONLINE (Local GPU Inference Ready)"
    except Exception:
        pass

    overall_status = "HEALTHY" if db_status == "CONNECTED" and "ONLINE" in chroma_status else "DEGRADED"

    return HealthCheckResponse(
        status=overall_status,
        uptime_seconds=round(time.time() - _daemon_start_time, 2),
        chromadb_status=chroma_status,
        chromadb_record_count=record_count,
        database_status=db_status,
        ollama_status=ollama_status,
        agent_pipeline_version="4.0.0-level4-agent-first",
        timestamp=datetime.now().isoformat()
    )


@app.post("/api/v1/order-event", response_model=OrderEventResponse, tags=["Agent Execution"])
def handle_order_event(event: OrderEventRequest, background_tasks: BackgroundTasks):
    """
    Ingests an operational ERP order event or telematics ping and routes it through the
    Level 4 dynamic supervisor multi-agent graph.
    """
    order_id = event.order_id
    pred_payload = event.prediction_payload or {}
    order_data = event.order_data or {}

    # If payload is minimal, provide realistic fallback defaults
    if not pred_payload:
        pred_payload = {
            "order_id": order_id,
            "customer_name": order_data.get("customer_name", "Valued Healthcare Partner"),
            "customer_tier": order_data.get("customer_tier", "Standard"),
            "carrier_name": order_data.get("carrier_name", "Regional Carrier"),
            "shipping_type": order_data.get("shipping_type", "Road (FTL)"),
            "dest_city": order_data.get("dest_city", "Mumbai"),
            "delay_probability": 0.15,
            "will_be_delayed": False,
            "delay_hours": 0.0,
            "predicted_eta": datetime.now().strftime("%Y-%m-%d 14:00"),
            "root_causes": []
        }

    if event.async_mode:
        background_tasks.add_task(run_order_graph, order_id, pred_payload, order_data)
        return OrderEventResponse(
            status="QUEUED_ASYNC",
            order_id=order_id,
            execution_route="PENDING",
            governance_status="PENDING",
            final_decision="Order processing dispatched to background execution queue.",
            audit_trail=[f"[{datetime.now().strftime('%H:%M:%S')}] Event {event.event_type} queued for async execution."]
        )

    # Synchronous multi-agent graph execution
    try:
        final_state = run_order_graph(order_id, pred_payload, order_data)
    except Exception as e:
        logger.error(f"Graph execution failed for order {order_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent Graph Execution Error: {str(e)}"
        )

    active_plan = final_state.get("active_plan", [])
    is_fast_track = "FAST_TRACK_EXECUTION" in active_plan
    route_name = "FAST_TRACK" if is_fast_track else "FULL_INVESTIGATION"

    req_approval = final_state.get("requires_human_approval", False)
    gov_status = "DIRECTOR_APPROVAL_REQUIRED" if req_approval else "AUTONOMOUSLY_APPROVED"

    # Extract negotiation summary if present
    negotiation_summary = None
    neg_history = final_state.get("negotiation_history", [])
    if neg_history:
        negotiation_summary = f"Inter-agent consensus established over {len(neg_history)} dialogue turns."

    return OrderEventResponse(
        status="SUCCESS",
        order_id=order_id,
        execution_route=route_name,
        governance_status=gov_status,
        approval_reason=final_state.get("approval_reason"),
        final_decision=final_state.get("final_decision"),
        total_mitigation_cost_usd=float(final_state.get("total_mitigation_cost", 0.0)),
        executed_erp_actions=final_state.get("executed_erp_actions", []),
        escalation_payload=final_state.get("escalation_payload"),
        audit_trail=final_state.get("audit_trail", []),
        negotiation_summary=negotiation_summary,
        precedents_consulted=final_state.get("precedents_consulted", [])
    )


@app.post("/api/v1/approval/{order_id}", response_model=ApprovalCallbackResponse, tags=["Human-In-The-Loop"])
def handle_approval_callback(order_id: str, callback: ApprovalCallbackRequest):
    """
    Receives Human-in-the-Loop governance decision (e.g. from MS Teams Adaptive Card callback)
    and executes post-approval ERP writebacks in SAP.
    """
    db = DatabaseManager()
    adapter = SQLiteSAPMockAdapter(db_manager=db)
    now_iso = datetime.now().isoformat()
    executed_actions = []

    decision_norm = callback.decision.upper().strip()
    if decision_norm not in ["APPROVED", "REJECTED", "MODIFIED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid decision '{callback.decision}'. Must be APPROVED, REJECTED, or MODIFIED."
        )

    if decision_norm in ["APPROVED", "MODIFIED"]:
        budget = callback.authorized_budget_usd or 1000.0
        db.record_sap_action(
            order_id=order_id,
            action_type="DIRECTOR_MITIGATION_APPROVED",
            sap_table="SAP_BKPF",
            sap_field="DMBTR",
            previous_value="PENDING_APPROVAL",
            new_value=f"${budget:,.2f} Authorized",
            reason=f"Approved by {callback.approver_id}: {callback.comments or 'Expedited air freight confirmed'}",
            executed_at=now_iso
        )
        executed_actions.append({
            "action": "EMERGENCY_BUDGET_AUTHORIZED",
            "amount_usd": budget,
            "approver": callback.approver_id,
            "status": "SUCCESS"
        })
    else:
        db.record_sap_action(
            order_id=order_id,
            action_type="DIRECTOR_MITIGATION_REJECTED",
            sap_table="SAP_BKPF",
            sap_field="DMBTR",
            previous_value="PENDING_APPROVAL",
            new_value="REJECTED",
            reason=f"Rejected by {callback.approver_id}: {callback.comments or 'Maintain standard transit mode'}",
            executed_at=now_iso
        )
        executed_actions.append({
            "action": "MITIGATION_EXPENSE_DECLINED",
            "approver": callback.approver_id,
            "status": "SUCCESS"
        })

    return ApprovalCallbackResponse(
        order_id=order_id,
        decision=decision_norm,
        status="EXECUTED",
        erp_writeback_status="SUCCESS",
        actions_executed=executed_actions,
        timestamp=now_iso
    )


@app.get("/api/v1/orders/{order_id}/audit", response_model=AuditTrailResponse, tags=["Audit & Governance"])
def get_order_audit_trail(order_id: str):
    """
    Returns chronological multi-agent audit trail, SAP ERP write-backs,
    and governance approvals for a specific sales order.
    """
    db = DatabaseManager()
    try:
        events = db.get_sap_audit_log(order_id)
    except Exception as e:
        logger.error(f"Failed to query audit trail for order {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database query error: {str(e)}"
        )

    return AuditTrailResponse(
        order_id=order_id,
        total_events=len(events),
        audit_events=events
    )


# ============================================================================
# Daemon Standalone Entrypoint
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("AGENT_DAEMON_PORT", "8000"))
    logger.info(f"Starting O2C AI Agent Daemon on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
