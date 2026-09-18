"""
O2C AI - LLM Provider Routing & Dynamic Fallback Testing Workbench
Streamlit Application providing:
1. Explicit switch for External Cloud LLM API (STRICTLY OFF BY DEFAULT).
2. Multi-tier fallback testing workbench: Cloud API -> Local Ollama -> Deterministic Model.
3. Live health diagnostics for all 3 tiers.
4. One-click stress-test simulations (Switch OFF, API Error Fallback, Live API).
5. Real SAP Order Adjudication workbench powered by the multi-agent specialist pipeline.
"""

import os
import sys
import time
import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import asdict
import streamlit as st

# Ensure repository root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from modules.llm_provider import (
    LLMProvider,
    LLMProviderConfig,
    LLMResponse,
    FallbackStepTrace
)
from modules.agent_specialists import (
    RouteSupervisorAgent,
    ContractAdjudicatorAgent,
    QualityMitigationAgent,
    LLMReasoningEngine,
    negotiate_inter_agent_consensus
)
from modules.config import DB_PATH

# -----------------------------------------------------------------------------
# Streamlit Page Setup & Custom Enterprise CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="O2C AI - LLM Provider & Fallback Workbench",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Metric & Card styling */
    .tier-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.82rem;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .badge-success { background-color: #e6f4ea; color: #137333; border: 1px solid #ceead6; }
    .badge-failed { background-color: #fce8e6; color: #c5221f; border: 1px solid #fad2cf; }
    .badge-skipped { background-color: #f1f3f4; color: #5f6368; border: 1px solid #dadce0; }
    .badge-online { background-color: #e8f0fe; color: #1a73e8; border: 1px solid #d2e3fc; }
    .badge-off { background-color: #fef7e0; color: #b06000; border: 1px solid #feefc3; }

    .trace-card {
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
        border-left: 5px solid #dadce0;
        background-color: #ffffff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .trace-card-success { border-left-color: #1e8e3e; }
    .trace-card-failed { border-left-color: #d93025; }
    .trace-card-skipped { border-left-color: #9aa0a6; }

    .exec-brief-box {
        border: 1px solid #d0d7de;
        border-left: 5px solid #1a73e8;
        border-radius: 6px;
        padding: 16px 20px;
        background-color: #f8fafd;
        font-size: 0.95rem;
        line-height: 1.55;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Database Helper to Retrieve Orders
# -----------------------------------------------------------------------------
@st.cache_data(ttl=60)
def fetch_sample_orders() -> List[Dict[str, Any]]:
    """Fetch real orders from SQLite database if available"""
    db_file = Path(DB_PATH)
    if not db_file.exists():
        # Fallback to local root db if relative
        db_file = BASE_DIR / "india_monitor_data" / "database" / "india_monitor.db"

    if not db_file.exists():
        return []

    try:
        conn = sqlite3.connect(str(db_file))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Check if sap_vbak exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sap_vbak'")
        if not cur.fetchone():
            conn.close()
            return []

        query = """
            SELECT 
                v.vbeln as order_id,
                MAX(v.netwr) as order_value,
                MAX(v.erdat) as order_date,
                COALESCE(MAX(k.name1), 'Apollo Veterinary Clinic') as customer_name,
                COALESCE(MAX(c.customer_tier), 'Platinum') as customer_tier,
                'National Cold-Chain Express' as carrier_name,
                COALESCE(MAX(k.ort01), 'Bangalore') as dest_city
            FROM sap_vbak v
            LEFT JOIN sap_kna1 k ON v.kunnr = k.kunnr
            LEFT JOIN sap_knvv c ON v.kunnr = c.kunnr
            GROUP BY v.vbeln
            ORDER BY v.vbeln ASC
            LIMIT 50
        """
        rows = cur.execute(query).fetchall()
        orders = [dict(r) for r in rows]
        conn.close()
        return orders
    except Exception as e:
        st.sidebar.warning(f"Could not load orders from DB: {e}")
        return []


# -----------------------------------------------------------------------------
# Sidebar: Provider Configuration & Explicit Switch
# -----------------------------------------------------------------------------
st.sidebar.title("⚙️ LLM Routing Engine")
st.sidebar.caption("Deterministic-First & Multi-Tier Fallback Architecture")

st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Explicit Cloud LLM Switch")

# CRITICAL: Switch MUST BE strictly OFF by default (value=False)
use_cloud_api = st.sidebar.toggle(
    "Enable External Cloud LLM API",
    value=False,
    help="CRITICAL: Default is OFF. When OFF, external cloud calls are completely bypassed, routing directly to local Ollama or deterministic expert rules."
)

if use_cloud_api:
    st.sidebar.success("⚡ External Cloud API is ENABLED")
else:
    st.sidebar.info("🛡️ Cloud API is DISABLED (Default: Deterministic / Local Only)")

st.sidebar.markdown("---")
st.sidebar.subheader("☁️ Tier 1: Cloud API Config")

provider_choice = st.sidebar.selectbox(
    "Provider Protocol",
    options=["gemini", "groq", "openai", "custom"],
    index=0,
    help="Supports Google Gemini REST API, Groq Cloud, OpenAI, or Custom OpenAI-compatible REST endpoints."
)

# Auto-detect defaults
default_env_keys = {
    "gemini": os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", "")),
    "groq": os.getenv("GROQ_API_KEY", ""),
    "openai": os.getenv("OPENAI_API_KEY", ""),
    "custom": os.getenv("CUSTOM_API_KEY", "")
}

model_options = {
    "gemini": ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"],
    "groq": ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"],
    "openai": ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
    "custom": ["custom-model"]
}

env_key_present = bool(default_env_keys.get(provider_choice))
api_key_input = st.sidebar.text_input(
    f"{provider_choice.title()} API Key",
    value=default_env_keys.get(provider_choice, ""),
    type="password",
    help="Enter API key or set via environment variable. Input is kept securely in session memory."
)

selected_model = st.sidebar.selectbox(
    "Model Name",
    options=model_options.get(provider_choice, ["default-model"]),
    index=0
)

custom_endpoint = ""
if provider_choice == "custom":
    custom_endpoint = st.sidebar.text_input(
        "Custom Endpoint URL",
        value="http://localhost:8000/v1",
        help="Base URL for OpenAI-compatible REST API (e.g. vLLM, LM-Studio, LocalAI)"
    )

timeout_secs = st.sidebar.slider(
    "API Timeout (seconds)",
    min_value=1.0,
    max_value=30.0,
    value=8.0,
    step=0.5,
    help="Fast timeout ensures rapid fallback cascading without hanging the user session."
)

st.sidebar.markdown("---")
st.sidebar.subheader("🦙 Tier 2: Local Ollama Config")

ollama_host = st.sidebar.text_input(
    "Ollama Daemon URL",
    value="http://127.0.0.1:11434",
    help="Probed with lightweight /api/tags ping before attempting inference."
)

ollama_model = st.sidebar.text_input(
    "Ollama Model Tag",
    value="qwen2.5:7b",
    help="Local model name (e.g. qwen2.5:7b, llama3:8b)"
)

# Instantiate the active LLMProvider with current UI settings
current_config = LLMProviderConfig(
    use_cloud_api=use_cloud_api,
    provider=provider_choice,
    api_key=api_key_input,
    model_name=selected_model,
    custom_endpoint=custom_endpoint,
    ollama_host=ollama_host,
    ollama_model=ollama_model,
    timeout_seconds=timeout_secs
)
active_provider = LLMProvider(config=current_config)


# -----------------------------------------------------------------------------
# Main Header & Architectural Fallback Diagram
# -----------------------------------------------------------------------------
st.title("⚡ O2C AI - LLM Provider & Dynamic Fallback Workbench")
st.markdown("""
This testing page verifies the **resilient multi-tier LLM fallback hierarchy** designed for the **Order-to-Cash (O2C) AI Disruption Monitor**.
By default, the external Cloud API is **explicitly disabled** to guarantee 0-dependency, zero-cost, and deterministic execution.
""")

# Architecture Pipeline Banner
st.markdown("""
```text
  ┌─────────────────────────────────┐
  │  1. External Cloud LLM API      │ ──[ Switch OFF ]───────────────┐
  │  (Google Gemini / Groq / OpenAI)│ ──[ Switch ON / Run Failed ]───┼──┐
  └─────────────────────────────────┘                                │  │
                                                                     │  │
  ┌─────────────────────────────────┐                                │  │
  │  2. Local Ollama SLM/LLM        │ ◄──────────────────────────────┘  │
  │  (127.0.0.1:11434 / Qwen2.5)    │ ──[ Daemon Offline / Failed ]─────┼──┐
  └─────────────────────────────────┘                                   │  │
                                                                        │  │
  ┌─────────────────────────────────────────────────────────────┐       │  │
  │  3. Deterministic Specialist Model                          │ ◄─────┴──┘
  │  (Guaranteed Rule Engine, Zero Latency, 100% Reliable)      │
  └─────────────────────────────────────────────────────────────┘
```
""")

# -----------------------------------------------------------------------------
# Live Health Diagnostics Bar
# -----------------------------------------------------------------------------
st.subheader("🩺 Live Health Diagnostics")

col_diag1, col_diag2, col_diag3 = st.columns(3)

with col_diag1:
    h_cloud = active_provider.check_cloud_api()
    if not use_cloud_api:
        st.markdown("""
        **Tier 1: External Cloud API**  
        <span class="tier-badge badge-off">🔒 DISABLED (Switch OFF)</span>  
        *Explicit switch is OFF. Cloud calls are bypassed.*
        """, unsafe_allow_html=True)
    elif h_cloud.get("available"):
        st.markdown(f"""
        **Tier 1: External Cloud API**  
        <span class="tier-badge badge-success">🟢 ONLINE ({h_cloud.get('latency_ms', 0):.0f} ms)</span>  
        *Provider: {provider_choice.upper()} ({selected_model})*
        """, unsafe_allow_html=True)
    elif h_cloud.get("status") == "CONFIG_ERROR":
        st.markdown(f"""
        **Tier 1: External Cloud API**  
        <span class="tier-badge badge-failed">⚠️ KEY MISSING</span>  
        *{h_cloud.get('message')}*
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        **Tier 1: External Cloud API**  
        <span class="tier-badge badge-failed">🔴 ERROR / UNREACHABLE</span>  
        *{h_cloud.get('message', 'Failed')}*
        """, unsafe_allow_html=True)

with col_diag2:
    h_ollama = active_provider.check_ollama()
    if h_ollama.get("available"):
        st.markdown(f"""
        **Tier 2: Local Ollama (SLM)**  
        <span class="tier-badge badge-success">🟢 ONLINE ({h_ollama.get('latency_ms', 0):.0f} ms)</span>  
        *Host: {ollama_host} (Model: {ollama_model})*
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        **Tier 2: Local Ollama (SLM)**  
        <span class="tier-badge badge-skipped">⚪ OFFLINE / STANDBY</span>  
        *{h_ollama.get('message', 'Daemon not active')}*
        """, unsafe_allow_html=True)

with col_diag3:
    h_det = active_provider.check_deterministic()
    st.markdown("""
    **Tier 3: Deterministic Model**  
    <span class="tier-badge badge-success">🟢 ACTIVE & READY (100% Guaranteed)</span>  
    *In-memory rule engine; zero latency, zero RAM bloat.*
    """, unsafe_allow_html=True)

st.markdown("---")


# -----------------------------------------------------------------------------
# Function to Render Trace Timeline
# -----------------------------------------------------------------------------
def render_trace_timeline(response: LLMResponse):
    """Renders the step-by-step fallback cascade visually"""
    col_prov, col_lat, col_stat = st.columns([2, 1, 1])
    with col_prov:
        if response.effective_provider == "CLOUD_API":
            st.markdown(f"### Effective Provider: <span class='tier-badge badge-online'>☁️ CLOUD API ({active_provider.config.provider.upper()})</span>", unsafe_allow_html=True)
        elif response.effective_provider == "LOCAL_OLLAMA":
            st.markdown(f"### Effective Provider: <span class='tier-badge badge-online'>🦙 LOCAL OLLAMA ({active_provider.config.ollama_model})</span>", unsafe_allow_html=True)
        else:
            st.markdown("### Effective Provider: <span class='tier-badge badge-success'>⚡ DETERMINISTIC SPECIALIST MODEL</span>", unsafe_allow_html=True)

    with col_lat:
        st.metric("Total Latency", f"{response.total_latency_ms:.1f} ms")
    with col_stat:
        st.metric("Execution Status", response.status)

    st.markdown("#### 🌊 Cascading Fallback Waterfall Trace")
    
    for step in response.trace:
        if step.status == "SUCCESS":
            card_class = "trace-card trace-card-success"
            badge = f'<span class="tier-badge badge-success">✓ SUCCESS ({step.latency_ms:.1f} ms)</span>'
        elif step.status == "FAILED":
            card_class = "trace-card trace-card-failed"
            badge = f'<span class="tier-badge badge-failed">✗ FAILED ({step.latency_ms:.1f} ms)</span>'
        else:
            card_class = "trace-card trace-card-skipped"
            badge = '<span class="tier-badge badge-skipped">○ SKIPPED</span>'

        error_html = f"<div style='color: #c5221f; font-size: 0.85rem; margin-top: 6px;'><b>Error details:</b> {step.error_message}</div>" if step.error_message else ""

        st.markdown(f"""
        <div class="{card_class}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <b>Step {step.step_number}: {step.tier_name}</b>
                {badge}
            </div>
            <div style="color: #444; font-size: 0.9rem; margin-top: 4px;">
                <b>Target:</b> <code>{step.target_endpoint}</code> | <b>Attempted:</b> {step.attempted}
            </div>
            <div style="color: #666; font-size: 0.88rem; margin-top: 4px;">
                {step.details}
            </div>
            {error_html}
        </div>
        """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Testing Workbench Tabs
# -----------------------------------------------------------------------------
tab1, tab2 = st.tabs([
    "🧪 Mode A: Quick Fallback Simulation & Stress Tests",
    "📦 Mode B: Real SAP Order Multi-Agent Adjudication"
])

# =============================================================================
# TAB 1: Quick Fallback Stress Tests
# =============================================================================
with tab1:
    st.markdown("### 🧪 One-Click Fallback Stress Tests")
    st.caption("Verify behavior of switch and fallback cascades under various conditions instantly.")

    col_btn1, col_btn2, col_btn3 = st.columns(3)

    run_scenario = None

    with col_btn1:
        if st.button("🧪 Test 1: Switch OFF (Default)\nVerify Cloud Bypassed -> Deterministic", use_container_width=True):
            run_scenario = "SWITCH_OFF"

    with col_btn2:
        if st.button("🚨 Test 2: Switch ON + Invalid Key\nVerify Safe Cascade -> Ollama -> Deterministic", use_container_width=True):
            run_scenario = "SWITCH_ON_API_ERROR"

    with col_btn3:
        if st.button("🚀 Test 3: Run with Current Sidebar Config\nTest Current Settings", use_container_width=True):
            run_scenario = "CURRENT_CONFIG"

    if run_scenario:
        st.markdown("---")
        test_prompt = (
            "Analyze order 800000000000001: Apollo Veterinary Hospital (Tier 1). "
            "Delay: 14.5 hours due to NH-48 monsoon flooding. Cargo: Biological Prescription Diet. "
            "SLA penalty: $450.00. Recommend immediate operational action and financial passthrough."
        )

        def mock_deterministic_brief() -> str:
            return (
                "Order 800000000000001 destined for Apollo Veterinary Hospital (Enterprise Tier 1) via Gati Logistics "
                "is predicted to be DELAYED by 14.5 hours (Delay Probability: 88.0%); Hazards: NH-48 Monsoon Inundation.\n"
                "Contractual SLA Exposure: $450.00. Total Carrier Chargeback: $300.00. Force Majeure: NOT_APPLICABLE.\n"
                "Recommended Action: INTERCEPT & DIVERT: Immediately halt transit for bio-secure quarantine; cancel forward delivery.\n"
                "QA Quarantine: Prescription diet shelf-life expired.\n"
                "Governance Status: AUTONOMOUSLY_APPROVED (AI Copilot Auto-Approval)."
            )

        if run_scenario == "SWITCH_OFF":
            st.info("Executing Scenario 1: Switch is set to OFF. Cloud API should be skipped, local Ollama probed, and Deterministic model executed.")
            test_provider = LLMProvider(LLMProviderConfig(use_cloud_api=False, ollama_host=ollama_host, ollama_model=ollama_model))
            resp = test_provider.invoke_with_fallback(
                prompt=test_prompt,
                system_prompt="You are an enterprise logistics dispute synthesizer.",
                deterministic_fallback_fn=mock_deterministic_brief
            )
        elif run_scenario == "SWITCH_ON_API_ERROR":
            st.warning("Executing Scenario 2: Switch is ON, but using a simulated invalid API key. Must catch error without crashing, check Ollama, and cascade to Deterministic.")
            test_provider = LLMProvider(LLMProviderConfig(
                use_cloud_api=True,
                provider="gemini",
                api_key="SIMULATED_INVALID_KEY_9999_FORCE_FAIL",
                ollama_host=ollama_host,
                ollama_model=ollama_model,
                timeout_seconds=3.0
            ))
            resp = test_provider.invoke_with_fallback(
                prompt=test_prompt,
                system_prompt="You are an enterprise logistics dispute synthesizer.",
                deterministic_fallback_fn=mock_deterministic_brief
            )
        else:
            st.info("Executing Scenario 3: Running with live active configuration from sidebar.")
            resp = active_provider.invoke_with_fallback(
                prompt=test_prompt,
                system_prompt="You are an enterprise logistics dispute synthesizer.",
                deterministic_fallback_fn=mock_deterministic_brief
            )

        render_trace_timeline(resp)

        st.markdown("#### 📋 Synthesized Output Brief")
        st.markdown(f"""
        <div class="exec-brief-box">
            {resp.content.replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)

        with st.expander("🔍 Inspect Full Audit Trace JSON", expanded=False):
            st.json(resp.to_dict())


# =============================================================================
# TAB 2: Real SAP Order Multi-Agent Adjudication
# =============================================================================
with tab2:
    st.markdown("### 📦 Real SAP Order Adjudication & Inter-Agent Negotiation")
    st.caption("Select an order from the enterprise database to run the complete 4-Specialist Agent Pipeline using the configured switch and fallback engine.")

    orders = fetch_sample_orders()
    order_options = {}
    if orders:
        for o in orders:
            oid = str(o.get("order_id"))
            cname = o.get("customer_name") or "Clinic"
            val = float(o.get("order_value", 0))
            order_options[f"Order #{oid} - {cname} (${val:,.2f})"] = o
    
    order_options["Custom Simulation Scenario"] = {
        "order_id": "800000000099999",
        "customer_name": "Fortis Veterinary Institute",
        "customer_tier": "Tier-1 Enterprise",
        "carrier_name": "Gati KWE Cold-Chain",
        "shipping_type": "Road (Refrigerated FTL)",
        "dest_city": "Mumbai",
        "order_value": 45000.00
    }

    selected_order_label = st.selectbox("Select Target Order", options=list(order_options.keys()), index=0)
    target_order = order_options[selected_order_label]

    col_ord1, col_ord2, col_ord3, col_ord4 = st.columns(4)
    with col_ord1:
        st.text_input("Order ID", value=str(target_order.get("order_id", "800000000000001")), disabled=True)
        st.text_input("Customer Name", value=str(target_order.get("customer_name", "Clinic")), disabled=True)
    with col_ord2:
        cust_tier = st.selectbox("Customer Tier", options=["Tier-1 Enterprise", "Tier-2 Regional", "Independent Clinic"], index=0)
        carrier_name = st.text_input("Carrier", value=str(target_order.get("carrier_name", "Gati Logistics")))
    with col_ord3:
        delay_prob = st.slider("Simulated Delay Probability", min_value=0.0, max_value=1.0, value=0.88, step=0.01)
        delay_hours = st.slider("Predicted Delay (Hours)", min_value=0.0, max_value=48.0, value=14.5, step=0.5)
    with col_ord4:
        force_qa_hold = st.checkbox("Mandate QA Quarantine Hold (Biological Cargo)", value=True)
        invoke_force_majeure = st.checkbox("Invoke Act of God / Force Majeure", value=False)

    btn_run_pipeline = st.button("🚀 Run Multi-Agent Adjudication & Negotiation", type="primary", use_container_width=True)

    if btn_run_pipeline:
        st.markdown("---")
        order_id = str(target_order.get("order_id", "800000000000001"))
        customer_name = str(target_order.get("customer_name", "Veterinary Clinic"))
        shipping_type = str(target_order.get("shipping_type", "Road (Refrigerated FTL)"))
        dest_city = str(target_order.get("dest_city", "Mumbai"))
        order_val = float(target_order.get("order_value", 25000.0))
        will_delay = delay_prob >= 0.50

        # Build prediction payload
        prediction_payload = {
            "order_id": order_id,
            "customer_name": customer_name,
            "customer_tier": cust_tier,
            "carrier_name": carrier_name,
            "shipping_type": shipping_type,
            "dest_city": dest_city,
            "order_value_usd": order_val,
            "delay_probability": delay_prob,
            "will_be_delayed": will_delay,
            "delay_hours": delay_hours,
            "predicted_eta": "2026-10-15 18:30 IST",
            "root_causes": ["Monsoon highway waterlogging", "Thermal monitor divergence"] if will_delay else ["On schedule"],
            "rag_sources": [
                "Master Vendor Agreement Art. 8.4 (SLA Delay Penalties)",
                "Cold-Chain Quality Policy SOP-QC-401 (Temperature Excursion Quarantine)",
                "Carrier Chargeback Schedule 2026 Cl. 12"
            ]
        }

        order_data = {
            "order_id": order_id,
            "kunnr": 1001,
            "netwr": order_val,
            "materials": [{"matnr": "DIET-RENAL-01", "maktx": "Prescription Diet Renal Canine 12kg", "is_perishable": True}]
        }

        # 1. Specialist Agents Execution
        route_agent = RouteSupervisorAgent()
        contract_agent = ContractAdjudicatorAgent()
        quality_agent = QualityMitigationAgent()
        reasoning_engine = LLMReasoningEngine(llm_provider=active_provider)

        with st.spinner("Specialist Agents collaborating across Route, Legal, Quality, and Fallback LLM Engine..."):
            # Route Supervisor
            route_res = route_agent.analyze_route(prediction_payload, order_data)

            # Contract Adjudicator
            contract_res = contract_agent.adjudicate_contract(
                prediction_payload=prediction_payload,
                order_data=order_data,
                route_analysis=route_res,
                notice_given_12h=not invoke_force_majeure
            )
            if invoke_force_majeure:
                contract_res["force_majeure_status"] = "INVOKED_VALID_ACT_OF_GOD"
                contract_res["force_majeure_waived"] = True
                contract_res["sla_delay_penalty_usd"] = 0.0

            # Quality Mitigation
            quality_res = quality_agent.plan_mitigation(
                prediction_payload=prediction_payload,
                order_data=order_data,
                contract_analysis=contract_res
            )
            if force_qa_hold:
                quality_res["qa_hold_required"] = True
                quality_res.setdefault("qa_hold_reasons", []).append("Prescription diet shelf-life thermal threshold violated")

            # Inter-Agent Multi-Turn Negotiation Protocol
            negotiation_res = negotiate_inter_agent_consensus(
                contract_agent=contract_agent,
                quality_agent=quality_agent,
                prediction_payload=prediction_payload,
                order_data=order_data,
                route_analysis=route_res,
                notice_given_12h=not invoke_force_majeure,
                llm_provider=active_provider
            )

            # Executive Synthesis via Multi-Tier Fallback Provider
            synthesis_resp = reasoning_engine.synthesize_executive_decision_with_trace(
                order_id=order_id,
                customer_name=customer_name,
                customer_tier=cust_tier,
                carrier_name=carrier_name,
                shipping_type=shipping_type,
                delay_prob=delay_prob,
                will_delay=will_delay,
                delay_hours=delay_hours,
                predicted_eta="2026-10-15 18:30 IST",
                route_analysis=route_res,
                contract_analysis=contract_res,
                quality_analysis=quality_res,
                rag_citations=prediction_payload["rag_sources"]
            )

        # Render Waterfall Trace
        render_trace_timeline(synthesis_resp)

        # Render Executive Brief
        st.markdown("#### 📜 Authoritative Executive Decision Brief")
        st.markdown(f"""
        <div class="exec-brief-box">
            {synthesis_resp.content.replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)

        # Specialist Findings Sub-Tabs
        st.markdown("#### 👥 Specialist Agent Adjudications")
        t_route, t_legal, t_qual, t_debate, t_audit = st.tabs([
            "🗺️ Route Supervisor",
            "⚖️ Contract Adjudicator",
            "🔬 Quality Mitigation",
            "💬 Multi-Turn Debate",
            "📊 Full Audit Payload"
        ])

        with t_route:
            st.json(route_res)

        with t_legal:
            st.json(contract_res)

        with t_qual:
            st.json(quality_res)

        with t_debate:
            outcome = negotiation_res.get("negotiation_outcome", {})
            st.markdown(f"**Consensus Compromise:** {outcome.get('compromise_summary', 'N/A')}")
            turns = outcome.get("turns", [])
            for t in turns:
                speaker = t.get("speaker", "Agent")
                proposal = t.get("proposal", "")
                st.markdown(f"**Turn {t.get('turn_index')} [{speaker}]:** {proposal}")

        with t_audit:
            audit_bundle = {
                "order_id": order_id,
                "effective_provider": synthesis_resp.effective_provider,
                "provider_config": {
                    "switch_is_on": use_cloud_api,
                    "provider": provider_choice,
                    "model": selected_model
                },
                "fallback_trace": [asdict(t) for t in synthesis_resp.trace] if hasattr(synthesis_resp, "trace") else [],
                "specialist_analyses": {
                    "route": route_res,
                    "contract": contract_res,
                    "quality": quality_res,
                    "negotiation": outcome
                }
            }
            st.json(audit_bundle)

# Footer
st.markdown("---")
st.caption("O2C AI Disruption Monitor | Multi-Tier Resilient Fallback Architecture | Offline-Capable & Lightweight")
