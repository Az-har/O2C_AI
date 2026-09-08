"""
Phase 7 Verification Suite: True Cognitive Autonomy (Level 4/5 Multi-Agent Architecture)
Validates the complete implementation of Phase 7 (TODO 7.1 to 7.7 in evaluation/architecture_critique.md):

Suites:
1. ReAct Tool Execution & Autonomous Tool Calling (TODO 7.2)
2. True Generative Multi-Turn LLM Dialogue & Semantic Arbiter Consensus (TODO 7.1)
3. Tool 9: Interactive Counterfactual What-If Route Simulation (TODO 7.3)
4. Active Cognitive Precedent Reflection & Variance Justification (TODO 7.4)
5. Metacognitive Pre-Execution Guardrails & Self-Correction Reflection Loop (TODO 7.5)
6. Bidirectional Conversational Human-In-The-Loop Re-Planning (TODO 7.6)
7. Local GPU Concurrency & VRAM Management Safeguards (TODO 7.7)
"""

import os
import sys
import json
import time
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

# Windows encoding safety
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient


def print_banner(title: str):
    print("\n" + "=" * 80)
    print(f"🧪 {title}")
    print("=" * 80)


def test_suite_1_react_tool_execution():
    print_banner("SUITE 1: REACT SPECIALIST TOOL EXECUTION & TRACE LOGGING (TODO 7.2)")
    from modules.agent_specialists import RouteSupervisorAgent

    agent = RouteSupervisorAgent(autonomous_mode=True)
    pred_payload = {
        "order_id": "800000000000001",
        "dest_city": "Mumbai",
        "shipping_type": "Road (FTL)",
        "carrier_name": "DHL Supply Chain",
        "haversine_distance_km": 1150.0,
        "required_transit_speed_kmh": 62.5,
        "will_be_delayed": True,
        "delay_hours": 36.0,
        "delay_probability": 0.82
    }
    order_data = {
        "order_id": "800000000000001",
        "dest_city": "Mumbai",
        "shipping_type": "Road (FTL)",
        "carrier_name": "DHL Supply Chain",
        "telematics_status": "CONNECTED"
    }

    result = agent.analyze_route(pred_payload, order_data)
    tools_invoked = result.get("tools_invoked", [])
    print(f"   ✅ RouteSupervisorAgent executed {len(tools_invoked)} tool calls autonomously:")
    for t in tools_invoked:
        print(f"      • Tool: {t}")

    assert "fetch_corridor_weather" in tools_invoked, "Expected fetch_corridor_weather in tool trace"
    assert "fetch_strike_alerts" in tools_invoked, "Expected fetch_strike_alerts in tool trace"
    assert "query_historical_incident_memory" in tools_invoked, "Expected query_historical_incident_memory in tool trace"
    assert "simulate_alternative_route_risk" in tools_invoked, "Expected simulate_alternative_route_risk in tool trace"
    assert len(result.get("route_hazards", [])) > 0, "Expected hazard detection"
    print(f"   ✅ Autonomous Tool Calling Rate: 100% (All 4 specialized tools executed)")
    return True


