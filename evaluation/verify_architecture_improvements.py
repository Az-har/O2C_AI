"""
Verification Suite for 8 Strategic Architectural Improvements (Production Roadmap)
Covers Improvements 5.1 through 5.8 from evaluation/architecture_critique.md.

Tests:
1. Improvement 5.1: Unified Graph-Native Orchestration Engine
2. Improvement 5.2: Polystore Architecture (DuckDB Columnar OLAP Engine)
3. Improvement 5.3: Zero-Churn Direct Markdown Knowledge Base Generation
4. Improvement 5.4: Hierarchical Multi-Tier Working Blackboard Memory
5. Improvement 5.5: Local OpenTelemetry / OpenInference Tracing Harness
6. Improvement 5.6: Transactional Outbox & Two-Phase Idempotent ERP Adapter
7. Improvement 5.7: Reactive Event-Driven Streaming Worker Daemon Endpoints
8. Improvement 5.8: Token-Efficient ReWOO Specialist Execution Topology
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime

# Windows encoding safety
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def print_banner(title: str):
    print("\n" + "=" * 80)
    print(f"🚀 {title}")
    print("=" * 80)


def test_1_unified_graph_orchestrator():
    print_banner("TEST 1: UNIFIED GRAPH-NATIVE ORCHESTRATION (IMPROVEMENT 5.1)")
    from modules.agentic_orchestrator import AgenticOrchestrator, LLMSynthesizer
    import inspect

    # 1. Inspect default parameter in run_daily_agent_cycle
    sig = inspect.signature(AgenticOrchestrator.run_daily_agent_cycle)
    default_graph = sig.parameters["use_agent_graph"].default
    assert default_graph is True, f"Expected use_agent_graph default True, got {default_graph}"
    print(f"   ✅ AgenticOrchestrator.run_daily_agent_cycle defaults to use_agent_graph={default_graph}")

    # 2. Test synthesize_with_graph produces langgraph_state metadata
    synth = LLMSynthesizer()
    pred_payload = {
        "order_id": "TEST_UNIFIED_001",
        "customer_name": "Metro Clinic",
        "customer_tier": "Gold",
        "carrier_name": "SafeLogistics FTL",
        "shipping_type": "Road (FTL)",
        "dest_city": "Delhi",
        "delay_probability": 0.20,
        "will_be_delayed": False,
        "delay_hours": 0.0,
        "predicted_eta": "2026-09-12 10:00"
    }
    decision = synth.synthesize_with_graph(pred_payload, order_data={"dest_city": "Delhi"})
    assert "langgraph_state" in decision, "Expected 'langgraph_state' in decision"
    assert "governance_checkpoint" in decision["langgraph_state"]
    print(f"   ✅ LangGraph unified synthesis succeeded for {decision['order_id']}:")
    print(f"      - Checkpoint: {decision['langgraph_state']['governance_checkpoint']}")
    print(f"      - Requires Approval: {decision['langgraph_state']['requires_human_approval']}")


def test_2_duckdb_polystore_olap():
    print_banner("TEST 2: POLYSTORE ARCHITECTURE (DUCKDB OLAP - IMPROVEMENT 5.2)")
    from modules.analytical_feature_store import AnalyticalFeatureStore

    t0 = time.time()
    store = AnalyticalFeatureStore()
    df = store.get_ml_ready_dataset()
    load_time = time.time() - t0

    assert not df.empty, "DuckDB OLAP dataset is empty!"
    assert len(df) >= 60000, f"Expected >= 60,000 rows, got {len(df)}"
    assert "haversine_distance_km" in df.columns
    assert "required_transit_speed_kmh" in df.columns
    assert "is_delayed" in df.columns
    assert "delay_hours" in df.columns
    print(f"   ✅ DuckDB Analytical Join: {len(df):,} rows x {len(df.columns)} cols loaded in {load_time:.3f}s")
    assert load_time < 3.0, f"DuckDB join took too long: {load_time:.2f}s"

    sample_id = str(df["order_id"].iloc[0])
    details = store.get_order_details(sample_id)
    assert details is not None, f"Could not lookup details for order {sample_id}"
    print(f"   ✅ O(1) Order Detail Lookup: Order {sample_id} -> City: {details.get('dest_city')}, Tier: {details.get('customer_tier')}")


def test_3_zero_churn_markdown_kb():
    print_banner("TEST 3: ZERO-CHURN DIRECT MARKDOWN KNOWLEDGE BASE (IMPROVEMENT 5.3)")
    from modules.weather_policy_generator import WeatherPolicyGenerator
    from modules.strike_intelligence_generator import StrikeIntelligenceGenerator

    # 1. Weather Policy Markdown
    w_gen = WeatherPolicyGenerator()
    dummy_alerts = [{"city": "Mumbai", "temp_c": 43.5, "wind_ms": 18.0, "rain_mm": 5.0, "visibility_km": 0.8, "description": "Extreme Heatwave"}]
    w_md = w_gen._create_city_weather_policy_md("Mumbai", dummy_alerts)
    assert w_md.exists(), f"Expected markdown file {w_md} to exist"
    content = w_md.read_text(encoding="utf-8")
    assert "[RULE-W-MUM-01]" in content
    assert "[RULE-W-MUM-02]" in content
    print(f"   ✅ Weather Policy Markdown Generated: {w_md.name} ({len(content)} bytes)")

    # 2. Strike Intelligence Markdown
    s_gen = StrikeIntelligenceGenerator()
    dummy_articles = [{"title": "Highway Transport Blockade", "transport_mode": "Road (FTL)", "severity": "HIGH", "published": "2026-09-10"}]
    s_md = s_gen._create_city_strike_brief_md("Delhi", dummy_articles)
    assert s_md.exists(), f"Expected markdown file {s_md} to exist"
    s_content = s_md.read_text(encoding="utf-8")
    assert "[RULE-S-DEL-01]" in s_content
    print(f"   ✅ Strike Intelligence Markdown Generated: {s_md.name} ({len(s_content)} bytes)")


def test_4_blackboard_memory():
    print_banner("TEST 4: HIERARCHICAL MULTI-TIER WORKING BLACKBOARD MEMORY (IMPROVEMENT 5.4)")
    from modules.blackboard_memory import BlackboardMemory, get_blackboard_memory
    import concurrent.futures

    bb = get_blackboard_memory()
    bb.clear()

    # Publish corridor hazard
    bb.publish_corridor_hazard("Pune", {
        "hazard_type": "LANDSLIDE_BLOCKAGE",
        "corridor": "NH-48",
        "severity": "CRITICAL",
        "summary": "Landslide on NH-48 Ghat section; lane closed"
    })

    # Retrieve and verify
    h = bb.get_corridor_hazard("pune")
    assert h is not None, "Corridor hazard lookup returned None"
    assert h["hazard_details"]["hazard_type"] == "LANDSLIDE_BLOCKAGE"
    print(f"   ✅ Published and Retrieved Corridor Hazard on Pune: {h['hazard_details']['summary']}")

    # Test concurrent multi-thread publishing
    def _pub(city_name):
        bb.publish_corridor_hazard(city_name, {"summary": f"Hazard in {city_name}"})

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(_pub, ["Mumbai", "Chennai", "Delhi", "Bangalore"]))

    all_hazards = bb.get_all_hazards()
    assert len(all_hazards) >= 5, f"Expected >= 5 hazards in blackboard, found {len(all_hazards)}"
    print(f"   ✅ Concurrent Multi-Thread Blackboard Access Verified: {len(all_hazards)} corridors registered")


def test_5_telemetry_tracing():
    print_banner("TEST 5: LOCAL OPENTELEMETRY / OPENINFERENCE TRACING (IMPROVEMENT 5.5)")
    from modules.telemetry import trace_span, trace_agent_action, get_recent_traces

    # 1. Test generic span
    with trace_span("test_pipeline_span", {"test_key": "val123"}) as span:
        time.sleep(0.01)

    # 2. Test agent action trace
    with trace_agent_action("ContractAdjudicator", "ORDER_TEL_001", action_type="adjudication"):
        time.sleep(0.01)

    traces = get_recent_traces(limit=10)
    assert len(traces) >= 2, f"Expected >= 2 traces, got {len(traces)}"
    names = [t.get("span_name") for t in traces]
    assert "test_pipeline_span" in names
    assert "ContractAdjudicator.adjudication" in names
    print(f"   ✅ OpenTelemetry Spans Recorded Successfully:")
    for t in traces[-2:]:
        print(f"      • Span: {t.get('span_name')} | Status: {t.get('status')} | Duration: {t.get('duration_ms')}ms")


def test_6_transactional_outbox():
    print_banner("TEST 6: TRANSACTIONAL OUTBOX & 2-PHASE ERP ADAPTER (IMPROVEMENT 5.6)")
    from modules.action_execution_engine import (
        TransactionalOutboxManager,
        SQLiteSAPMockAdapter,
        SAPActionExecutor
    )

    outbox = TransactionalOutboxManager()
    order_id = f"TEST_OUTBOX_{int(time.time())}"

    # 1. Enqueue an action
    row_id = outbox.enqueue_action(
        order_id=order_id,
        action_type="SET_DELIVERY_BLOCK",
        payload={"block_code": "01", "reason": "Test Outbox Hold"},
        idempotency_key=f"{order_id}_HOLD"
    )
    print(f"   ✅ Action Enqueued into erp_outbox_actions (ID: {row_id})")

    # 2. Retrieve pending
    pending = outbox.get_pending_actions()
    target_pending = [p for p in pending if p["order_id"] == order_id]
    assert len(target_pending) >= 1, "Expected pending outbox action not found"
    print(f"   ✅ Retrieved {len(pending)} pending outbox action(s)")

    # 3. Dispatch pending with mock adapter
    mock_adapter = SQLiteSAPMockAdapter()
    dispatch_res = outbox.dispatch_pending_actions(mock_adapter)
    assert dispatch_res["successful"] >= 1, "Outbox dispatch did not report success"
    print(f"   ✅ Outbox Dispatch Complete: {dispatch_res['successful']} dispatched, {dispatch_res['failed']} failed")

    # 4. Test SAPActionExecutor with use_outbox=True
    executor = SAPActionExecutor()
    actions = executor.execute_sap_writebacks(
        order_id=order_id,
        predicted_eta="2026-09-15 12:00",
        qa_hold_required=True,
        qa_reasons=["Perishable stability hold"],
        carrier_chargeback_usd=500.0,
        carrier_name="SafeLogistics",
        penalty_clauses=["SLA late delivery"],
        use_outbox=True
    )
    assert len(actions) >= 1, "Expected executed actions from outbox path"
    print(f"   ✅ SAPActionExecutor Outbox Two-Phase Commit Verified ({len(actions)} actions committed)")


def test_7_event_streaming_daemon():
    print_banner("TEST 7: REACTIVE EVENT-DRIVEN STREAMING DAEMON (IMPROVEMENT 5.7)")
    from fastapi.testclient import TestClient
    from modules.agent_daemon import app

    client = TestClient(app)

    # 1. Test telematics stalled event
    res_stall = client.post("/api/v1/events/telematics", json={
        "order_id": "TEST_STREAM_001",
        "latitude": 19.07,
        "longitude": 72.87,
        "speed_kmh": 2.1,
        "status": "STALLED",
        "corridor": "Mumbai-Pune Expressway"
    })
    assert res_stall.status_code == 200
    data_stall = res_stall.json()
    assert data_stall["status"] == "TELEMATICS_STALL_DETECTED"
    print(f"   ✅ POST /api/v1/events/telematics: Stall detected -> {data_stall['action']}")

    # 2. Test disruption ingestion to blackboard
    res_disrupt = client.post("/api/v1/events/disruption", json={
        "corridor_or_city": "Nagpur Hub",
        "transport_mode": "Freight Rail",
        "hazard_title": "Rail yard signal failure",
        "severity": "HIGH",
        "impact_summary": "Inbound rail cargo halted 8 hours"
    })
    assert res_disrupt.status_code == 200
    assert res_disrupt.json()["status"] == "DISRUPTION_PUBLISHED_TO_BLACKBOARD"
    print(f"   ✅ POST /api/v1/events/disruption: Published to Blackboard")

    # 3. Test GET /api/v1/blackboard
    res_bb = client.get("/api/v1/blackboard")
    assert res_bb.status_code == 200
    bb_state = res_bb.json()
    assert "corridor_hazards" in bb_state
    print(f"   ✅ GET /api/v1/blackboard: {len(bb_state['corridor_hazards'])} active hazards in working memory")

    # 4. Test GET /api/v1/outbox
    res_outbox = client.get("/api/v1/outbox")
    assert res_outbox.status_code == 200
    print(f"   ✅ GET /api/v1/outbox: {res_outbox.json().get('pending_count')} pending actions in ERP queue")


def test_8_rewoo_execution_topology():
    print_banner("TEST 8: TOKEN-EFFICIENT ReWOO SPECIALIST EXECUTION (IMPROVEMENT 5.8)")
    from modules.agent_specialists import RouteSupervisorAgent, RouteAnalysisOutput

    agent = RouteSupervisorAgent(autonomous_mode=False)
    pred_payload = {
        "order_id": "TEST_REWOO_001",
        "dest_city": "Chennai",
        "shipping_type": "Road (FTL)",
        "carrier_name": "BlueDart Surface",
        "haversine_distance_km": 600.0,
        "required_transit_speed_kmh": 28.0
    }
    order_data = {
        "dest_city": "Chennai",
        "shipping_type": "Road (FTL)",
        "carrier_name": "BlueDart Surface",
        "telematics_status": "CONNECTED"
    }

    t0 = time.time()
    rewoo_result = agent.analyze_route_rewoo(pred_payload, order_data)
    rewoo_duration = time.time() - t0

    assert "ReWOO" in rewoo_result["agent_name"]
    assert "fetch_corridor_weather" in rewoo_result["tools_invoked"]
    assert "fetch_strike_alerts" in rewoo_result["tools_invoked"]
    assert "query_historical_incident_memory" in rewoo_result["tools_invoked"]

    # Validate with Pydantic
    parsed = RouteAnalysisOutput.model_validate(rewoo_result)
    assert parsed.destination_city == "Chennai"
    print(f"   ✅ ReWOO Topology Completed in {rewoo_duration:.3f}s:")
    print(f"      - Agent: {parsed.agent_name}")
    print(f"      - Parallel Tools Invoked: {len(parsed.tools_invoked)} {parsed.tools_invoked}")
    print(f"      - Telematics Status: {'Active' if parsed.telematics_active else 'Disconnected'}")
    print(f"      - Weather Hazard Detected: {parsed.weather_hazard_detected}")


def test_9_semantic_invariant_verifier():
    print_banner("TEST 9: DETERMINISTIC SEMANTIC INVARIANT VERIFIER (IMPROVEMENT 5.9)")
    from modules.order_audit_reporter import SemanticInvariantVerifier

    # 1. Test fully compliant state & report
    compliant_state = {
        "order_id": "800000000000003",
        "total_mitigation_cost": 0.0,
        "quality_findings": {
            "qa_hold_required": True,
            "qa_hold_reasons": ["Short-Dated Shelf Life Breach (<6 mos)"]
        },
        "order_data": {"order_value": 63544.59}
    }
    compliant_md = (
        "# Comprehensive Delivery Risk & Cognitive Audit Report: Order #800000000000003\n"
        "- **Invoice Net Value:** $63,544.59 USD\n"
        "- **Detour / Corridor Recommendation:** INTERCEPT & DIVERT: Halt transit\n"
        "- **Mitigated Delay Hours:** 0.0 hours (Forward Transit Halted)\n"
        "| SLA Penalty Ceiling | Chargeback ($450.00) <= 150% invoice value ($95,316.88) | PASS |\n"
        "\"title\": \"🛑 Authorize Quarantine Disposition\"\n"
    )
    v_clean = SemanticInvariantVerifier.verify_and_reconcile(compliant_state, compliant_md)
    assert len(v_clean) == 0, f"Expected 0 violations for compliant report, got: {v_clean}"
    print("   ✅ Compliant Report Verified: 0 violations across 11 Invariant Axioms")

    # 2. Test Axiom 1 induced breach (Expense $0 card on QA Quarantine)
    breach_state = dict(compliant_state)
    breach_md_1 = compliant_md + "\nApprove Expense ($0) | EXPEDITED FREIGHT APPROVAL REQUIRED"
    v_1 = SemanticInvariantVerifier.verify_and_reconcile(breach_state, breach_md_1)
    assert any("Axiom 1" in v for v in v_1), f"Expected Axiom 1 violation, got: {v_1}"
    print(f"   ✅ Axiom 1 Violation Caught: {v_1[0]}")

    # 3. Test Axiom 2 induced breach (Forward route maintained during QA Quarantine)
    breach_md_2 = compliant_md + "\nMaintain designated route"
    v_2 = SemanticInvariantVerifier.verify_and_reconcile(breach_state, breach_md_2)
    assert any("Axiom 2" in v for v in v_2), f"Expected Axiom 2 violation, got: {v_2}"
    print(f"   ✅ Axiom 2 Violation Caught: {v_2[0]}")

    # 4. Test Axiom 4 induced breach (Negative zero numerical artifact)
    breach_md_4 = compliant_md + "\nMitigated Delay: -0.0h post-mitigation (-0.0%)"
    v_4 = SemanticInvariantVerifier.verify_and_reconcile(breach_state, breach_md_4)
    assert any("Axiom 4" in v for v in v_4), f"Expected Axiom 4 violation, got: {v_4}"
    print(f"   ✅ Axiom 4 Violation Caught: {v_4[0]}")

    # 5. Test Axiom 11 induced breach (UNKNOWN order id)
    breach_md_11 = "# Comprehensive Delivery Risk & Cognitive Audit Report: Order #UNKNOWN"
    v_11 = SemanticInvariantVerifier.verify_and_reconcile(breach_state, breach_md_11)
    assert any("Axiom 11" in v for v in v_11), f"Expected Axiom 11 violation, got: {v_11}"
    print(f"   ✅ Axiom 11 Violation Caught: {v_11[0]}")


def test_10_dynamic_sensory_service():
    print_banner("TEST 10: ORDER-FIRST DYNAMIC GLOBAL SENSORY INGESTION (IMPROVEMENT 5.10)")
    from modules.dynamic_sensory_service import (
        CorridorExtractionOutput,
        OrderCorridorExtractor,
        GlobalDynamicWeatherService,
        DynamicDisruptionKeywordGenerator,
        enrich_order_with_dynamic_sensory
    )

    # 1. Test Corridor Extraction
    extractor = OrderCorridorExtractor()
    order_payload = {
        "order_id": "800000000000003",
        "dest_city": "Boston",
        "destination_country": "US",
        "plant_city": "Chicago",
        "shipping_type": "Road (FTL)",
        "requested_delivery_date": "2026-05-02"
    }
    corridor = extractor.extract_corridor(order_payload)
    assert isinstance(corridor, CorridorExtractionOutput)
    assert corridor.destination_city == "Boston"
    assert corridor.origin_city == "Chicago"
    assert corridor.shipping_mode == "Road (FTL)"
    assert len(corridor.connection_nodes) >= 1
    print(f"   ✅ Corridor Extracted: {corridor.origin_city} -> {corridor.destination_city} via {corridor.shipping_mode}")
    print(f"      - Temporal Horizon: {corridor.temporal_horizon} (Date: {corridor.target_transit_date})")
    print(f"      - Waypoints: {corridor.connection_nodes}")

    # 2. Test Global Weather Geocoding & Fetch
    weather_svc = GlobalDynamicWeatherService()
    coords = weather_svc.geocode_location("Boston", "US")
    assert coords is not None
    assert "lat" in coords and "lon" in coords
    print(f"   ✅ Global Geocoding Succeeded: Boston -> Lat {coords['lat']}, Lon {coords['lon']}")

    weather_res = weather_svc.fetch_corridor_weather(corridor)
    assert weather_res.get("status") in ("SUCCESS", "FALLBACK")
    assert weather_res.get("city") == "Boston"
    print(f"   ✅ Global Weather Retrieved for {corridor.destination_city}: Status={weather_res.get('status')}")

    # 3. Test Disruption Keyword Generator
    keyword_gen = DynamicDisruptionKeywordGenerator()
    queries = keyword_gen.generate_search_queries(corridor)
    assert len(queries) >= 3
    print(f"   ✅ Generated {len(queries)} Targeted Corridor Disruption Queries:")
    for q in queries:
        print(f"      • {q}")

    # 4. Test End-to-End Dynamic Enrichment
    enriched = enrich_order_with_dynamic_sensory(order_payload)
    assert "corridor" in enriched
    assert "weather" in enriched
    assert "targeted_search_queries" in enriched
    assert enriched["corridor"]["destination_city"] == "Boston"
    print(f"   ✅ End-to-End Order-First Dynamic Sensory Enrichment Succeeded!")


def run_all_improvements_tests():
    t_start = time.time()
    print("\n" + "🚀" * 40)
    print("   O2C AI MONITOR - 10 ARCHITECTURAL IMPROVEMENTS VERIFICATION")
    print("   Validating Production Upgrades (Improvements 5.1 - 5.10)")
    print("🚀" * 40)

    test_1_unified_graph_orchestrator()
    test_2_duckdb_polystore_olap()
    test_3_zero_churn_markdown_kb()
    test_4_blackboard_memory()
    test_5_telemetry_tracing()
    test_6_transactional_outbox()
    test_7_event_streaming_daemon()
    test_8_rewoo_execution_topology()
    test_9_semantic_invariant_verifier()
    test_10_dynamic_sensory_service()

    total_time = time.time() - t_start
    print("\n" + "=" * 80)
    print(f"🎉 ALL 10 ARCHITECTURAL IMPROVEMENT SUITES PASSED! Completed in {total_time:.2f}s")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_all_improvements_tests()

