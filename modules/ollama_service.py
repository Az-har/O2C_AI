"""
Ollama LLM Service for Local Autonomous AI Generation
Integrates with local Ollama instance (e.g. Qwen2.5, Llama3) for dynamic intelligence document synthesis.
Includes automatic health-checking and graceful fallback.
"""

import os
import requests
import json
from typing import Optional, Dict, Any

class OllamaService:
    """Local LLM client interfacing with Ollama REST API"""

    DEFAULT_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

    def __init__(self, host: str = DEFAULT_HOST, model: str = DEFAULT_MODEL, timeout: int = 45):
        self.host = host.rstrip("/")
        self.model = model
        self.timeout = timeout
        self._is_available = None

    def is_available(self) -> bool:
        """Check if local Ollama daemon is reachable and model is loaded"""
        if self._is_available is not None:
            return self._is_available

        try:
            r = requests.get(f"{self.host}/api/tags", timeout=2)
            if r.status_code == 200:
                models = [m.get("name") for m in r.json().get("models", [])]
                # Match exact or prefix (e.g. 'qwen2.5:7b' or 'qwen2.5')
                has_model = any(self.model in m or m.startswith(self.model.split(":")[0]) for m in models)
                if has_model:
                    self._is_available = True
                    return True
                # If specific model not found but other models exist, pick the first available
                elif models:
                    self.model = models[0]
                    self._is_available = True
                    return True
            self._is_available = False
            return False
        except Exception:
            self._is_available = False
            return False

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """
        Generate text completion via Ollama.
        Returns generated string or None on failure/timeout.
        """
        if not self.is_available():
            return None

        url = f"{self.host}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.9,
                "num_predict": 1024
            }
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            r = requests.post(url, json=payload, timeout=self.timeout)
            if r.status_code == 200:
                return r.json().get("response", "").strip()
            return None
        except Exception as e:
            return None