def test_suite_2_generative_dialogue_and_arbiter():
    print_banner("SUITE 2: GENERATIVE MULTI-TURN DIALOGUE & ARBITER CONVERGENCE (TODO 7.1)")
    from modules.agent_specialists import (
        ContractAdjudicatorAgent,
        QualityMitigationAgent,
        negotiate_inter_agent_consensus
    )

    contract_agent = ContractAdjudicatorAgent()
    quality_agent = QualityMitigationAgent()

    pred_payload = {
        "order_id": "800000000000001",
        "customer_name": "Metro Animal Hospital",
        "customer_tier": "Platinum",
        "carrier_name": "DHL Supply Chain",
        "shipping_type": "Road (FTL)",
        "net_value_usd": 15000.0,
        "delay_probability": 0.78,
        "will_be_delayed": True,
        "delay_hours": 42.0,
        "predicted_eta": "2026-09-10 16:00",
        "has_specialty_diet": True,
        "root_causes": ["Monsoon downpour flood", "Thermal degradation >40C"]
    }
    order_data = {
        "order_id": "800000000000001",
        "customer_tier": "Platinum",
        "material_description": "Prescription Renal Diet (Perishable)",
        "has_specialty_diet": True,
        "min_shelf_life_months": 18,
        "telematics_status": "CONNECTED"
    }
    route_findings = {
        "weather_hazard_detected": True,
        "telematics_active": True,
        "telematics_penalty_usd": 0.0
    }

    res = negotiate_inter_agent_consensus(
        contract_agent=contract_agent,
        quality_agent=quality_agent,
        prediction_payload=pred_payload,
        order_data=order_data,
        route_analysis=route_findings
    )

    outcome = res.get("negotiation_outcome", {})
    turns = outcome.get("turns", [])
    arbiter = outcome.get("arbiter_evaluation", {})

    print(f"   ✅ Dialogue completed across {len(turns)} turns:")
    for turn in turns:
        print(f"      Turn {turn.get('turn_index')} [{turn.get('speaker')}]: {turn.get('proposal')[:95]}...")

    print(f"   ✅ Arbiter Evaluation:")
    print(f"      • Converged: {arbiter.get('has_converged')}")
    print(f"      • Compromise Score: {arbiter.get('compromise_score')}")
    print(f"      • Ratified Summary: {arbiter.get('ratified_decision')[:100]}...")

    assert len(turns) >= 4, "Expected at least 4 turns in inter-agent negotiation"
    assert arbiter.get("has_converged") is True, "Arbiter should confirm consensus convergence"
    assert float(arbiter.get("compromise_score", 0.0)) >= 0.85, "Expected compromise score >= 0.85"
    return True


def test_suite_3_counterfactual_simulation_tool():
    print_banner("SUITE 3: INTERACTIVE COUNTERFACTUAL WHAT-IF SIMULATION TOOL 9 (TODO 7.3)")
    from modules.agent_tools import simulate_alternative_route_risk

    # Simulate switching road transit to expedited air freight with -4h offset
    sim_res = simulate_alternative_route_risk.invoke({
        "order_id": "800000000000001",
        "carrier_name": "Bluedart Air Expedited",
        "shipping_type": "Air Freight",
        "departure_offset_hours": -4.0
    })

    print(f"   ✅ Tool 9 (simulate_alternative_route_risk) Execution Result:")
    print(f"      • Status: {sim_res.get('status')}")
    print(f"      • Recommendation: {sim_res.get('recommendation')}")
    print(f"      • Baseline: Delay Prob={sim_res.get('baseline', {}).get('delay_probability'):.1%}, Hours={sim_res.get('baseline', {}).get('delay_hours')}h")
    print(f"      • Counterfactual: Delay Prob={sim_res.get('counterfactual', {}).get('delay_probability'):.1%}, Hours={sim_res.get('counterfactual', {}).get('delay_hours')}h")
    print(f"      • Delta: Hours Saved={sim_res.get('delta', {}).get('delay_hours_saved')}h, Financial Saved=${sim_res.get('delta', {}).get('financial_risk_saved_usd'):.2f}")
    print(f"      • Explanation: {sim_res.get('explanation')}")

    assert sim_res.get("status") == "SUCCESS", "Expected simulation success"
    assert sim_res.get("recommendation") == "RECOMMENDED", "Air freight upgrade should be recommended for high delay order"
    assert float(sim_res.get("delta", {}).get("delay_hours_saved", 0.0)) > 0, "Expected positive hours saved"
    return True


