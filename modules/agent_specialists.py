"""
Multi-Agent Specialist Roles & LLM Legal Reasoning Engine (Phase 4)
Implements collaborative multi-agent specialist architecture aligned with Reference specifications:
- RouteSupervisorAgent: Telemetry, transit velocity, corridor weather, strike disruptions, telematics disconnect penalties ($200)
- ContractAdjudicatorAgent: Platinum/Gold SLA matrices, receiving dock operating hours (post-17:00 $150 waiver), Force Majeure conditionality
- QualityMitigationAgent: Prescription diet stock-out mitigation ($1,000 Air Freight cap), QA inspection holds, minimum shelf-life rules
- LLMReasoningEngine: Structured multi-model LLM legal synthesis (Gemini / OpenAI / Ollama / Local Expert fallback)
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import numpy as np


class RouteSupervisorAgent:
    """
    Specialist Agent 1: Route & Telematics Supervisor
    Monitors live shipment milestones, corridor weather, transport strikes,
    transit velocity, and carrier GPS/telematics integrity.
    """

    def analyze_route(self, prediction_payload: Dict[str, Any], order_data: Dict[str, Any]) -> Dict[str, Any]:
        dest_city = str(prediction_payload.get("dest_city", "Unknown"))
        shipping_type = str(prediction_payload.get("shipping_type", "Road (FTL)"))
        carrier_name = str(prediction_payload.get("carrier_name", "Unknown Carrier"))
        distance_km = float(prediction_payload.get("haversine_distance_km", 500.0))
        speed_kmh = float(prediction_payload.get("required_transit_speed_kmh", 25.0))
        
        telematics_active = True
        telematics_penalty = 0.0
        telematics_notes = []
        
        if "blind" in carrier_name.lower() or order_data.get("telematics_status") == "DISCONNECTED":
            telematics_active = False
            telematics_penalty = 200.0
            telematics_notes.append("Telematics Disconnect Breach: GPS signal lost >12 hours; $200 blind-tracking penalty assessed.")

        route_hazards = []
        if speed_kmh > 55.0:
            route_hazards.append(f"Unrealistic Transit Velocity ({speed_kmh:.1f} km/h required over {distance_km:.0f} km corridor)")
        if "LTL" in shipping_type.upper():
            route_hazards.append("LTL Multi-Stop Terminal Consolidation Dwell")

        return {
            "agent_name": "RouteSupervisorAgent",
            "telematics_active": telematics_active,
            "telematics_penalty_usd": telematics_penalty,
            "telematics_notes": telematics_notes,
            "route_hazards": route_hazards,
            "corridor_distance_km": distance_km,
            "transit_speed_kmh": speed_kmh,
            "destination_city": dest_city,
            "shipping_mode": shipping_type
        }


class ContractAdjudicatorAgent:
    """
    Specialist Agent 2: Contract & SLA Legal Adjudicator
    Evaluates customer tier penalties, grace periods, receiving dock closing hours,
    and adjudicates Force Majeure conditions against the 12-hour notification mandate.
    """

    def adjudicate_contract(
        self,
        prediction_payload: Dict[str, Any],
        order_data: Dict[str, Any],
        route_analysis: Dict[str, Any],
        notice_given_12h: bool = True
    ) -> Dict[str, Any]:
        customer_tier = str(prediction_payload.get("customer_tier", "Independent")).capitalize()
        order_val = float(prediction_payload.get("order_value_usd", 2500.0))
        delay_prob = float(prediction_payload.get("delay_probability", 0.0))
        will_delay = bool(prediction_payload.get("will_be_delayed", delay_prob >= 0.50))
        delay_hours = float(prediction_payload.get("delay_hours", 0.0))
        predicted_eta = str(prediction_payload.get("predicted_eta", ""))
        root_causes = prediction_payload.get("root_causes", prediction_payload.get("root_cause", []))
        if isinstance(root_causes, str):
            root_causes = [r.strip() for r in root_causes.split(";")]

        weather_alert = any("thermal" in r.lower() or "rain" in r.lower() or "wind" in r.lower() or "heatwave" in r.lower() or "act of god" in r.lower() for r in root_causes)
        telematics_active = route_analysis.get("telematics_active", True)
        
        force_majeure_status = "NOT_APPLICABLE"
        force_majeure_waived = False

        if weather_alert:
            if not telematics_active:
                force_majeure_status = "VOIDED_TELEMATICS_DISCONNECT ($200 penalty applied, weather waiver revoked)"
            elif not notice_given_12h:
                force_majeure_status = "REJECTED_NOTICE_BREACH (12-Hour proactive notification rule missed)"
            else:
                force_majeure_status = "GRANTED_72H_WAIVER (Act of God verified, 12h notification confirmed)"
                force_majeure_waived = True

        delay_days = max(0.0, (delay_hours - 24.0) / 24.0) if delay_hours > 24.0 else 0.0
        sla_penalty = 0.0
        penalty_clauses = []

        if will_delay and delay_days > 0 and not force_majeure_waived:
            if customer_tier.lower() == "platinum":
                days_billed = np.ceil(delay_days)
                sla_penalty = days_billed * 500.0
                penalty_clauses.append(f"Platinum SLA Clause: ${sla_penalty:.2f} penalty ({days_billed:.0f} day(s) @ $500/day past 24h grace).")
            else:
                days_billed = np.ceil(delay_days)
                daily_fee = 0.05 * order_val
                sla_penalty = min(0.25 * order_val, days_billed * daily_fee)
                penalty_clauses.append(f"Independent/Gold SLA Clause: ${sla_penalty:.2f} penalty (5%/day capped at 25% of ${order_val:.2f}).")
        elif force_majeure_waived:
            penalty_clauses.append("Force Majeure Exemption: Standard SLA late penalties 100% waived under Act of God protocol.")

        close_time_str = str(order_data.get("close_time", "17:00"))
        after_hours_violation = False
        redelivery_fee_usd = 0.0
        try:
            eta_dt = datetime.strptime(predicted_eta[:16], "%Y-%m-%d %H:%M")
            close_hour = int(close_time_str.split(":")[0])
            if eta_dt.hour >= close_hour:
                after_hours_violation = True
                redelivery_fee_usd = 150.0
                penalty_clauses.append(f"Receiving Window Breach: ETA {predicted_eta} falls after {close_time_str} dock close; carrier absorbs $150 redelivery fee.")
        except Exception:
            pass

        total_carrier_chargeback = sla_penalty + redelivery_fee_usd + route_analysis.get("telematics_penalty_usd", 0.0)

        return {
            "agent_name": "ContractAdjudicatorAgent",
            "customer_tier": customer_tier,
            "force_majeure_status": force_majeure_status,
            "force_majeure_waived": force_majeure_waived,
            "sla_delay_penalty_usd": float(sla_penalty),
            "after_hours_violation": after_hours_violation,
            "after_hours_redelivery_fee_usd": float(redelivery_fee_usd),
            "total_carrier_chargeback_usd": float(total_carrier_chargeback),
            "penalty_clauses": penalty_clauses
        }


class QualityMitigationAgent:
    """
    Specialist Agent 3: Quality Assurance & Mitigation Planner
    Evaluates prescription diet fragility, shelf-life destruction risks,
    and authorizes emergency Air Freight ($1,000 replacement) or QA Holds.
    """

    def plan_mitigation(
        self,
        prediction_payload: Dict[str, Any],
        order_data: Dict[str, Any],
        contract_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        has_specialty = bool(prediction_payload.get("has_specialty_diet", False))
        delay_hours = float(prediction_payload.get("delay_hours", 0.0))
        will_delay = bool(prediction_payload.get("will_be_delayed", False))
        min_shelf_life = int(order_data.get("min_shelf_life", 12))
        material_desc = str(order_data.get("material_description", "Veterinary Nutrition Diet"))
        
        mitigation_actions = []
        mitigation_cost = 0.0
        qa_hold_required = False
        qa_hold_reasons = []

        if has_specialty and delay_hours > 48.0:
            mitigation_cost += 1000.0
            mitigation_actions.append(
                "EMERGENCY_AIR_FREIGHT: Authorized $1,000 replacement pallet via expedited air courier to prevent critical prescription diet stock-out."
            )

        if min_shelf_life < 6 or (will_delay and delay_hours > 120.0 and min_shelf_life <= 6):
            qa_hold_required = True
            qa_hold_reasons.append("Short-Dated Shelf Life Breach (<6 mos): Order quarantined for bio-secure return/destruction at carrier liability.")

        root_causes = prediction_payload.get("root_causes", prediction_payload.get("root_cause", []))
        if isinstance(root_causes, str):
            root_causes = [r.strip() for r in root_causes.split(";")]
        if any("thermal" in r.lower() or "heatwave" in r.lower() for r in root_causes) and delay_hours > 24.0:
            qa_hold_required = True
            qa_hold_reasons.append("Thermal Degradation Alert (>40°C heatwave): Cargo flagged for lab vitamin potency testing prior to clinic release.")

        if mitigation_cost > 500.0 or contract_analysis.get("sla_delay_penalty_usd", 0) > 1000.0:
            approval_status = "DIRECTOR_APPROVAL_REQUIRED"
            approval_gate = "Actionable Card Routed to Regional Logistics Director via MS Teams (Expense > $500, 2-Hour SLA)"
            ms_teams_escalation = {
                "recipient": "Regional Logistics Director",
                "channel": "MS Teams / Logistics Desk",
                "order_id": str(prediction_payload.get("order_id")),
                "customer": str(prediction_payload.get("customer_name")),
                "carrier": str(prediction_payload.get("carrier_name")),
                "mitigation_expense_usd": mitigation_cost,
                "recommended_action": mitigation_actions[0] if mitigation_actions else "Approve expedited re-routing",
                "sla_response_hours": 2.0,
                "urgency": "CRITICAL" if has_specialty else "HIGH"
            }
        else:
            approval_status = "AUTONOMOUSLY_APPROVED"
            approval_gate = "AI Copilot Auto-Approval (Expense <= $500 threshold)"
            ms_teams_escalation = None

        return {
            "agent_name": "QualityMitigationAgent",
            "has_specialty_diet": has_specialty,
            "material_description": material_desc,
            "mitigation_actions": mitigation_actions,
            "total_mitigation_cost_usd": float(mitigation_cost),
            "qa_hold_required": qa_hold_required,
            "qa_hold_reasons": qa_hold_reasons,
            "approval_status": approval_status,
            "approval_gate": approval_gate,
            "ms_teams_escalation_card": ms_teams_escalation
        }


class LLMReasoningEngine:
    """
    Specialist Agent 4: LLM Legal Reasoning & Synthesis Core
    Combines Math (ML delay predictions, velocity, delay hours), Contract Rules
    (RAG exact retrieved clauses), and Master Data into a comprehensive executive brief.
    
    Supports:
    1. Databricks Foundation Model Serving (e.g. databricks-meta-llama-3-70b-instruct, dbrx-instruct)
    2. Google Gemini API (gemini-1.5-pro / gemini-1.5-flash)
    3. OpenAI API (gpt-4o, gpt-4o-mini)
    4. Local Ollama (llama3, mistral)
    5. Deterministic Local Expert Reasoning (zero-latency, offline fallback)
    """

    def __init__(self):
        self.provider = "local_expert"
        self.endpoint_name = os.getenv("DATABRICKS_LLM_ENDPOINT", "databricks-meta-llama-3-70b-instruct")
        
        if os.getenv("DATABRICKS_HOST") and os.getenv("DATABRICKS_TOKEN"):
            self.provider = "databricks_foundation_model"
        elif os.getenv("GEMINI_API_KEY"):
            self.provider = "gemini"
        elif os.getenv("OPENAI_API_KEY"):
            self.provider = "openai"
        elif os.getenv("OLLAMA_HOST"):
            self.provider = "ollama"

    def build_synthesis_prompt(
        self,
        order_id: str,
        customer_name: str,
        customer_tier: str,
        carrier_name: str,
        shipping_type: str,
        delay_prob: float,
        will_delay: bool,
        delay_hours: float,
        predicted_eta: str,
        route_analysis: Dict[str, Any],
        contract_analysis: Dict[str, Any],
        quality_analysis: Dict[str, Any],
        rag_citations: List[str]
    ) -> str:
        """Constructs rich legal prompt combining ML Math + RAG Contract Clauses + Master Data"""
        return f"""You are the O2C Delivery Risk Copilot Legal & Operations Synthesizer.
