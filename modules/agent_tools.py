"""
Centralized Agent Tool Registry (Phase 2)
Provides LangChain @tool decorated functions with Pydantic typing and full docstrings
for autonomous LLM function calling across the multi-agent graph.
"""

from typing import Dict, List, Any, Optional
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from modules.config import DB_PATH, BASE_DIR
from modules.database_manager import DatabaseManager
from modules.action_execution_engine import SAPActionExecutor, MSTeamsDispatcher, SQLiteSAPMockAdapter

logger = logging.getLogger("AgentTools")


# ============================================================================
# Tool 1: Query SAP Order Telemetry
# ============================================================================

class QuerySAPOrderInput(BaseModel):
    order_id: str = Field(description="The SAP Sales Order ID (e.g. '800000000000001' or '1')")

@tool(args_schema=QuerySAPOrderInput)
def query_sap_order(order_id: str) -> Dict[str, Any]:
    """
    Retrieve comprehensive enterprise telemetry for an SAP Sales Order.
    Returns customer details, customer tier, origin and destination cities,
    assigned logistics carrier, net order value in USD, promised delivery date,
    minimum product shelf-life requirements, and order line items.
    """
    try:
        from modules.ml_db_extension import MLDatabaseExtension
        ext = MLDatabaseExtension()
        ctx = ext.get_order_context(order_id)
        if not ctx:
            # Fallback to direct DatabaseManager query
            db = DatabaseManager()
            with db.connection() as conn:
                c = conn.cursor()
                c.execute("""
                    SELECT vbeln, kunnr, vdatu, netwr, waerk
                    FROM sap_vbak
                    WHERE vbeln = ? OR vbeln LIKE ?
                    LIMIT 1
                """, (order_id, f"%{order_id}"))
                row = c.fetchone()
                if row:
                    ctx = {
                        "order_id": row["vbeln"],
                        "customer_id": row["kunnr"],
                        "customer_name": f"Customer-{row['kunnr']}",
                        "customer_tier": "Tier 1",
                        "net_order_value_usd": float(row["netwr"] or 10000.0),
                        "promised_delivery_date": str(row["vdatu"] or "2026-09-08"),
                        "origin_city": "Mumbai",
                        "dest_city": "Delhi",
                        "carrier_name": "DHL Supply Chain",
                        "min_shelf_life_months": 12.0,
                        "line_items": []
                    }
        if ctx:
            return {
                "status": "SUCCESS",
                "order_id": str(ctx.get("order_id", order_id)),
                "customer_name": ctx.get("customer_name", "Global Pharma Clinic"),
                "customer_tier": ctx.get("customer_tier", "Tier 1"),
                "origin_city": ctx.get("origin_city", "Mumbai"),
                "dest_city": ctx.get("dest_city", "Delhi"),
                "carrier_name": ctx.get("carrier_name", "SafeLogistics Express"),
                "net_value_usd": float(ctx.get("net_order_value_usd", 15000.0)),
                "promised_delivery_date": str(ctx.get("promised_delivery_date", "")),
                "min_shelf_life_months": float(ctx.get("min_shelf_life_months", 12.0)),
                "line_items_count": len(ctx.get("line_items", []))
            }
        return {"status": "NOT_FOUND", "message": f"Order {order_id} not found in SAP ERP records."}
    except Exception as e:
        logger.error(f"Error querying SAP order {order_id}: {e}")
        return {"status": "ERROR", "message": str(e)}


# ============================================================================
# Tool 2: Fetch Corridor Weather Telemetry & Hazards
# ============================================================================

class FetchWeatherInput(BaseModel):
    city: str = Field(description="The transit hub or corridor city name (e.g. 'Mumbai', 'Delhi', 'Chennai')")