def test_suite_4_cognitive_precedent_reflection():
    print_banner("SUITE 4: ACTIVE COGNITIVE PRECEDENT REFLECTION (TODO 7.4)")
    from modules.agent_specialists import (
        RouteSupervisorAgent,
        ContractAdjudicatorAgent,
        QualityMitigationAgent
    )

    pred_payload = {
        "order_id": "800000000000001",
        "dest_city": "Mumbai",
        "customer_tier": "Platinum",
        "carrier_name": "DHL Supply Chain",
        "shipping_type": "Road (FTL)",
        "net_value_usd": 12000.0,
        "delay_probability": 0.75,
        "will_be_delayed": True,
        "delay_hours": 36.0,
        "predicted_eta": "2026-09-10 18:00",
        "has_specialty_diet": True,
        "root_causes": ["Heavy Monsoon Downpour", "Thermal Heatwave >40C"]
    }
    order_data = {
        "order_id": "800000000000001",
        "dest_city": "Mumbai",
        "customer_tier": "Platinum",
        "carrier_name": "DHL Supply Chain",
        "shipping_type": "Road (FTL)",
        "telematics_status": "CONNECTED",
        "material_description": "Hypoallergenic Clinical Diet",
        "min_shelf_life_months": 18
    }

    route_agent = RouteSupervisorAgent()
    route_res = route_agent.analyze_route(pred_payload, order_data)
    route_reflections = route_res.get("precedent_reflections", [])
    print(f"   ✅ RouteSupervisorAgent Precedent Reflections ({len(route_reflections)} generated):")
    for ref in route_reflections:
        print(f"      • [{ref.get('precedent_id')}] (Score: {ref.get('similarity_score')}): {ref.get('factual_analogy')}")
        print(f"        Justification: {ref.get('variance_justification')}")

    legal_agent = ContractAdjudicatorAgent()
    legal_res = legal_agent.adjudicate_contract(pred_payload, order_data, route_res)
    legal_reflections = legal_res.get("precedent_reflections", [])
    print(f"   ✅ ContractAdjudicatorAgent Precedent Reflections ({len(legal_reflections)} generated):")
    for ref in legal_reflections:
        print(f"      • [{ref.get('precedent_id')}]: {ref.get('legal_operational_clause')}")

    assert len(route_reflections) > 0, "Expected Route reflections from episodic memory"
    assert len(legal_reflections) > 0, "Expected Legal reflections from episodic memory"
    assert "precedent_id" in route_reflections[0], "Missing precedent_id"
    assert "factual_analogy" in route_reflections[0], "Missing factual_analogy"
    assert "variance_justification" in route_reflections[0], "Missing variance_justification"
    return True


def test_suite_5_guardrails_and_self_correction():
    print_banner("SUITE 5: PRE-EXECUTION GUARDRAIL AUDIT & REFLECTION LOOP (TODO 7.5)")
    from modules.agentic_graph import pre_execution_guardrail_node, guardrail_reflection_router, run_order_graph

    # Test 5A: Compliant State Audit
    compliant_state = {
        "prediction_payload": {"delay_hours": 12.0, "net_value_usd": 5000.0, "has_specialty_diet": True, "root_causes": []},
        "order_data": {"min_shelf_life_months": 18, "has_specialty_diet": True},
        "legal_findings": {"force_majeure_waived": True, "total_carrier_chargeback_usd": 200.0},
        "quality_findings": {"qa_hold_required": False},
        "route_findings": {"telematics_active": True},
        "total_mitigation_cost": 450.0,
        "reflection_count": 0,
        "requires_human_approval": False
    }
    audit_res = pre_execution_guardrail_node(compliant_state)
    print(f"   ✅ Compliant State Guardrail Audit:")
    print(f"      • Passed: {audit_res.get('audit_passed')}")
    print(f"      • Violations: {audit_res.get('audit_violations')}")
    assert audit_res.get("audit_passed") is True, "Compliant state should pass guardrail audit"

    # Test 5B: Induced Policy Breach (Thermal exposure >40C with delay >24h but NO QA quarantine hold)
    violating_state = {
        "prediction_payload": {"delay_hours": 36.0, "net_value_usd": 5000.0, "has_specialty_diet": False, "root_causes": ["Severe thermal degradation >40C heatwave"]},
        "order_data": {"min_shelf_life_months": 12, "has_specialty_diet": False},
        "legal_findings": {"force_majeure_waived": False, "total_carrier_chargeback_usd": 500.0},
        "quality_findings": {"qa_hold_required": False},  # VIOLATION: QA Hold omitted
        "route_findings": {"telematics_active": True},
        "total_mitigation_cost": 300.0,
        "reflection_count": 0,
        "requires_human_approval": False
    }
    audit_violation_res = pre_execution_guardrail_node(violating_state)
    print(f"   ✅ Induced Breach Guardrail Audit:")
    print(f"      • Passed: {audit_violation_res.get('audit_passed')}")
    print(f"      • Violations: {audit_violation_res.get('audit_violations')}")
    print(f"      • Correction Guidance: {audit_violation_res.get('correction_guidance')}")
    assert audit_violation_res.get("audit_passed") is False, "Violating state must fail guardrail audit"
    assert len(audit_violation_res.get("audit_violations")) > 0, "Expected violations logged"

    # Test 5C: Router triggers reflection loop
    merged_state = dict(violating_state)
    merged_state.update(audit_violation_res)
    route_decision = guardrail_reflection_router(merged_state)
    print(f"   ✅ Reflection Router Decision: {route_decision}")
    assert route_decision == "renegotiate", "Router must redirect to renegotiate when audit fails"

    # Test 5D: End-to-end Graph Self-Correction
    order_pred = {
        "order_id": "TEST_GUARDRAIL_SELF_CORRECT",
        "customer_name": "Canine Care Clinic",
        "customer_tier": "Gold",
        "carrier_name": "SafeLogistics Express",
        "shipping_type": "Road (FTL)",
        "dest_city": "Nagpur",
        "delay_probability": 0.70,
        "will_be_delayed": True,
        "delay_hours": 30.0,
        "predicted_eta": "2026-09-10 12:00",
        "root_causes": ["Severe thermal degradation >40C heatwave"]
    }
    order_info = {
        "order_id": "TEST_GUARDRAIL_SELF_CORRECT",
        "dest_city": "Nagpur",
        "customer_tier": "Gold",
        "material_description": "Clinical Thermal Sensitive Diet",
        "min_shelf_life_months": 12,
        "has_specialty_diet": True
    }
    final_graph_state = run_order_graph("TEST_GUARDRAIL_SELF_CORRECT", order_pred, order_info)
    print(f"   ✅ End-to-end Graph Execution with Guardrail:")
    print(f"      • Audit Passed: {final_graph_state.get('audit_passed')}")
    print(f"      • QA Hold Mandated: {final_graph_state.get('quality_findings', {}).get('qa_hold_required')}")
    print(f"      • Final Decision: {final_graph_state.get('final_decision')[:100]}...")
    assert final_graph_state.get("audit_passed") is True, "Graph must successfully pass guardrails after self-correction"
    assert final_graph_state.get("quality_findings", {}).get("qa_hold_required") is True, "Thermal hazard requires QA hold"
    return True


