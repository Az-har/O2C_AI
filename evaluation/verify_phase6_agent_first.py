"""
Phase 6 Architecture Critique Verification Suite (Level 4 Agent-First)
Validates the advancement of the O2C Copilot to Level 4 Autonomous Multi-Agent Architecture:
1. Long-Term Episodic Memory Store (ChromaDB + Tool 8)
2. Dynamic Supervisor Conditional Routing (Fast-Track vs Full Investigation)
3. Inter-Agent Conversational Negotiation Protocol (Multi-Turn Adversarial Consensus)
4. Event-Driven Agent Daemon REST API (FastAPI Webhooks & Adaptive Card Callback)
5. Autonomous ReAct Specialists with Memory Integration
6. End-to-End Delivery Risk Orchestration Integration
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any

# Windows encoding safety
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient


def print_banner(title: str):
    print("\n" + "=" * 80)
    print(f"🧪 {title}")
    print("=" * 80)


def test_suite_1_episodic_incident_memory():
    print_banner("SUITE 1: CHROMADB EPISODIC INCIDENT MEMORY & TOOL 8")
    from modules.incident_memory import get_incident_memory_store
    from modules.agent_tools import query_historical_incident_memory

    store = get_incident_memory_store()
    stats = store.get_collection_stats()
    print(f"   ✅ Episodic Memory Store initialized: {stats['record_count']} precedents loaded")
    assert stats["record_count"] >= 5, "Episodic memory store should have at least 5 seeded precedents"

    # Test direct semantic retrieval
    query_text = "Severe heatwave thermal degradation prescription diet"
    results = store.query_similar_incidents(query_text=query_text, top_k=2)
    print(f"   ✅ Direct ChromaDB Query returned {len(results)} precedents:")
    for r in results:
        print(f"      • [{r['order_id']}] {r['carrier_name']} | City: {r['dest_city']} | Distance: {r['relevance_distance']:.3f}")
        print(f"        Action: {r['mitigation_action'][:80]}...")
    assert len(results) > 0, "Expected at least one semantic match for heatwave incident"

    # Test Tool 8 invocation
    tool_res = query_historical_incident_memory.invoke({
        "query_text": "Monsoon flooding corridor delay penalty dispute",
        "carrier_name": "DHL Supply Chain",
        "dest_city": "Mumbai",
        "top_k": 2
    })
    print(f"   ✅ Tool 8 (query_historical_incident_memory) Execution:")
    print(f"      - Status: {tool_res.get('status')}")
    print(f"      - Matched Precedents: {tool_res.get('count')}")
    assert tool_res.get("status") == "SUCCESS", "Tool 8 query should succeed"
    assert tool_res.get("count", 0) > 0, "Tool 8 should return matching precedents"
    return True


def test_suite_2_dynamic_supervisor_routing():
    print_banner("SUITE 2: DYNAMIC SUPERVISOR ROUTING (FAST-TRACK VS INVESTIGATION)")
    from modules.agentic_graph import run_order_graph

    # Case A: On-Schedule Low-Risk Order -> FAST-TRACK PATH
    on_time_pred = {
        "order_id": "TEST_FAST_PATH_001",
        "customer_name": "Sunrise Vet Clinic",
        "customer_tier": "Standard",
        "carrier_name": "Blue Dart Express",
        "shipping_type": "Road (FTL)",
        "dest_city": "Pune",
        "delay_probability": 0.08,
        "will_be_delayed": False,
        "delay_hours": 0.0,
        "predicted_eta": "2026-09-08 11:00",
        "root_causes": []
    }
    on_time_order_data = {
        "dest_city": "Pune",
        "shipping_type": "Road (FTL)",
        "carrier_name": "Blue Dart Express",
        "customer_tier": "Standard",
        "net_value_usd": 1500.0,
        "has_specialty_diet": False,
        "min_shelf_life_months": 24,
        "material_description": "Standard Adult Canine Maintenance",
        "telematics_status": "CONNECTED",
        "close_time": "17:00"
    }

    state_fast = run_order_graph("TEST_FAST_PATH_001", on_time_pred, on_time_order_data)
    print(f"   ✅ Fast-Track Order Graph Execution:")
    print(f"      - Active Plan: {state_fast.get('active_plan')}")
    print(f"      - Requires Approval: {state_fast.get('requires_human_approval')}")
    print(f"      - Executed SAP Actions: {len(state_fast.get('executed_erp_actions', []))}")
    assert state_fast.get("active_plan") == ["FAST_TRACK_EXECUTION"], "On-time order must trigger fast-track execution"
    assert state_fast.get("requires_human_approval") is False, "Fast-track must not require human approval"

    # Case B: High-Risk Perishable Order -> FULL SPECIALIST INVESTIGATION
    urgent_pred = {
        "order_id": "TEST_URGENT_002",
        "customer_name": "Metro Veterinary Oncology",
        "customer_tier": "Platinum",
        "carrier_name": "ColdEx Logistics",
        "shipping_type": "Road (Reefer)",
        "dest_city": "Hyderabad",
        "delay_probability": 0.88,
        "will_be_delayed": True,
        "delay_hours": 52.0,
        "predicted_eta": "2026-09-10 16:00",
        "root_causes": ["Reefer temperature excursion >40°C", "Transit velocity deficit"]
    }
    urgent_order_data = {
        "dest_city": "Hyderabad",
        "shipping_type": "Road (Reefer)",
        "carrier_name": "ColdEx Logistics",
        "customer_tier": "Platinum",
        "net_value_usd": 28000.0,
        "has_specialty_diet": True,
        "min_shelf_life_months": 5,
        "material_description": "Critical Oncology Prescription Formulation",
        "telematics_status": "CONNECTED",
        "close_time": "17:00"
    }

    state_urgent = run_order_graph("TEST_URGENT_002", urgent_pred, urgent_order_data)
    print(f"   ✅ Urgent Order Graph Execution:")
    print(f"      - Active Plan: {state_urgent.get('active_plan')}")
    print(f"      - Mitigation Cost: ${state_urgent.get('total_mitigation_cost', 0):,.2f}")
    print(f"      - Requires Approval: {state_urgent.get('requires_human_approval')}")
    print(f"      - Negotiation History Turns: {len(state_urgent.get('negotiation_history', []))}")
    print(f"      - Precedents Consulted: {len(state_urgent.get('precedents_consulted', []))}")
    assert "INTER_AGENT_NEGOTIATION" in state_urgent.get("active_plan", []), "Urgent order must include inter-agent negotiation"
    assert state_urgent.get("requires_human_approval") is True, "High-risk oncology cargo must trigger approval gate"
    assert len(state_urgent.get("negotiation_history", [])) == 4, "Must complete 4-turn negotiation protocol"
    return True


def test_suite_3_inter_agent_negotiation():
    print_banner("SUITE 3: INTER-AGENT CONVERSATIONAL NEGOTIATION PROTOCOL")
    from modules.agent_specialists import (
        ContractAdjudicatorAgent,
        QualityMitigationAgent,
        negotiate_inter_agent_consensus
    )

    contract_agent = ContractAdjudicatorAgent()
    quality_agent = QualityMitigationAgent()

    prediction_payload = {
        "order_id": "TEST_NEGOTIATE_003",
        "customer_name": "Central Animal Referral Hospital",
        "customer_tier": "Platinum",
        "carrier_name": "Express Line Freight",
        "shipping_type": "Road (FTL)",
        "dest_city": "Delhi",
        "haversine_distance_km": 850.0,
        "required_transit_speed_kmh": 45.0,
        "delay_probability": 0.90,
        "will_be_delayed": True,
        "delay_hours": 60.0,
        "predicted_eta": "2026-09-10 18:00",
        "root_causes": ["Severe monsoon rain", "Extreme transit delay"]
    }
    order_data = {
        "dest_city": "Delhi",
        "carrier_name": "Express Line Freight",
        "customer_tier": "Platinum",
        "net_value_usd": 32000.0,
        "has_specialty_diet": True,
        "min_shelf_life_months": 8,
        "material_description": "Prescription Kidney Care Renal Diet",
        "telematics_status": "CONNECTED",
        "close_time": "17:00"
    }
    route_analysis = {
        "destination_city": "Delhi",
        "shipping_mode": "Road (FTL)",
        "telematics_active": True,
        "telematics_penalty_usd": 0.0,
        "weather_hazard_detected": True,
        "strike_disruptions_detected": False
    }

    res = negotiate_inter_agent_consensus(
        contract_agent=contract_agent,
        quality_agent=quality_agent,
        prediction_payload=prediction_payload,
        order_data=order_data,
        route_analysis=route_analysis,
        notice_given_12h=True
    )

    outcome = res["negotiation_outcome"]
    turns = outcome["turns"]
    print(f"   ✅ Negotiation Outcome Synthesized across {len(turns)} Turns:")
    for t in turns:
        print(f"      Turn {t['turn_index']} [{t['speaker']}]:")
        print(f"        Proposal: {t['proposal'][:90]}...")
        if t["concessions"]:
            print(f"        Concessions: {t['concessions']}")

    print(f"\n   ✅ Financial Compromise:")
    print(f"      - Agreed Mitigation Cost: ${outcome['final_mitigation_cost_usd']:,.2f}")
    print(f"      - Final SLA Penalty: ${outcome['final_sla_penalty_usd']:,.2f}")
    print(f"      - Force Majeure Invoked: {outcome['force_majeure_invoked']}")
    print(f"      - QA Hold Mandated: {outcome['qa_hold_mandated']}")
    print(f"      - Compromise Summary: {outcome['compromise_summary'][:110]}...")

    assert len(turns) == 4, "Negotiation must consist of 4 distinct debate turns"
    assert outcome["final_mitigation_cost_usd"] == 1000.0, "Air freight for critical diet must be $1,000"
    assert len(outcome["agreed_actions"]) > 0, "Agreed actions must not be empty"
    return True


def test_suite_4_fastapi_agent_daemon():
    print_banner("SUITE 4: FASTAPI AGENT DAEMON REST API ENDPOINTS")
    from modules.agent_daemon import app

    client = TestClient(app)

    # 1. Health check endpoint
    h_res = client.get("/api/v1/health")
    print(f"   ✅ GET /api/v1/health -> HTTP {h_res.status_code}")
    assert h_res.status_code == 200
    h_data = h_res.json()
    print(f"      - System Status: {h_data['status']}")
    print(f"      - ChromaDB Status: {h_data['chromadb_status']} ({h_data['chromadb_record_count']} records)")
    print(f"      - Database Status: {h_data['database_status']}")
    print(f"      - Ollama Inference: {h_data['ollama_status']}")
    assert h_data["database_status"] == "CONNECTED"
    assert "ONLINE" in h_data["chromadb_status"]

    # 2. Event ingestion endpoint (Fast-Track)
    e1_res = client.post("/api/v1/order-event", json={
        "event_type": "ORDER_CREATED",
        "order_id": "DAEMON_FAST_001",
        "prediction_payload": {
            "order_id": "DAEMON_FAST_001",
            "customer_name": "Pune Pet Clinic",
            "customer_tier": "Standard",
            "carrier_name": "FastTrack Courier",
            "delay_probability": 0.10,
            "will_be_delayed": False,
            "delay_hours": 0.0,
            "predicted_eta": "2026-09-08 12:00"
        },
        "order_data": {
            "has_specialty_diet": False,
            "material_description": "Standard Maintenance Kibble"
        }
    })
    print(f"   ✅ POST /api/v1/order-event (Fast-Track) -> HTTP {e1_res.status_code}")
    assert e1_res.status_code == 200
    e1_data = e1_res.json()
    print(f"      - Route: {e1_data['execution_route']} | Status: {e1_data['governance_status']}")
    assert e1_data["execution_route"] == "FAST_TRACK"
    assert e1_data["governance_status"] == "AUTONOMOUSLY_APPROVED"

    # 3. Event ingestion endpoint (Full Investigation & Approval Gate)
    e2_res = client.post("/api/v1/order-event", json={
        "event_type": "TELEMATICS_PING",
        "order_id": "DAEMON_URGENT_002",
        "prediction_payload": {
            "order_id": "DAEMON_URGENT_002",
            "customer_name": "Bangalore Emergency Vet",
            "customer_tier": "Platinum",
            "carrier_name": "National Roadways",
            "shipping_type": "Road (FTL)",
            "dest_city": "Bangalore",
            "delay_probability": 0.92,
            "will_be_delayed": True,
            "delay_hours": 65.0,
            "predicted_eta": "2026-09-11 18:00",
            "root_causes": ["Severe monsoon rain", "Transit velocity deficit"]
        },
        "order_data": {
            "has_specialty_diet": True,
            "material_description": "Critical Care Clinical Diet",
            "net_value_usd": 25000.0,
            "min_shelf_life_months": 4
        }
    })
    print(f"   ✅ POST /api/v1/order-event (Investigation) -> HTTP {e2_res.status_code}")
    assert e2_res.status_code == 200
    e2_data = e2_res.json()
    print(f"      - Route: {e2_data['execution_route']} | Status: {e2_data['governance_status']}")
    print(f"      - Mitigation Cost: ${e2_data['total_mitigation_cost_usd']:,.2f}")
    assert e2_data["execution_route"] == "FULL_INVESTIGATION"
    assert e2_data["governance_status"] == "DIRECTOR_APPROVAL_REQUIRED"

    # 4. Approval callback endpoint (Human-in-the-Loop)
    app_res = client.post("/api/v1/approval/DAEMON_URGENT_002", json={
        "approver_id": "dir_supply_chain_09",
        "decision": "APPROVED",
        "comments": "Emergency replacement air pallet approved from Bangalore hub.",
        "authorized_budget_usd": 1000.0
    })
    print(f"   ✅ POST /api/v1/approval/DAEMON_URGENT_002 -> HTTP {app_res.status_code}")
    assert app_res.status_code == 200
    app_data = app_res.json()
    print(f"      - Decision: {app_data['decision']} | ERP Status: {app_data['erp_writeback_status']}")
    assert app_data["decision"] == "APPROVED"
    assert app_data["erp_writeback_status"] == "SUCCESS"

    # 5. Audit trail endpoint
    aud_res = client.get("/api/v1/orders/DAEMON_URGENT_002/audit")
    print(f"   ✅ GET /api/v1/orders/DAEMON_URGENT_002/audit -> HTTP {aud_res.status_code}")
    assert aud_res.status_code == 200
    aud_data = aud_res.json()
    print(f"      - Total Recorded ERP Events: {aud_data['total_events']}")
    assert aud_data["total_events"] > 0, "Audit trail should have at least 1 event"
    return True


def test_suite_5_specialists_with_memory_precedents():
    print_banner("SUITE 5: AUTONOMOUS SPECIALISTS RETRIEVING EPISODIC PRECEDENTS")
    from modules.agent_specialists import (
        RouteSupervisorAgent,
        ContractAdjudicatorAgent,
        QualityMitigationAgent
    )

    pred = {
        "order_id": "TEST_PREC_005",
        "customer_name": "Mumbai Veterinary Hospital",
        "customer_tier": "Platinum",
        "carrier_name": "DHL Supply Chain",
        "shipping_type": "Road (FTL)",
        "dest_city": "Mumbai",
        "delay_probability": 0.85,
        "will_be_delayed": True,
        "delay_hours": 30.0,
        "predicted_eta": "2026-09-08 14:00",
        "root_causes": ["Severe monsoon rain", "Thermal extreme (>40C)"]
    }
    order_data = {
        "dest_city": "Mumbai",
        "carrier_name": "DHL Supply Chain",
        "customer_tier": "Platinum",
        "net_value_usd": 20000.0,
        "has_specialty_diet": True,
        "min_shelf_life_months": 12,
        "material_description": "Renal Clinical Formulation",
        "telematics_status": "CONNECTED",
        "close_time": "17:00"
    }

    # 1. Route Agent
    r_agent = RouteSupervisorAgent()
    r_out = r_agent.analyze_route(pred, order_data)
    print(f"   ✅ RouteSupervisorAgent Precedents Consulted: {len(r_out['precedents_consulted'])}")
    assert len(r_out["precedents_consulted"]) > 0, "Route agent must consult episodic memory"

    # 2. Contract Agent
    c_agent = ContractAdjudicatorAgent()
    c_out = c_agent.adjudicate_contract(pred, order_data, r_out, notice_given_12h=True)
    print(f"   ✅ ContractAdjudicatorAgent Precedents Consulted: {len(c_out['precedents_consulted'])}")
    assert len(c_out["precedents_consulted"]) > 0, "Contract agent must consult episodic memory"

    # 3. Quality Agent
    q_agent = QualityMitigationAgent()
    q_out = q_agent.plan_mitigation(pred, order_data, c_out)
    print(f"   ✅ QualityMitigationAgent Precedents Consulted: {len(q_out['precedents_consulted'])}")
    assert len(q_out["precedents_consulted"]) > 0, "Quality agent must consult episodic memory"
    return True


def test_suite_6_end_to_end_orchestrator_integration():
    print_banner("SUITE 6: END-TO-END MASTER ORCHESTRATOR SYNTHESIS WITH GRAPH")
    from modules.database_manager import DatabaseManager
    from modules.agentic_orchestrator import LLMSynthesizer

    db = DatabaseManager()
    synth = LLMSynthesizer(db_manager=db)

    test_pred = {
        "order_id": "800000000000001",
        "customer_name": "Thrive Pet Healthcare",
        "customer_tier": "Platinum",
        "carrier_name": "DHL Supply Chain",
        "shipping_type": "Road (FTL)",
        "dest_city": "Mumbai",
        "haversine_distance_km": 480.0,
        "required_transit_speed_kmh": 22.0,
        "delay_probability": 0.75,
        "will_be_delayed": True,
        "delay_hours": 28.0,
        "predicted_eta": "2026-09-08 16:00",
        "root_causes": ["Carrier dwell", "Light drizzle"]
    }
    test_order_data = {
        "dest_city": "Mumbai",
        "shipping_type": "Road (FTL)",
        "carrier_name": "DHL Supply Chain",
        "customer_tier": "Platinum",
        "net_value_usd": 15000.0,
        "has_specialty_diet": False,
        "min_shelf_life_months": 12,
        "material_description": "Canine Adult Diet",
        "telematics_status": "CONNECTED",
        "close_time": "17:00"
    }

    t0 = time.time()
    decision = synth.synthesize_with_graph(test_pred, test_order_data)
    elapsed = time.time() - t0

    print(f"   ✅ Synthesized Graph Decision in {elapsed:.3f} seconds:")
    print(f"      - Order: {decision['order_id']}")
    print(f"      - LangGraph State Captured: {bool(decision.get('langgraph_state'))}")
    print(f"      - Governance Checkpoint: {decision['langgraph_state'].get('governance_checkpoint')}")
    print(f"      - Executive Decision Brief Snippet:")
    brief = decision.get("executive_decision_brief", "")
    for line in brief.split("\n")[:3]:
        print(f"        > {line}")

    assert decision.get("order_id") == "800000000000001"
    assert "langgraph_state" in decision
    return True


def main():
    print("\n" + "#" * 80)
    print("🎯 PHASE 6 ARCHITECTURE CRITIQUE: LEVEL 4 AGENT-FIRST VERIFICATION SUITE")
    print("#" * 80)

    start_time = time.time()
    results = {}

    try:
        results["Suite 1 (ChromaDB Memory Store)"] = test_suite_1_episodic_incident_memory()
        results["Suite 2 (Dynamic Supervisor Router)"] = test_suite_2_dynamic_supervisor_routing()
        results["Suite 3 (Inter-Agent Negotiation)"] = test_suite_3_inter_agent_negotiation()
        results["Suite 4 (FastAPI Daemon Webhooks)"] = test_suite_4_fastapi_agent_daemon()
        results["Suite 5 (Specialists Memory Precedents)"] = test_suite_5_specialists_with_memory_precedents()
        results["Suite 6 (End-to-End Orchestration)"] = test_suite_6_end_to_end_orchestrator_integration()
    except Exception as e:
        print(f"\n❌ Test suite execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    elapsed = time.time() - start_time

    print("\n" + "=" * 80)
    print("📊 SUMMARY OF PHASE 6 VERIFICATION RESULTS")
    print("=" * 80)
    for suite, status_val in results.items():
        print(f"   {suite:<42}: {'✅ PASSED' if status_val else '❌ FAILED'}")
    print("=" * 80)
    print(f"🎉 ALL PHASE 6 LEVEL 4 AGENT-FIRST CRITIQUE GOALS SUCCESSFULLY VERIFIED in {elapsed:.2f}s!\n")


if __name__ == "__main__":
    main()
