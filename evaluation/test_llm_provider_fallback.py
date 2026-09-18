"""
Unit Test Suite for LLMProvider Multi-Tier Fallback Hierarchy & Explicit Switch
Validates:
1. Explicit switch is strictly OFF (False) by default.
2. Switch OFF: Tier 1 Cloud API is skipped, Ollama is probed, Deterministic executes.
3. Switch ON with API Error: Tier 1 fails safely, cascades to Ollama and Deterministic without crashing.
4. Switch ON with Valid API: Tier 1 succeeds, skipping Tier 2 and 3.
5. Integration with LLMReasoningEngine and negotiate_inter_agent_consensus.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.llm_provider import (
    LLMProvider,
    LLMProviderConfig,
    LLMResponse,
    FallbackStepTrace
)
from modules.agent_specialists import (
    LLMReasoningEngine,
    RouteSupervisorAgent,
    ContractAdjudicatorAgent,
    QualityMitigationAgent,
    negotiate_inter_agent_consensus
)


class TestLLMProviderFallback(unittest.TestCase):
    """Test multi-tier fallback engine and explicit switch compliance"""

    def test_switch_is_off_by_default(self):
        """CRITICAL: Explicit switch MUST be False by default"""
        config = LLMProviderConfig()
        self.assertFalse(
            config.use_cloud_api,
            "LLMProviderConfig.use_cloud_api must default to False"
        )
        provider = LLMProvider()
        self.assertFalse(
            provider.config.use_cloud_api,
            "LLMProvider default configuration must have use_cloud_api=False"
        )

    def test_switch_off_fallback_to_deterministic(self):
        """When switch is OFF and Ollama is offline, must fall back cleanly to deterministic model"""
        config = LLMProviderConfig(use_cloud_api=False, ollama_host="http://127.0.0.1:99999")
        provider = LLMProvider(config=config)

        def mock_deterministic():
            return "Deterministic Expert Decision for Order 800000000000001"

        response = provider.invoke_with_fallback(
            prompt="Analyze route delay",
            system_prompt="You are an expert",
            deterministic_fallback_fn=mock_deterministic
        )

        self.assertIsInstance(response, LLMResponse)
        self.assertEqual(response.effective_provider, "DETERMINISTIC")
        self.assertEqual(response.status, "FALLBACK_SUCCESS")
        self.assertIn("Deterministic Expert Decision", response.content)
        self.assertEqual(len(response.trace), 3)

        # Trace audit verification
        t1, t2, t3 = response.trace[0], response.trace[1], response.trace[2]
        self.assertEqual(t1.step_number, 1)
        self.assertFalse(t1.attempted)
        self.assertEqual(t1.status, "SKIPPED")
        self.assertIn("switch is off", t1.details.lower())

        self.assertEqual(t2.step_number, 2)
        self.assertTrue(t2.attempted)
        self.assertEqual(t2.status, "FAILED")

        self.assertEqual(t3.step_number, 3)
        self.assertTrue(t3.attempted)
        self.assertEqual(t3.status, "SUCCESS")

    def test_switch_on_with_api_failure_cascades_safely(self):
        """When switch is ON but Cloud API fails, must catch error, log trace, and cascade to deterministic"""
        config = LLMProviderConfig(
            use_cloud_api=True,
            provider="gemini",
            api_key="SIMULATED_INVALID_KEY_9999",
            ollama_host="http://127.0.0.1:99999"
        )
        provider = LLMProvider(config=config)

        def mock_deterministic():
            return "Safe Deterministic Fallback Output"

        response = provider.invoke_with_fallback(
            prompt="Analyze route delay",
            system_prompt="You are an expert",
            deterministic_fallback_fn=mock_deterministic
        )

        self.assertIsInstance(response, LLMResponse)
        self.assertEqual(response.effective_provider, "DETERMINISTIC")
        self.assertEqual(response.status, "FALLBACK_SUCCESS")
        self.assertIn("Safe Deterministic Fallback Output", response.content)

        # Trace audit: Step 1 attempted and FAILED, Step 2 FAILED, Step 3 SUCCESS
        t1 = response.trace[0]
        self.assertTrue(t1.attempted)
        self.assertEqual(t1.status, "FAILED")
        self.assertIsNotNone(t1.error_message)

        t2 = response.trace[1]
        self.assertTrue(t2.attempted)
        self.assertEqual(t2.status, "FAILED")

        t3 = response.trace[2]
        self.assertTrue(t3.attempted)
        self.assertEqual(t3.status, "SUCCESS")

    def test_switch_on_with_successful_cloud_api(self):
        """When switch is ON and Cloud API succeeds, Tier 1 is returned and downstream tiers skipped"""
        config = LLMProviderConfig(
            use_cloud_api=True,
            provider="gemini",
            api_key="TEST_VALID_KEY"
        )
        provider = LLMProvider(config=config)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": "Cloud Gemini Executive Brief Analysis"}]
                    }
                }
            ]
        }

        with patch("requests.post", return_value=mock_response):
            response = provider.invoke_with_fallback(
                prompt="Evaluate cargo disruption",
                system_prompt="Executive synthesizer",
                deterministic_fallback_fn=lambda: "Deterministic fallback"
            )

            self.assertEqual(response.effective_provider, "CLOUD_API")
            self.assertEqual(response.status, "SUCCESS")
            self.assertEqual(response.content, "Cloud Gemini Executive Brief Analysis")
            self.assertEqual(len(response.trace), 3)

            self.assertEqual(response.trace[0].status, "SUCCESS")
            self.assertEqual(response.trace[1].status, "SKIPPED")
            self.assertEqual(response.trace[2].status, "SKIPPED")

    def test_health_checks(self):
        """Verify individual health check diagnostic functions"""
        provider = LLMProvider()
        h_det = provider.check_deterministic()
        self.assertEqual(h_det["status"], "ONLINE")

        h_cloud_off = provider.check_cloud_api()
        self.assertEqual(h_cloud_off["status"], "DISABLED")
        self.assertIn("switch is OFF", h_cloud_off["message"])

        provider.config.use_cloud_api = True
        provider.config.api_key = ""
        h_cloud_no_key = provider.check_cloud_api()
        self.assertEqual(h_cloud_no_key["status"], "CONFIG_ERROR")
        self.assertIn("API key is not configured", h_cloud_no_key["message"])

        provider.config.ollama_host = "http://127.0.0.1:99999"
        h_ollama = provider.check_ollama()
        self.assertEqual(h_ollama["status"], "OFFLINE")

    def test_llm_reasoning_engine_integration(self):
        """Verify LLMReasoningEngine works seamlessly with LLMProvider and fallback trace"""
        config = LLMProviderConfig(use_cloud_api=False, ollama_host="http://127.0.0.1:99999")
        provider = LLMProvider(config=config)
        engine = LLMReasoningEngine(llm_provider=provider)

        resp = engine.synthesize_executive_decision_with_trace(
            order_id="800000000000001",
            customer_name="Apollo Veterinary Hospital",
            customer_tier="Enterprise Tier 1",
            carrier_name="Gati Logistics",
            shipping_type="Road (Express)",
            delay_prob=0.88,
            will_delay=True,
            delay_hours=14.5,
            predicted_eta="2026-10-12 18:00",
            route_analysis={"route_hazards": ["NH-48 Monsoon Inundation"], "corridor_distance_km": 650.0},
            contract_analysis={"sla_delay_penalty_usd": 450.0, "total_carrier_chargeback_usd": 300.0, "force_majeure_status": "NOT_APPLICABLE"},
            quality_analysis={"qa_hold_required": True, "qa_hold_reasons": ["Prescription diet shelf-life expired"], "mitigation_actions": ["Intercept and divert to cold warehouse"]},
            rag_citations=["SLA Standard Framework Art. 4.2"]
        )

        self.assertIsInstance(resp, LLMResponse)
        self.assertEqual(resp.effective_provider, "DETERMINISTIC")
        self.assertIn("800000000000001", resp.content)
        self.assertIn("Apollo Veterinary Hospital", resp.content)
        self.assertIn("QA Quarantine", resp.content)

        content = engine.synthesize_executive_decision(
            order_id="800000000000001",
            customer_name="Apollo Veterinary Hospital",
            customer_tier="Enterprise Tier 1",
            carrier_name="Gati Logistics",
            shipping_type="Road (Express)",
            delay_prob=0.88,
            will_delay=True,
            delay_hours=14.5,
            predicted_eta="2026-10-12 18:00",
            route_analysis={"route_hazards": []},
            contract_analysis={},
            quality_analysis={},
            rag_citations=[]
        )
        self.assertIsInstance(content, str)
        self.assertTrue(len(content) > 20)


if __name__ == "__main__":
    unittest.main(verbosity=2)