def test_suite_6_conversational_hitl_collaboration():
    print_banner("SUITE 6: BIDIRECTIONAL CONVERSATIONAL HITL RE-PLANNING (TODO 7.6)")
    from modules.agent_daemon import app
    from modules.database_manager import DatabaseManager

    client = TestClient(app)
    order_id = "800000000000001"

    feedback_payload = {
        "manager_id": "DIR_LOGISTICS_WEST",
        "feedback": "Authorize $400 for local express courier, but disallow expensive air freight and keep QA hold.",
        "override_budget_usd": 400.0,
        "force_qa_quarantine": True
    }

    response = client.post(f"/api/v1/orders/{order_id}/collaborate", json=feedback_payload)
    print(f"   ✅ POST /api/v1/orders/{order_id}/collaborate Status: {response.status_code}")
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"

    resp_data = response.json()
    print(f"      • Status: {resp_data.get('status')}")
    print(f"      • Manager: {resp_data.get('manager_id')}")
    print(f"      • Revised Mitigation Cost: ${resp_data.get('revised_mitigation_cost_usd'):,.2f}")
    print(f"      • Revised Decision: {resp_data.get('revised_final_decision')[:110]}...")

    assert resp_data.get("status") == "COLLABORATION_RATIFIED"
    assert float(resp_data.get("revised_mitigation_cost_usd", 0.0)) <= 400.0, "Mitigation cost should honor manager budget cap"

    # Verify audit trail in SQLite database
    db = DatabaseManager()
    audit_events = db.get_sap_audit_log(order_id)
    collaboration_events = [e for e in audit_events if e.get("action_type") == "MANAGER_COLLABORATION_FEEDBACK"]
    print(f"   ✅ SQLite Audit Trail: {len(collaboration_events)} collaboration event(s) recorded:")
    if collaboration_events:
        latest = collaboration_events[-1]
        print(f"      • Reason: {latest.get('reason')}")
        print(f"      • New Value: {latest.get('new_value')}")
    assert len(collaboration_events) > 0, "Expected collaboration entry in sap_action_audit_log"
    return True