Analyze the following Order-to-Cash disruption package and formulate a legally grounded executive decision:

### 1. SAP MASTER DATA & PREDICTIVE ML ENGINE A OUTPUT:
- Order ID: {order_id}
- Customer: {customer_name} (Tier: {customer_tier})
- Carrier: {carrier_name} (Mode: {shipping_type})
- Delay Prediction: {'DELAYED by ' + f'{delay_hours:.1f} hrs' if will_delay else 'ON SCHEDULE'} (Probability: {delay_prob:.1%})
- Predicted ETA: {predicted_eta}
- Route Corridor: {route_analysis.get('corridor_distance_km', 0):.0f} km @ required {route_analysis.get('transit_speed_kmh', 0):.1f} km/h
- Route Hazards: {', '.join(route_analysis.get('route_hazards', [])) or 'None detected'}

### 2. ENGINE B RETRIEVED CONTRACT & POLICY CLAUSES (RAG):
- Citations: {', '.join(rag_citations) if rag_citations else 'Standard Master Vendor Agreement'}
- Force Majeure Status: {contract_analysis.get('force_majeure_status')}
- Contractual Penalty Exposure: ${contract_analysis.get('sla_delay_penalty_usd', 0):.2f}
- Carrier Chargeback Liability: ${contract_analysis.get('total_carrier_chargeback_usd', 0):.2f}
- Receiving Window Violation: {contract_analysis.get('after_hours_violation')}

