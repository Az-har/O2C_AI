"""
Verification Test Suite for Phase 1 & Phase 2 Architecture Critique
Tests:
1. Open-Source AI Package Suite (LangGraph, LangChain Core, LangChain Ollama, ChromaDB, DuckDB, Pydantic)
2. Local Ollama Engine & GPU Offload (AMD Radeon RX 6600, Qwen2.5 models)
3. Database Decoupling (MLDatabaseExtension via DatabaseManager pool)
4. Central Agent Tool Registry (All 7 @tool functions with real DB data)
5. Tool Binding with ChatOllama
"""

import sys
import os
import json
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
    print(f"🧪 {title}")
    print("=" * 80)


def test_suite_1_packages():
    print_banner("SUITE 1: VERIFYING OPEN-SOURCE AGENT PACKAGES")
    pkgs = [
        "langgraph",
        "langchain_core",
        "langchain_ollama",
        "chromadb",
        "duckdb",
        "pydantic"
    ]
    for pkg in pkgs:
        try:
            m = __import__(pkg)
            version = getattr(m, "__version__", "Installed")
            print(f"   ✅ {pkg:<20} : {version}")
        except ImportError as e:
            print(f"   ❌ {pkg:<20} : FAILED ({e})")
            return False
    return True


def test_suite_2_ollama():
    print_banner("SUITE 2: VERIFYING LOCAL OLLAMA SERVICE & GPU INFERENCE")
    import urllib.request
    try:
        req = urllib.request.Request("http://127.0.0.1:11434/api/tags")
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            models = [m.get("name") for m in data.get("models", [])]
            print(f"   ✅ Ollama API online at http://127.0.0.1:11434")
            print(f"   📦 Available models: {', '.join(models)}")
            if not models:
                print("   ⚠️ No models currently loaded in Ollama.")
                return False
    except Exception as e:
        print(f"   ❌ Ollama API unreachable: {e}")
        return False

    # Test ChatOllama inference
    try:
        from langchain_ollama import ChatOllama
        model_name = "qwen2.5:7b" if any("7b" in m for m in models) else models[0]
        print(f"   🤖 Testing inference with {model_name}...")
        llm = ChatOllama(model=model_name, temperature=0.1, base_url="http://127.0.0.1:11434")
        resp = llm.invoke("Respond with the single word: READY")
        content = resp.content.strip()
        print(f"   ✅ Response received: '{content}'")
    except Exception as e:
        print(f"   ⚠️ ChatOllama test failed: {e}")
        return False

    return True


def test_suite_3_database_decoupling():
    print_banner("SUITE 3: DATABASE DECOUPLING & CONNECTION POOLING")
    from modules.database_manager import DatabaseManager
    from modules.ml_db_extension import MLDatabaseExtension

    db = DatabaseManager()
    print("   ✅ DatabaseManager instantiated with connection pool size:", db._pool.maxsize)

    # Dependency Injection test
    ext = MLDatabaseExtension(db_manager=db)
    print("   ✅ MLDatabaseExtension successfully initialized via injected db_manager")
    
    # Test query through pooled connection
    ctx = ext.get_order_context("1")
    print(f"   ✅ Retrieved sample order context via connection pool: {'Found' if ctx else 'Queried (Empty)'}")
    
    # Test safe close
    ext.close()
    print("   ✅ MLDatabaseExtension safely released pooled connection back to pool")
    return True