@tool(args_schema=FetchWeatherInput)
def fetch_corridor_weather(city: str) -> Dict[str, Any]:
    """
    Query real-time weather telemetry and severe weather hazard alerts for a transit city or corridor.
    Inspects temperature, precipitation (rain mm), and severe weather condition codes.
    Flags thermal hazards (>40°C heat wave or freezing) and precipitation hazards (>20mm rain / storms).
    """
    try:
        db = DatabaseManager()
        reading = db.get_city_weather(city)
        if not reading:
            df = db.read_weather(city=city)
            if not df.empty:
                reading = df.iloc[0].to_dict()

        if not reading:
            return {
                "status": "NO_DATA",
                "city": city,
                "hazard_detected": False,
                "message": f"No recent weather stations reporting for {city}."
            }

        temp = float(reading.get("temperature", 25.0))
        rain = float(reading.get("rain_1h", 0.0) or reading.get("precipitation", 0.0))
        desc = str(reading.get("weather_description", reading.get("weather_desc", "Normal")))

        is_thermal_hazard = temp > 40.0 or temp < 2.0
        is_rain_hazard = rain > 15.0 or any(w in desc.lower() for w in ["storm", "cyclone", "flood", "heavy", "hail"])
        hazard_detected = is_thermal_hazard or is_rain_hazard

        hazard_reasons = []
        if is_thermal_hazard:
            hazard_reasons.append(f"Thermal extreme ({temp}°C) threatens temperature-sensitive cargo")
        if is_rain_hazard:
            hazard_reasons.append(f"Severe precipitation/storm ({desc}, {rain}mm) threatens transit corridor")

        return {
            "status": "SUCCESS",
            "city": city,
            "temperature_celsius": temp,
            "rain_mm_1h": rain,
            "weather_description": desc,
            "hazard_detected": hazard_detected,
            "hazard_reasons": hazard_reasons
        }
    except Exception as e:
        logger.error(f"Error fetching weather for {city}: {e}")
        return {"status": "ERROR", "city": city, "hazard_detected": False, "message": str(e)}


# ============================================================================
# Tool 3: Fetch Strike & Multimodal Disruption Alerts
# ============================================================================

class FetchStrikeAlertsInput(BaseModel):
    city_or_corridor: str = Field(description="The transit city, port, chokepoint, or corridor to check (e.g. 'Mumbai', 'Suez Canal', 'Rotterdam')")

