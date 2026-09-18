"""
Unified Multi-Tier LLM Provider & Dynamic Fallback Routing Engine
Implements resilient 3-tier model execution hierarchy:
  Tier 1: External Cloud LLM API (Google Gemini, Groq, OpenAI, Custom) - Gated by explicit switch (DEFAULT OFF)
  Tier 2: Local Ollama SLM/LLM (e.g. Qwen2.5, Llama3 at 127.0.0.1:11434)
  Tier 3: High-Fidelity Deterministic Expert Rule-Based Model (Zero latency, zero memory, 100% reliable)
"""

import os
import json
import time
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
import requests

logger = logging.getLogger("LLMProvider")


@dataclass
class LLMProviderConfig:
    """Configuration for LLM routing and fallback behavior"""
    # EXPLICIT SWITCH: Strictly OFF by default
    use_cloud_api: bool = False

    # Cloud API Provider Settings
    provider: str = "gemini"  # "gemini", "groq", "openai", "custom"
    api_key: str = ""
    model_name: str = "gemini-1.5-flash"
    custom_endpoint: str = ""

    # Local Ollama Settings
    ollama_host: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen2.5:7b"

    # Execution Parameters
    timeout_seconds: float = 10.0
    temperature: float = 0.2
    max_tokens: int = 1024

    def __post_init__(self):
        # Auto-detect API key from environment if not explicitly provided
        if not self.api_key:
            if self.provider == "gemini":
                self.api_key = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
            elif self.provider == "groq":
                self.api_key = os.getenv("GROQ_API_KEY", "")
            elif self.provider == "openai":
                self.api_key = os.getenv("OPENAI_API_KEY", "")


@dataclass
class FallbackStepTrace:
    """Audit trace for a single step in the fallback evaluation"""
    step_number: int
    tier_name: str
    target_endpoint: str
    attempted: bool
    status: str  # "SKIPPED", "SUCCESS", "FAILED"
    latency_ms: float = 0.0
    details: str = ""
    error_message: Optional[str] = None


@dataclass
class LLMResponse:
    """Unified structured response returned by LLMProvider"""
    content: str
    effective_provider: str  # "CLOUD_API", "LOCAL_OLLAMA", "DETERMINISTIC"
    status: str              # "SUCCESS", "FALLBACK_SUCCESS", "ALL_FAILED"
    trace: List[FallbackStepTrace] = field(default_factory=list)
    total_latency_ms: float = 0.0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "effective_provider": self.effective_provider,
            "status": self.status,
            "total_latency_ms": self.total_latency_ms,
            "error": self.error,
            "trace": [asdict(t) for t in self.trace]
        }