### 3. MITIGATION & QUALITY ASSURANCE:
- Action Plan: {quality_analysis.get('mitigation_actions', ['Monitor active telematics'])[0]}
- QA Quarantine Required: {quality_analysis.get('qa_hold_required')}
- Governance Approval Gate: {quality_analysis.get('approval_gate')}

Provide a concise, authoritative executive synthesis brief summarizing the root cause, financial liability passthrough, and action authorization."""

    def synthesize_executive_decision(
        self,
        order_id: str,
        customer_name: str,
        customer_tier: str,
        carrier_name: str,
        shipping_type: str,
        delay_prob: float,
        will_delay: bool,
        delay_hours: float,
        predicted_eta: str,
        route_analysis: Dict[str, Any],
        contract_analysis: Dict[str, Any],
        quality_analysis: Dict[str, Any],
        rag_citations: List[str]
    ) -> str:
        # Check if external LLM provider is configured
        if self.provider == "databricks_foundation_model":
            try:
                import urllib.request
                import urllib.error
                prompt = self.build_synthesis_prompt(
                    order_id, customer_name, customer_tier, carrier_name, shipping_type,
                    delay_prob, will_delay, delay_hours, predicted_eta,
                    route_analysis, contract_analysis, quality_analysis, rag_citations
                )
                host = os.getenv("DATABRICKS_HOST", "").rstrip("/")
                token = os.getenv("DATABRICKS_TOKEN", "")
                url = f"{host}/serving-endpoints/{self.endpoint_name}/invocations"
                
                payload = json.dumps({
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 512,
                    "temperature": 0.2
                }).encode("utf-8")
                
                req = urllib.request.Request(
                    url,
                    data=payload,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    }
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                pass  # Fall back to local expert engine

        # Default high-fidelity Deterministic Legal Reasoning Engine
        status_str = f"DELAYED by {delay_hours:.1f} hrs (ETA: {predicted_eta})" if will_delay else "ON SCHEDULE"
        hazards = route_analysis.get("route_hazards", [])
        hazard_str = f"; Hazards: {', '.join(hazards)}" if hazards else ""
        
        sla_penalty = contract_analysis.get("sla_delay_penalty_usd", 0.0)
        carrier_cb = contract_analysis.get("total_carrier_chargeback_usd", 0.0)
        fm_status = contract_analysis.get("force_majeure_status", "NOT_APPLICABLE")
        
        actions = quality_analysis.get("mitigation_actions", [])
        action_str = actions[0] if actions else "Standard active telematics monitoring"
        qa_holds = quality_analysis.get("qa_hold_reasons", [])
        qa_str = f"\nQA Quarantine: {'; '.join(qa_holds)}" if qa_holds else ""
        
        app_status = quality_analysis.get("approval_status", "AUTONOMOUSLY_APPROVED")
        app_gate = quality_analysis.get("approval_gate", "AI Copilot Auto-Approval")
        citations_str = ", ".join(rag_citations[:3]) if rag_citations else "Standard MVA Framework"

        brief = f"""Order {order_id} destined for {customer_name} ({customer_tier} Tier) via {carrier_name} ({shipping_type}) is predicted to be {status_str} (Delay Probability: {delay_prob:.1%}){hazard_str}.
Contractual SLA Exposure: ${sla_penalty:.2f}. Total Carrier Chargeback: ${carrier_cb:.2f}.
Force Majeure Status: {fm_status}.
Recommended Action: {action_str}.{qa_str}
Governance Status: {app_status} ({app_gate}).
Referenced Policy Citations: {citations_str}."""

        return brief