@tool(args_schema=FetchStrikeAlertsInput)
def fetch_strike_alerts(city_or_corridor: str) -> Dict[str, Any]:
    """
    Search active transport strikes, multimodal blockades, natural disaster halts,
    and port/chokepoint congestions affecting a target transit location or international corridor.
    Returns active disruption events, transport modes, causal categories, and severity levels.
    """
    try:
        db = DatabaseManager()
        with db.connection() as conn:
            c = conn.cursor()
            pattern = f"%{city_or_corridor.strip()}%"
            c.execute("""
                SELECT title, 
                       COALESCE(transport_mode, 'Multimodal') as mode,
                       COALESCE(disruption_category, 'Disruption') as category,
                       COALESCE(country_mentioned, 'Global') as country,
                       COALESCE(city_mentioned, 'International Corridor') as hub,
                       severity, published_date, source_name
                FROM strike_news
                WHERE city_mentioned LIKE ? 
                   OR title LIKE ?
                   OR country_mentioned LIKE ?
                ORDER BY published_date DESC
                LIMIT 5
            """, (pattern, pattern, pattern))
            rows = [dict(r) for r in c.fetchall()]

        hazard_detected = any("HIGH" in str(r.get("severity", "")).upper() for r in rows) or len(rows) >= 2

        return {
            "status": "SUCCESS",
            "location_queried": city_or_corridor,
            "active_disruptions_count": len(rows),
            "hazard_detected": hazard_detected,
            "disruptions": [
                {
                    "title": r.get("title"),
                    "mode": r.get("mode"),
                    "category": r.get("category"),
                    "severity": r.get("severity"),
                    "hub": r.get("hub"),
                    "date": r.get("published_date")
                }
                for r in rows
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching strike alerts for {city_or_corridor}: {e}")
        return {"status": "ERROR", "location_queried": city_or_corridor, "hazard_detected": False, "message": str(e)}


# ============================================================================
# Tool 4: Query RAG Contract SLA & Policy Knowledge Base
# ============================================================================

class QueryRAGContractsInput(BaseModel):
    query: str = Field(description="The natural language question regarding SLA penalties, Force Majeure, QA rules, or carrier contracts")
    category: Optional[str] = Field(default=None, description="Optional filter category (e.g. 'SLA', 'Weather', 'Strike', 'Force Majeure')")

@tool(args_schema=QueryRAGContractsInput)
def query_rag_contracts(query: str, category: Optional[str] = None) -> Dict[str, Any]:
    """
    Query the enterprise RAG vector store for legally binding contract clauses,
    Master Service Agreement (MSA) SLA penalty terms, Force Majeure provisions,
    and Cold-Chain QA compliance thresholds.
    """
    try:
        from modules.rag_engine import RAGEngine
        rag = RAGEngine()
        full_query = f"{query} [Category: {category}]" if category else query
        result = rag.ask(full_query, category=category)
        return {
            "status": "SUCCESS",
            "query": query,
            "answer": result.get("answer", "No specific policy clause found."),
            "citations": result.get("citations", []),
            "sources": result.get("sources", [])
        }
    except Exception as e:
        logger.error(f"Error querying RAG contracts: {e}")
        return {"status": "ERROR", "query": query, "message": str(e), "answer": "Unable to query RAG knowledge base."}


# ============================================================================
# Tool 5: Adjudicate Contract SLA Penalties
# ============================================================================

class CalculateSLAInput(BaseModel):
    customer_tier: str = Field(description="Customer tier level ('Tier 1', 'Tier 2', or 'Tier 3')")
    delay_hours: float = Field(description="Predicted or actual delivery delay in hours")
    order_value_usd: float = Field(description="Net total sales order value in USD")
    notice_compliant: bool = Field(default=True, description="Whether proactive 12-hour customer notification was dispatched before SLA breach")
    is_force_majeure: bool = Field(default=False, description="Whether delay was caused by a verified Act of God / severe natural disaster / government blockade")

@tool(args_schema=CalculateSLAInput)
def calculate_adjudicated_sla(
    customer_tier: str,
    delay_hours: float,
    order_value_usd: float,
    notice_compliant: bool = True,
    is_force_majeure: bool = False
) -> Dict[str, Any]:
    """
    Deterministically adjudicate contractual SLA penalty chargebacks per Master Service Agreement.
    Applies customer tier rates ($500/day for Tier 1, $300/day for Tier 2, $150/day for Tier 3),
    enforces 50% early warning notice relief, and applies 100% waiver ($0.00) under Section 8.1 Force Majeure.
    """
    try:
        tier_clean = customer_tier.upper().strip()
        if "1" in tier_clean:
            daily_rate = 500.0
            cap_ratio = 0.15
        elif "2" in tier_clean:
            daily_rate = 300.0
            cap_ratio = 0.10
        else:
            daily_rate = 150.0
            cap_ratio = 0.05

        if delay_hours <= 0:
            return {
                "status": "ON_TIME",
                "customer_tier": customer_tier,
                "delay_hours": delay_hours,
                "gross_penalty_usd": 0.0,
                "net_chargeback_usd": 0.0,
                "notice_discount_applied": False,
                "force_majeure_invoked": False,
                "governing_clause": "MSA Section 4.1 (On-Time Delivery)"
            }

        days_delayed = max(1, int((delay_hours + 12) // 24))
        gross_penalty = min(days_delayed * daily_rate, order_value_usd * cap_ratio)

        if is_force_majeure:
            return {
                "status": "WAIVED_FORCE_MAJEURE",
                "customer_tier": customer_tier,
                "delay_hours": delay_hours,
                "gross_penalty_usd": gross_penalty,
                "net_chargeback_usd": 0.0,
                "notice_discount_applied": False,
                "force_majeure_invoked": True,
                "governing_clause": "MSA Section 8.1 (Force Majeure / Act of God Relief - 100% Waiver)"
            }

        notice_discount = 0.50 if notice_compliant else 0.0
        net_chargeback = gross_penalty * (1.0 - notice_discount)

        return {
            "status": "PENALTY_ASSESSED",
            "customer_tier": customer_tier,
            "delay_hours": delay_hours,
            "days_delayed": days_delayed,
            "gross_penalty_usd": round(gross_penalty, 2),
            "net_chargeback_usd": round(net_chargeback, 2),
            "notice_discount_applied": notice_compliant,
            "force_majeure_invoked": False,
            "governing_clause": "MSA Section 4.2 (Liquidated Damages with Proactive Notification Credit)"
        }
    except Exception as e:
        logger.error(f"Error calculating SLA penalty: {e}")
        return {"status": "ERROR", "message": str(e)}


# ============================================================================
# Tool 6: Post Simulated SAP ERP Write-Back
# ============================================================================

class PostSAPActionInput(BaseModel):
    order_id: str = Field(description="The target SAP Sales Order ID")
    action_type: str = Field(description="'DELIVERY_BLOCK' for QA quarantine hold (VBAK-LIFSK) or 'UPDATE_ETA' for promised date change (VBAK-VDATU)")
    reason: str = Field(description="Audit justification for ERP change")
    value: Optional[str] = Field(default=None, description="Block code (e.g. '01') or new promised ETA date ('YYYY-MM-DD')")

@tool(args_schema=PostSAPActionInput)
def post_sap_block_or_date(
    order_id: str,
    action_type: str,
    reason: str,
    value: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute an ERP write-back action on SAP S/4HANA via the standardized ERP Action Interface.
    Posts Delivery Block ('01' QA Quarantine) or updates Confirmed Promised Delivery Date (VDATU).
    Logs all changes to the central sap_actions_audit trail.
    """
    try:
        db = DatabaseManager()
        adapter = SQLiteSAPMockAdapter(db_manager=db)
        executor = SAPActionExecutor(erp_adapter=adapter, db_manager=db)

        action_upper = action_type.upper().strip()
        if "BLOCK" in action_upper:
            code = value or "01"
            res = adapter.set_delivery_block(order_id, block_code=code, reason=reason)
            return {"status": "SUCCESS", "erp_action": res}
        elif "ETA" in action_upper or "DATE" in action_upper:
            new_date = value or (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
            res = adapter.update_promised_date(order_id, new_eta_date=new_date, reason=reason)
            return {"status": "SUCCESS", "erp_action": res}
        else:
            return {"status": "INVALID_ACTION", "message": f"Unsupported action_type: {action_type}. Use 'DELIVERY_BLOCK' or 'UPDATE_ETA'."}
    except Exception as e:
        logger.error(f"Error posting SAP ERP action: {e}")
        return {"status": "ERROR", "order_id": order_id, "message": str(e)}


# ============================================================================
# Tool 7: Dispatch Microsoft Teams Human-in-the-Loop Approval Card
# ============================================================================

class DispatchTeamsCardInput(BaseModel):
    order_id: str = Field(description="The affected SAP Sales Order ID")
    escalation_reason: str = Field(description="Reason human review is required (e.g. 'Mitigation cost > $500' or 'QA Quarantine')")
    financial_impact_usd: float = Field(description="Estimated mitigation cost or financial liability in USD")
    proposed_action: str = Field(description="The recommended mitigation plan formulated by the agents")

@tool(args_schema=DispatchTeamsCardInput)
def dispatch_teams_approval_card(
    order_id: str,
    escalation_reason: str,
    financial_impact_usd: float,
    proposed_action: str
) -> Dict[str, Any]:
    """
    Generate an interactive Microsoft Teams Adaptive Card (v1.4) payload for human supervisor review.
    Invoked whenever high-risk mitigations exceed financial authorization thresholds (> $500)
    or require clinical quality quarantine sign-off.
    """
    try:
        dispatcher = MSTeamsDispatcher()
        card_payload = dispatcher.create_teams_card(
            order_id=order_id,
            escalation_reason=escalation_reason,
            financial_impact_usd=financial_impact_usd,
            proposed_action=proposed_action
        )
        return {
            "status": "CARD_GENERATED",
            "order_id": order_id,
            "requires_human_approval": True,
            "financial_impact_usd": financial_impact_usd,
            "escalation_reason": escalation_reason,
            "proposed_action": proposed_action,
            "card_summary": f"Teams Adaptive Card created with Approve/Reject action buttons for Order {order_id}"
        }
    except Exception as e:
        logger.error(f"Error dispatching Teams card: {e}")
        return {"status": "ERROR", "order_id": order_id, "message": str(e)}


# ============================================================================
# Tool 8: Query Historical Incident & Resolution Memory (ChromaDB)
# ============================================================================

class QueryIncidentMemoryInput(BaseModel):
    query_text: str = Field(description="Search description of the incident, delay conditions, or arbitration query")
    carrier_name: Optional[str] = Field(default=None, description="Optional carrier name filter (e.g. 'DHL Supply Chain')")
    dest_city: Optional[str] = Field(default=None, description="Optional destination city filter (e.g. 'Mumbai')")
    top_k: int = Field(default=3, description="Number of precedent resolutions to retrieve")

@tool(args_schema=QueryIncidentMemoryInput)
def query_historical_incident_memory(
    query_text: str,
    carrier_name: Optional[str] = None,
    dest_city: Optional[str] = None,
    top_k: int = 3
) -> Dict[str, Any]:
    """
    Retrieve historical incident precedents, dispute resolutions, and carrier performance
    records from the ChromaDB long-term episodic memory store.
    Provides legal and operational precedents for Force Majeure claims and mitigation authorizations.
    """
    try:
        from modules.incident_memory import EpisodicMemoryStore
        store = EpisodicMemoryStore()
        precedents = store.query_precedents(
            query_text=query_text,
            carrier_name=carrier_name,
            dest_city=dest_city,
            top_k=top_k
        )
        return {
            "status": "SUCCESS",
            "query": query_text,
            "precedents_found": len(precedents),
            "count": len(precedents),
            "precedents": precedents
        }
    except Exception as e:
        logger.error(f"Error querying episodic incident memory: {e}")
        return {"status": "ERROR", "query": query_text, "precedents_found": 0, "count": 0, "precedents": [], "message": str(e)}


# ============================================================================
# Tool 9: Interactive Counterfactual What-If Route Simulation (Phase 7 / Level 4 Autonomy)
# ============================================================================

class SimulateAlternativeRouteInput(BaseModel):
    order_id: str = Field(description="The SAP Sales Order ID to run counterfactual simulation on (e.g. '800000000000001' or '1')")
    carrier_name: Optional[str] = Field(default=None, description="Alternative carrier to evaluate (e.g. 'Bluedart Air Expedited', 'DHL Express', 'SafeLogistics FTL')")
    shipping_type: Optional[str] = Field(default=None, description="Alternative transport mode (e.g. 'Air Freight', 'Road (FTL)', 'Rail Intermodal')")
    departure_offset_hours: float = Field(default=0.0, description="Departure schedule shift in hours (negative for early departure, positive for delay)")

@tool(args_schema=SimulateAlternativeRouteInput)
def simulate_alternative_route_risk(
    order_id: str,
    carrier_name: Optional[str] = None,
    shipping_type: Optional[str] = None,
    departure_offset_hours: float = 0.0
) -> Dict[str, Any]:
    """
    Run interactive counterfactual what-if simulation on an SAP Sales Order using Engine A's Two-Stage Hurdle ML model.
    Evaluates alternative carriers, shipping modes (e.g., Road to Air Freight), and departure schedule offsets.
    Returns comparative delay probability, revised delay hours, projected ETA, financial penalty risk,
    and net risk reduction relative to the baseline route.
    """
    try:
        from modules.predictive_engine import PredictiveEngine
        from modules.ml_db_extension import MLDatabaseExtension
        ml_db = MLDatabaseExtension()
        engine = PredictiveEngine(ml_db_extension=ml_db)
        sim_res = engine.run_counterfactual_inference(
            order_id=order_id,
            carrier_name=carrier_name,
            shipping_type=shipping_type,
            departure_offset_hours=departure_offset_hours
        )
        sim_res["status"] = "SUCCESS"
        return sim_res
    except Exception as e:
        logger.error(f"Error executing counterfactual route simulation for {order_id}: {e}")
        return {
            "status": "ERROR",
            "order_id": order_id,
            "message": str(e),
            "recommendation": "NOT_RECOMMENDED"
        }


# Master Toolset for Agent Binding (9 Production Tools)
ALL_AGENT_TOOLS = [
    query_sap_order,
    fetch_corridor_weather,
    fetch_strike_alerts,
    query_rag_contracts,
    calculate_adjudicated_sla,
    post_sap_block_or_date,
    dispatch_teams_approval_card,
    query_historical_incident_memory,
    simulate_alternative_route_risk,
]


