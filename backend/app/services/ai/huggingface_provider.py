import time
import json
import logging
from typing import Dict, Any, Optional, List
import requests
from app.services.ai.base import BaseAIProvider, ProviderHealth, LLMOutput
from app.services.ai.schemas import extract_and_validate_json

logger = logging.getLogger(__name__)

HF_MODELS = [
    "mistralai/Mistral-7B-Instruct-v0.2",
    "meta-llama/Meta-Llama-3-8B-Instruct",
    "Qwen/Qwen2.5-7B-Instruct"
]

class HuggingFaceProvider(BaseAIProvider):
    def __init__(self, api_key: Optional[str] = None, selected_model: Optional[str] = None):
        self.api_key = api_key or ""
        self.selected_model = selected_model or "mistralai/Mistral-7B-Instruct-v0.2"
        self.endpoint = "https://api-inference.huggingface.co/models"

    def get_provider_name(self) -> str:
        return "huggingface"

    def list_available_models(self) -> List[str]:
        return HF_MODELS

    def check_health(self) -> ProviderHealth:
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        if not self.api_key:
            return ProviderHealth(
                provider_name="huggingface",
                status="unconfigured",
                message="No Hugging Face token configured (free token from https://huggingface.co/settings/tokens).",
                endpoint=self.endpoint,
                available_models=HF_MODELS,
                last_checked=now_str
            )
        try:
            resp = requests.get(
                "https://huggingface.co/api/whoami-v2",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=2.5
            )
            if resp.status_code == 200:
                return ProviderHealth(
                    provider_name="huggingface",
                    status="connected",
                    message="Hugging Face Inference Provider connected.",
                    endpoint=self.endpoint,
                    current_model=self.selected_model,
                    available_models=HF_MODELS,
                    last_checked=now_str
                )
            return ProviderHealth(
                provider_name="huggingface",
                status="error",
                message=f"Hugging Face returned HTTP {resp.status_code}",
                endpoint=self.endpoint,
                last_checked=now_str
            )
        except Exception as e:
            return ProviderHealth(
                provider_name="huggingface",
                status="offline",
                message=f"Hugging Face connection error: {str(e)}",
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
                provider_used="huggingface",
                model_used=self.selected_model,
                error="Hugging Face token not provided."
            )

        target_model = model or self.selected_model
        url = f"{self.endpoint}/{target_model}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "inputs": f"<s>[INST] {system_prompt}\n\nRespond ONLY in valid JSON matching the required schema.\n\n{prompt} [/INST]",
            "parameters": {"max_new_tokens": 1024, "temperature": 0.3, "return_full_text": False}
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout_seconds)
            elapsed_ms = int((time.time() - start_time) * 1000)
            if resp.status_code == 200:
                data = resp.json()
                raw_text = data[0].get("generated_text", "") if isinstance(data, list) else str(data)
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
                    provider_used="huggingface",
                    model_used=target_model,
                    latency_ms=elapsed_ms
                )
            return LLMOutput(
                raw_text="",
                is_fallback=True,
                provider_used="huggingface",
                model_used=target_model,
                latency_ms=elapsed_ms,
                error=f"HF HTTP {resp.status_code}: {resp.text}"
            )
        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return LLMOutput(
                raw_text="",
                is_fallback=True,
                provider_used="huggingface",
                model_used=target_model,
                latency_ms=elapsed_ms,
                error=f"Hugging Face request failed: {str(e)}"
            )