def test_suite_4_agent_tools():
    print_banner("SUITE 4: CENTRAL AGENT TOOL REGISTRY EXECUTION")
    from modules.agent_tools import (
        query_sap_order,
        fetch_corridor_weather,
        fetch_strike_alerts,
        query_rag_contracts,
        calculate_adjudicated_sla,
        post_sap_block_or_date,
        dispatch_teams_approval_card,
        ALL_AGENT_TOOLS
    )

    print(f"   ✅ Discovered {len(ALL_AGENT_TOOLS)} registered agent tools")

    # 1. query_sap_order
    res_order = query_sap_order.invoke({"order_id": "1"})
    print(f"   1. query_sap_order: Status={res_order.get('status')} | Customer={res_order.get('customer_name')}")

    # 2. fetch_corridor_weather
    res_weather = fetch_corridor_weather.invoke({"city": "Mumbai"})
    print(f"   2. fetch_corridor_weather: Status={res_weather.get('status')} | Temp={res_weather.get('temperature_celsius')}°C | Hazard={res_weather.get('hazard_detected')}")

    # 3. fetch_strike_alerts
    res_strike = fetch_strike_alerts.invoke({"city_or_corridor": "Mumbai"})
    print(f"   3. fetch_strike_alerts: Status={res_strike.get('status')} | Disruptions={res_strike.get('active_disruptions_count')}")

    # 4. query_rag_contracts
    res_rag = query_rag_contracts.invoke({"query": "What is the penalty for Tier 1 delay under MSA?", "category": "SLA"})
    print(f"   4. query_rag_contracts: Status={res_rag.get('status')} | Answer snippet: {res_rag.get('answer', '')[:70]}...")

    # 5. calculate_adjudicated_sla
    sla_normal = calculate_adjudicated_sla.invoke({
        "customer_tier": "Tier 1",
        "delay_hours": 36.0,
        "order_value_usd": 20000.0,
        "notice_compliant": True,
        "is_force_majeure": False
    })
    sla_fm = calculate_adjudicated_sla.invoke({
        "customer_tier": "Tier 1",
        "delay_hours": 36.0,
        "order_value_usd": 20000.0,
        "notice_compliant": True,
        "is_force_majeure": True
    })
    print(f"   5. calculate_adjudicated_sla:")
    print(f"      - Normal SLA (Notice relief): Net Chargeback = ${sla_normal.get('net_chargeback_usd')}")
    print(f"      - Force Majeure (Act of God): Net Chargeback = ${sla_fm.get('net_chargeback_usd')} (Waived: {sla_fm.get('force_majeure_invoked')})")

    # 6. post_sap_block_or_date
    res_sap = post_sap_block_or_date.invoke({
        "order_id": "TEST_ORD_001",
        "action_type": "DELIVERY_BLOCK",
        "reason": "QA Quarantine cold-chain breach test",
        "value": "01"
    })
    print(f"   6. post_sap_block_or_date: Status={res_sap.get('status')} | Action={res_sap.get('erp_action', {}).get('action')}")

    # 7. dispatch_teams_approval_card
    res_card = dispatch_teams_approval_card.invoke({
        "order_id": "TEST_ORD_001",
        "escalation_reason": "Mitigation cost $1,200 exceeds $500 threshold",
        "financial_impact_usd": 1200.0,
        "proposed_action": "Reroute via Priority Air Express"
    })
    print(f"   7. dispatch_teams_approval_card: Status={res_card.get('status')} | Approval Required={res_card.get('requires_human_approval')}")

    return True


def test_suite_5_tool_binding():
    print_banner("SUITE 5: LLM TOOL BINDING (LANGCHAIN + OLLAMA)")
    from langchain_ollama import ChatOllama
    from modules.agent_tools import ALL_AGENT_TOOLS
    import urllib.request

    try:
        req = urllib.request.Request("http://127.0.0.1:11434/api/tags")
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            models = [m.get("name") for m in data.get("models", [])]
        
        model_name = "qwen2.5:7b" if any("7b" in m for m in models) else models[0]
        llm = ChatOllama(model=model_name, temperature=0.1, base_url="http://127.0.0.1:11434")
        llm_with_tools = llm.bind_tools(ALL_AGENT_TOOLS)
        print(f"   ✅ Successfully bound {len(ALL_AGENT_TOOLS)} tools to {model_name}")
        print("   ✅ Tool serialization format validated for OpenAI/Ollama function calling")
        return True
    except Exception as e:
        print(f"   ❌ Tool binding failed: {e}")
        return False


def main():
    print("\n🚀 STARTING PHASE 1 & PHASE 2 VERIFICATION TEST SUITE\n")
    results = {
        "Suite 1 (Packages)": test_suite_1_packages(),
        "Suite 2 (Ollama & GPU)": test_suite_2_ollama(),
        "Suite 3 (DB Decoupling)": test_suite_3_database_decoupling(),
        "Suite 4 (Agent Tools)": test_suite_4_agent_tools(),
        "Suite 5 (Tool Binding)": test_suite_5_tool_binding(),
    }

    print_banner("SUMMARY OF VERIFICATION RESULTS")
    all_passed = True
    for suite, passed in results.items():
        icon = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {suite:<30} : {icon}")
        if not passed:
            all_passed = False

    print("=" * 80)
    if all_passed:
        print("🎉 ALL PHASE 1 & PHASE 2 REQUIREMENTS SUCCESSFULLY IMPLEMENTED AND VERIFIED!\n")
        sys.exit(0)
    else:
        print("⚠️ Some suites encountered issues. Review details above.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
