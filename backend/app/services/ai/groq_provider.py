import time
import json
import logging
from typing import Dict, Any, Optional, List
import requests
from app.services.ai.base import BaseAIProvider, ProviderHealth, LLMOutput
from app.services.ai.schemas import extract_and_validate_json

logger = logging.getLogger(__name__)

GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
    "gemma2-9b-it"
]

class GroqProvider(BaseAIProvider):
    def __init__(self, api_key: Optional[str] = None, selected_model: Optional[str] = None):
        self.api_key = api_key or ""
        self.selected_model = selected_model or "llama-3.3-70b-versatile"
        self.endpoint = "https://api.groq.com/openai/v1"

    def get_provider_name(self) -> str:
        return "groq"

    def list_available_models(self) -> List[str]:
        return GROQ_MODELS

    def check_health(self) -> ProviderHealth:
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        if not self.api_key:
            return ProviderHealth(
                provider_name="groq",
                status="unconfigured",
                message="No Groq API key set. Free Groq API keys can be generated at https://console.groq.com.",
                endpoint=self.endpoint,
                available_models=GROQ_MODELS,
                last_checked=now_str
            )
        try:
            resp = requests.get(
                f"{self.endpoint}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=2.5
            )
            if resp.status_code == 200:
                return ProviderHealth(
                    provider_name="groq",
                    status="connected",
                    message="Groq Free Models API is online and authenticated.",
                    endpoint=self.endpoint,
                    current_model=self.selected_model,
                    available_models=GROQ_MODELS,
                    last_checked=now_str
                )
            return ProviderHealth(
                provider_name="groq",
                status="error",
                message=f"Groq API returned HTTP {resp.status_code}: Invalid API key or quota exceeded.",
                endpoint=self.endpoint,
                last_checked=now_str
            )
        except Exception as e:
            return ProviderHealth(
                provider_name="groq",
                status="offline",
                message=f"Could not connect to Groq: {str(e)}",
                endpoint=self.endpoint,
                last_checked=now_str
            )

    def generate_structured(
        self,
        prompt: str,
        system_prompt: str,
        schema_cls: Optional[Any] = None,
        model: Optional[str] = None,
        timeout_seconds: float = 15.0
    ) -> LLMOutput:
        start_time = time.time()
        if not self.api_key:
            return LLMOutput(
                raw_text="",
                is_fallback=True,
                provider_used="groq",
                model_used=self.selected_model,
                error="Missing Groq API Key."
            )

        target_model = model or self.selected_model
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": target_model,
            "messages": [
                {"role": "system", "content": f"{system_prompt}\nCRITICAL: Output valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
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
                    provider_used="groq",
                    model_used=target_model,
                    latency_ms=elapsed_ms
                )
            return LLMOutput(
                raw_text="",
                is_fallback=True,
                provider_used="groq",
                model_used=target_model,
                latency_ms=elapsed_ms,
                error=f"Groq API HTTP {resp.status_code}: {resp.text}"
            )
        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return LLMOutput(
                raw_text="",
                is_fallback=True,
                provider_used="groq",
                model_used=target_model,
                latency_ms=elapsed_ms,
                error=f"Groq generation failed: {str(e)}"
            )
