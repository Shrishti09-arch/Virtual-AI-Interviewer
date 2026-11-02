import time
import json
import logging
from typing import Dict, Any, Optional, List
import requests
from app.services.ai.base import BaseAIProvider, ProviderHealth, LLMOutput
from app.services.ai.schemas import extract_and_validate_json

logger = logging.getLogger(__name__)

class LMStudioProvider(BaseAIProvider):
    def __init__(self, endpoint: str = "http://localhost:1234/v1", selected_model: Optional[str] = None):
        self.endpoint = endpoint.rstrip("/")
        self.selected_model = selected_model
        self.max_retries = 1

    def get_provider_name(self) -> str:
        return "lmstudio"

    def list_available_models(self) -> List[str]:
        try:
            resp = requests.get(f"{self.endpoint}/models", timeout=2.0)
            if resp.status_code == 200:
                data = resp.json()
                return [m.get("id") for m in data.get("data", []) if m.get("id")]
        except Exception:
            pass
        return []

    def check_health(self) -> ProviderHealth:
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            resp = requests.get(f"{self.endpoint}/models", timeout=2.0)
            if resp.status_code == 200:
                models = self.list_available_models()
                current = self.selected_model or (models[0] if models else "local-model")
                return ProviderHealth(
                    provider_name="lmstudio",
                    status="connected",
                    message="LM Studio local server is online.",
                    endpoint=self.endpoint,
                    current_model=current,
                    available_models=models,
                    last_checked=now_str
                )
            return ProviderHealth(
                provider_name="lmstudio",
                status="offline",
                message=f"LM Studio returned status {resp.status_code}",
                endpoint=self.endpoint,
                last_checked=now_str
            )
        except Exception as e:
            return ProviderHealth(
                provider_name="lmstudio",
                status="offline",
                message="Cannot reach LM Studio at http://localhost:1234. Ensure LM Studio Local Server is started.",
                endpoint=self.endpoint,
                last_checked=now_str,
                install_instructions="Download LM Studio from https://lmstudio.ai, load a model (e.g., Llama-3.1 or Mistral), and click 'Start Server' on port 1234."
            )

    def generate_structured(
        self,
        prompt: str,
        system_prompt: str,
        schema_cls: Optional[Any] = None,
        model: Optional[str] = None,
        timeout_seconds: float = 20.0
    ) -> LLMOutput:
        start_time = time.time()
        target_model = model or self.selected_model or "local-model"

        headers = {"Content-Type": "application/json"}
        payload = {
            "model": target_model,
            "messages": [
                {"role": "system", "content": f"{system_prompt}\nYou MUST output valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }

        try:
            resp = requests.post(f"{self.endpoint}/chat/completions", headers=headers, json=payload, timeout=timeout_seconds)
            elapsed_ms = int((time.time() - start_time) * 1000)
            if resp.status_code == 200:
                data = resp.json()
                raw_text = data["choices"][0]["message"]["content"]
                structured = None
                if schema_cls:
                    validated_obj = extract_and_validate_json(raw_text, schema_cls)
                    structured = validated_obj.model_dump()
                else:
                    structured = json.loads(raw_text)

                return LLMOutput(
                    raw_text=raw_text,
                    structured_data=structured,
                    is_fallback=False,
                    provider_used="lmstudio",
                    model_used=target_model,
                    latency_ms=elapsed_ms
                )
            return LLMOutput(
                raw_text="",
                is_fallback=True,
                provider_used="lmstudio",
                model_used=target_model,
                latency_ms=elapsed_ms,
                error=f"LM Studio HTTP {resp.status_code}: {resp.text}"
            )
        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return LLMOutput(
                raw_text="",
                is_fallback=True,
                provider_used="lmstudio",
                model_used=target_model,
                latency_ms=elapsed_ms,
                error=f"LM Studio request failed: {str(e)}"
            )