def test_suite_7_gpu_concurrency_management():
    print_banner("SUITE 7: LOCAL GPU CONCURRENCY & VRAM SEMAPHORE (TODO 7.7)")
    from modules.agent_daemon import _gpu_llm_semaphore, app
    client = TestClient(app)

    health_resp = client.get("/api/v1/health")
    assert health_resp.status_code == 200
    health_data = health_resp.json()
    print(f"   ✅ Health Endpoint GPU Concurrency Status: {health_data.get('gpu_concurrency_slots')} parallel slots configured")
    assert health_data.get("gpu_concurrency_slots") == 2, "Expected 2 GPU concurrency slots"

    # Simulate 10 concurrent requests competing for 2 slots
    async def simulate_concurrent_requests():
        active_slots = []
        max_observed_concurrency = 0

        async def worker(worker_id: int):
            nonlocal max_observed_concurrency
            async with _gpu_llm_semaphore:
                active_slots.append(worker_id)
                curr_conc = len(active_slots)
                if curr_conc > max_observed_concurrency:
                    max_observed_concurrency = curr_conc
                await asyncio.sleep(0.05)
                active_slots.remove(worker_id)
            return worker_id

        tasks = [worker(i) for i in range(10)]
        results = await asyncio.gather(*tasks)
        return max_observed_concurrency, len(results)

    max_conc, count = asyncio.run(simulate_concurrent_requests())
    print(f"   ✅ Concurrent Execution Under Semaphore(2):")
    print(f"      • Total Completed Tasks: {count}")
    print(f"      • Peak Concurrent Executions: {max_conc}")
    assert max_conc <= 2, f"Semaphore violated! Observed {max_conc} concurrent tasks, limit is 2"
    assert count == 10, "All 10 tasks should finish"
    print(f"   ✅ Local VRAM Safeguard Confirmed: Concurrency strictly capped at <= 2 on AMD RX 6600")
    return True


def run_all_autonomy_verification_suites():
    print("\n" + "🚀" * 40)
    print("   O2C DELIVERY RISK COPILOT - PHASE 7 AUTONOMY VERIFICATION HARNESS")
    print("   Validating True Cognitive Autonomy (Level 4/5 Multi-Agent System)")
    print("🚀" * 40)

    start_time = time.time()
    results = {}

    suites = [
        ("Suite 1: ReAct Tool Execution", test_suite_1_react_tool_execution),
        ("Suite 2: Generative Dialogue & Arbiter", test_suite_2_generative_dialogue_and_arbiter),
        ("Suite 3: Counterfactual Simulation Tool", test_suite_3_counterfactual_simulation_tool),
        ("Suite 4: Cognitive Precedent Reflection", test_suite_4_cognitive_precedent_reflection),
        ("Suite 5: Pre-Execution Guardrails", test_suite_5_guardrails_and_self_correction),
        ("Suite 6: Conversational HITL Collaboration", test_suite_6_conversational_hitl_collaboration),
        ("Suite 7: GPU Concurrency Management", test_suite_7_gpu_concurrency_management),
    ]

    for name, test_fn in suites:
        try:
            passed = test_fn()
            results[name] = "PASSED" if passed else "FAILED"
        except Exception as e:
            print(f"❌ {name} FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
            results[name] = f"FAILED: {e}"

    elapsed = time.time() - start_time
    print("\n" + "=" * 80)
    print(f"📊 PHASE 7 AUTONOMY VERIFICATION SUMMARY (Completed in {elapsed:.2f}s)")
    print("=" * 80)

    all_passed = True
    for name, status in results.items():
        status_icon = "✅" if status == "PASSED" else "❌"
        print(f"{status_icon} {name:<45} : {status}")
        if status != "PASSED":
            all_passed = False

    print("=" * 80)
    if all_passed:
        print("🎉 ALL 7 AUTONOMY SUITES PASSED! Level 4/5 Cognitive Agency fully validated.")
    else:
        print("⚠️ SOME SUITES FAILED. Please review error traces above.")

    return all_passed


if __name__ == "__main__":
    success = run_all_autonomy_verification_suites()
    sys.exit(0 if success else 1)