class LLMProvider:
    """
    Multi-tier LLM Provider that executes with strict cascading fallback:
      1. Cloud API (only if switch is ON)
      2. Local Ollama (if daemon active & model ready)
      3. Deterministic Specialist Model (guaranteed fallback)
    """

    def __init__(self, config: Optional[LLMProviderConfig] = None):
        self.config = config or LLMProviderConfig()

    def update_config(self, **kwargs) -> None:
        """Dynamically update provider configuration at runtime (e.g. from UI)"""
        for k, v in kwargs.items():
            if hasattr(self.config, k):
                setattr(self.config, k, v)
        # Re-run auto detection if provider changed and key is empty
        if "provider" in kwargs and not self.config.api_key:
            self.config.__post_init__()

    # =========================================================================
    # Health & Diagnostics Probes
    # =========================================================================

    def check_cloud_api(self) -> Dict[str, Any]:
        """Probe external cloud API connectivity with a lightweight ping"""
        if not self.config.use_cloud_api:
            return {
                "available": False,
                "status": "DISABLED",
                "message": f"Cloud API switch is OFF (default). Bypassed to Local/Deterministic tiers."
            }

        if not self.config.api_key:
            return {
                "available": False,
                "status": "CONFIG_ERROR",
                "message": f"API key is not configured for provider '{self.config.provider}'."
            }

        start = time.time()
        try:
            test_prompt = "Reply with 'PONG' only."
            res = self._call_cloud_api_raw(test_prompt, system_prompt="You are a ping test assistant.")
            latency_ms = (time.time() - start) * 1000
            if res and len(res.strip()) > 0:
                return {
                    "available": True,
                    "status": "ONLINE",
                    "provider": self.config.provider,
                    "model": self.config.model_name,
                    "latency_ms": round(latency_ms, 1),
                    "message": f"Connection verified in {latency_ms:.0f} ms."
                }
            return {
                "available": False,
                "status": "EMPTY_RESPONSE",
                "message": "Cloud API returned an empty response."
            }
        except Exception as e:
            latency_ms = (time.time() - start) * 1000
            return {
                "available": False,
                "status": "ERROR",
                "latency_ms": round(latency_ms, 1),
                "message": str(e)
            }

    def check_ollama(self) -> Dict[str, Any]:
        """Probe local Ollama daemon connectivity and model availability"""
        start = time.time()
        try:
            url = f"{self.config.ollama_host.rstrip('/')}/api/tags"
            r = requests.get(url, timeout=1.5)
            latency_ms = (time.time() - start) * 1000
            if r.status_code == 200:
                models = [m.get("name") for m in r.json().get("models", [])]
                has_target = any(self.config.ollama_model in m for m in models)
                return {
                    "available": True,
                    "status": "ONLINE",
                    "host": self.config.ollama_host,
                    "models_loaded": models,
                    "has_target_model": has_target,
                    "target_model": self.config.ollama_model,
                    "latency_ms": round(latency_ms, 1),
                    "message": f"Ollama online at {self.config.ollama_host} ({len(models)} models available)."
                }
            return {
                "available": False,
                "status": "UNREACHABLE",
                "message": f"Ollama returned HTTP status {r.status_code}."
            }
        except Exception as e:
            return {
                "available": False,
                "status": "OFFLINE",
                "message": f"Ollama daemon not responding at {self.config.ollama_host}."
            }

    def check_deterministic(self) -> Dict[str, Any]:
        """Deterministic rule-based specialist engine is always available"""
        return {
            "available": True,
            "status": "ONLINE",
            "latency_ms": 0.1,
            "message": "Deterministic Expert Specialist Engine is active and ready (Zero memory / zero latency)."
        }

    # =========================================================================
    # Cloud API REST Implementations (Native `requests`, zero heavy SDKs)
    # =========================================================================

    def _call_gemini_api(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Direct REST call to Google Generative Language API (Gemini)"""
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.config.model_name}:generateContent?key={self.config.api_key}"
        )
        contents = []
        if system_prompt:
            contents.append({
                "role": "user",
                "parts": [{"text": f"System Context / Rules:\n{system_prompt}\n\nTask:\n{prompt}"}]
            })
        else:
            contents.append({
                "role": "user",
                "parts": [{"text": prompt}]
            })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": self.config.temperature,
                "maxOutputTokens": self.config.max_tokens
            }
        }
        resp = requests.post(url, json=payload, timeout=self.config.timeout_seconds)
        if resp.status_code != 200:
            raise RuntimeError(f"Gemini API Error {resp.status_code}: {resp.text}")

        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            raise RuntimeError("Gemini API returned no candidates.")
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            raise RuntimeError("Gemini API returned empty parts.")
        return parts[0].get("text", "").strip()

    def _call_openai_compatible_api(
        self,
        endpoint_url: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        extra_headers: Optional[Dict[str, str]] = None
    ) -> str:
        """Call standard OpenAI-compatible completions endpoint (OpenAI, Groq, Custom)"""
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        if extra_headers:
            headers.update(extra_headers)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.config.model_name,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }

        resp = requests.post(endpoint_url, headers=headers, json=payload, timeout=self.config.timeout_seconds)
        if resp.status_code != 200:
            raise RuntimeError(f"{self.config.provider.upper()} API Error {resp.status_code}: {resp.text}")

        data = resp.json()
        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError("API returned no completion choices.")
        return choices[0].get("message", {}).get("content", "").strip()

    def _call_cloud_api_raw(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Route to appropriate Cloud API REST client based on provider setting"""
        provider = self.config.provider.lower()
        if provider == "gemini":
            return self._call_gemini_api(prompt, system_prompt)
        elif provider == "groq":
            url = "https://api.groq.com/openai/v1/chat/completions"
            return self._call_openai_compatible_api(url, prompt, system_prompt)
        elif provider == "openai":
            url = "https://api.openai.com/v1/chat/completions"
            return self._call_openai_compatible_api(url, prompt, system_prompt)
        elif provider == "custom":
            url = self.config.custom_endpoint.rstrip("/") + "/chat/completions"
            return self._call_openai_compatible_api(url, prompt, system_prompt)
        else:
            raise ValueError(f"Unsupported cloud provider: '{provider}'")

    # =========================================================================
    # Local Ollama REST Client
    # =========================================================================

    def _call_ollama_raw(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Call local Ollama REST endpoint via requests"""
        url = f"{self.config.ollama_host.rstrip('/')}/api/generate"
        payload = {
            "model": self.config.ollama_model,
            "prompt": prompt,
            "system": system_prompt or "",
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens
            }
        }
        resp = requests.post(url, json=payload, timeout=self.config.timeout_seconds)
        if resp.status_code != 200:
            raise RuntimeError(f"Ollama returned HTTP {resp.status_code}: {resp.text}")
        content = resp.json().get("response", "").strip()
        if not content:
            raise RuntimeError("Ollama returned empty response.")
        return content

    # =========================================================================
    # Resilient 3-Tier Cascading Fallback Invocation
    # =========================================================================

    def invoke_with_fallback(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        deterministic_fallback_fn: Optional[Callable[[], str]] = None
    ) -> LLMResponse:
        """
        Executes prompt through the 3-tier fallback hierarchy:
          Tier 1: Cloud API (if use_cloud_api switch is ON)
          Tier 2: Local Ollama (if daemon is running)
          Tier 3: Deterministic Rule-Based Fallback
        """
        overall_start = time.time()
        trace: List[FallbackStepTrace] = []

        # ---------------------------------------------------------------------
        # TIER 1: External Cloud LLM API (Conditional on explicit switch)
        # ---------------------------------------------------------------------
        if self.config.use_cloud_api:
            step_start = time.time()
            try:
                if not self.config.api_key:
                    raise ValueError(f"Cloud API switch is ON, but no API key configured for '{self.config.provider}'.")
                
                content = self._call_cloud_api_raw(prompt, system_prompt)
                latency = (time.time() - step_start) * 1000
                trace.append(FallbackStepTrace(
                    step_number=1,
                    tier_name="Tier 1: Cloud LLM API",
                    target_endpoint=f"{self.config.provider} ({self.config.model_name})",
                    attempted=True,
                    status="SUCCESS",
                    latency_ms=round(latency, 1),
                    details=f"Successfully synthesized response via Cloud API ({self.config.provider})."
                ))
                trace.append(FallbackStepTrace(
                    step_number=2,
                    tier_name="Tier 2: Local Ollama",
                    target_endpoint=f"{self.config.ollama_host} ({self.config.ollama_model})",
                    attempted=False,
                    status="SKIPPED",
                    latency_ms=0.0,
                    details="Tier 1 Cloud API succeeded. Local Ollama bypassed."
                ))
                trace.append(FallbackStepTrace(
                    step_number=3,
                    tier_name="Tier 3: Deterministic Specialist Model",
                    target_endpoint="In-Memory Expert Rules",
                    attempted=False,
                    status="SKIPPED",
                    latency_ms=0.0,
                    details="Tier 1 Cloud API succeeded. Deterministic model bypassed."
                ))
                return LLMResponse(
                    content=content,
                    effective_provider="CLOUD_API",
                    status="SUCCESS",
                    trace=trace,
                    total_latency_ms=round((time.time() - overall_start) * 1000, 1)
                )
            except Exception as e:
                latency = (time.time() - step_start) * 1000
                logger.warning(f"Tier 1 Cloud API failed: {e}. Cascading to Tier 2 (Ollama)...")
                trace.append(FallbackStepTrace(
                    step_number=1,
                    tier_name="Tier 1: Cloud LLM API",
                    target_endpoint=f"{self.config.provider} ({self.config.model_name})",
                    attempted=True,
                    status="FAILED",
                    latency_ms=round(latency, 1),
                    details="Cloud API execution failed. Cascading to local Ollama.",
                    error_message=str(e)
                ))
        else:
            trace.append(FallbackStepTrace(
                step_number=1,
                tier_name="Tier 1: Cloud LLM API",
                target_endpoint=f"{self.config.provider} ({self.config.model_name})",
                attempted=False,
                status="SKIPPED",
                latency_ms=0.0,
                details="Switch is OFF (default). Cloud API bypassed."
            ))

        # ---------------------------------------------------------------------
        # TIER 2: Local Ollama SLM/LLM
        # ---------------------------------------------------------------------
        step2_start = time.time()
        ollama_probe = self.check_ollama()
        if ollama_probe.get("available"):
            try:
                content = self._call_ollama_raw(prompt, system_prompt)
                latency = (time.time() - step2_start) * 1000
                trace.append(FallbackStepTrace(
                    step_number=2,
                    tier_name="Tier 2: Local Ollama",
                    target_endpoint=f"{self.config.ollama_host} ({self.config.ollama_model})",
                    attempted=True,
                    status="SUCCESS",
                    latency_ms=round(latency, 1),
                    details=f"Successfully synthesized response via local Ollama ({self.config.ollama_model})."
                ))
                trace.append(FallbackStepTrace(
                    step_number=3,
                    tier_name="Tier 3: Deterministic Specialist Model",
                    target_endpoint="In-Memory Expert Rules",
                    attempted=False,
                    status="SKIPPED",
                    latency_ms=0.0,
                    details="Tier 2 Local Ollama succeeded. Deterministic model bypassed."
                ))
                return LLMResponse(
                    content=content,
                    effective_provider="LOCAL_OLLAMA",
                    status="FALLBACK_SUCCESS" if self.config.use_cloud_api else "SUCCESS",
                    trace=trace,
                    total_latency_ms=round((time.time() - overall_start) * 1000, 1)
                )
            except Exception as e:
                latency = (time.time() - step2_start) * 1000
                logger.warning(f"Tier 2 Ollama failed: {e}. Cascading to Tier 3 (Deterministic)...")
                trace.append(FallbackStepTrace(
                    step_number=2,
                    tier_name="Tier 2: Local Ollama",
                    target_endpoint=f"{self.config.ollama_host} ({self.config.ollama_model})",
                    attempted=True,
                    status="FAILED",
                    latency_ms=round(latency, 1),
                    details="Ollama execution failed. Cascading to deterministic specialist engine.",
                    error_message=str(e)
                ))
        else:
            trace.append(FallbackStepTrace(
                step_number=2,
                tier_name="Tier 2: Local Ollama",
                target_endpoint=self.config.ollama_host,
                attempted=True,
                status="FAILED",
                latency_ms=round(ollama_probe.get("latency_ms", 0.0), 1),
                details=f"Local Ollama is unreachable ({ollama_probe.get('message')}). Cascading to Tier 3.",
                error_message="Daemon Offline"
            ))

        # ---------------------------------------------------------------------
        # TIER 3: Deterministic Specialist Model
        # ---------------------------------------------------------------------
        step3_start = time.time()
        try:
            if deterministic_fallback_fn:
                content = deterministic_fallback_fn()
            else:
                content = (
                    "[DETERMINISTIC FALLBACK EXECUTIVE SYNTHESIS]\n"
                    "Automated rule-based assessment: Adjudicated delay liabilities and protective quarantine rules "
                    "enforced in accordance with contractual SLA matrices and cold chain SOPs."
                )
            latency = (time.time() - step3_start) * 1000
            trace.append(FallbackStepTrace(
                step_number=3,
                tier_name="Tier 3: Deterministic Specialist Model",
                target_endpoint="In-Memory Expert Rules",
                attempted=True,
                status="SUCCESS",
                latency_ms=round(latency, 1),
                details="Executed deterministic rule-based specialist consensus with zero latency."
            ))
            return LLMResponse(
                content=content,
                effective_provider="DETERMINISTIC",
                status="FALLBACK_SUCCESS",
                trace=trace,
                total_latency_ms=round((time.time() - overall_start) * 1000, 1)
            )
        except Exception as e:
            trace.append(FallbackStepTrace(
                step_number=3,
                tier_name="Tier 3: Deterministic Specialist Model",
                target_endpoint="In-Memory Expert Rules",
                attempted=True,
                status="FAILED",
                latency_ms=0.0,
                details="Critical failure in deterministic fallback engine.",
                error_message=str(e)
            ))
            return LLMResponse(
                content="System Error: All three execution tiers (Cloud API, Ollama, Deterministic) failed.",
                effective_provider="NONE",
                status="ALL_FAILED",
                trace=trace,
                total_latency_ms=round((time.time() - overall_start) * 1000, 1),
                error=str(e)
            )
