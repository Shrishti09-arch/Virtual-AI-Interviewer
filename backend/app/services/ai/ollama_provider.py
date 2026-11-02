import time
import json
import logging
from typing import Dict, Any, Optional, List
import requests
from app.services.ai.base import BaseAIProvider, ProviderHealth, LLMOutput
from app.services.ai.schemas import extract_and_validate_json

logger = logging.getLogger(__name__)

# Priority order for models to auto-select
PREFERRED_OLLAMA_MODELS = [
    "qwen3:8b",
    "llama3.1:8b",
    "mistral:7b",
    "qwen2.5:8b",
    "llama3.1:latest",
    "llama3:8b",
    "llama3:latest",
    "mistral:latest",
    "qwen2.5:latest"
]

class OllamaProvider(BaseAIProvider):
    def __init__(self, endpoint: str = "http://localhost:11434", selected_model: Optional[str] = None):
        self.endpoint = endpoint.rstrip("/")
        self.selected_model = selected_model
        self.max_retries = 2
        self.retry_delay_seconds = 1.0

    def get_provider_name(self) -> str:
        return "ollama"

    def list_available_models(self) -> List[str]:
        try:
            resp = requests.get(f"{self.endpoint}/api/tags", timeout=2.5)
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name") for m in data.get("models", []) if m.get("name")]
                return models
        except Exception as e:
            logger.debug(f"Failed to list Ollama models: {e}")
        return []

    def select_best_model(self, available_models: List[str]) -> Optional[str]:
        if not available_models:
            return None
        # If user explicitly selected a model that exists, keep it
        if self.selected_model and any(self.selected_model in m for m in available_models):
            return self.selected_model

        # Auto-select by preference priority
        for pref in PREFERRED_OLLAMA_MODELS:
            for avail in available_models:
                if pref in avail or avail.startswith(pref.split(":")[0]):
                    return avail

        # Otherwise pick the first installed model
        return available_models[0]

    def check_health(self) -> ProviderHealth:
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            resp = requests.get(f"{self.endpoint}/api/tags", timeout=2.0)
            if resp.status_code != 200:
                return ProviderHealth(
                    provider_name="ollama",
                    status="offline",
                    message=f"Ollama returned HTTP error code {resp.status_code}",
                    endpoint=self.endpoint,
                    last_checked=now_str,
                    install_instructions=self.get_install_instructions()
                )

            data = resp.json()
            models = [m.get("name") for m in data.get("models", []) if m.get("name")]
            
            if not models:
                return ProviderHealth(
                    provider_name="ollama",
                    status="no_models",
                    message="Ollama is running, but no models are currently installed.",
                    endpoint=self.endpoint,
                    available_models=[],
                    last_checked=now_str,
                    install_instructions=(
                        "Ollama is running! To download a recommended model, open PowerShell and run:\n"
                        "  ollama run llama3.1:8b\n"
                        "or:\n"
                        "  ollama run qwen2.5:8b\n"
                        "  ollama run mistral:7b"
                    )
                )

            best_model = self.select_best_model(models)
            self.selected_model = best_model

            return ProviderHealth(
                provider_name="ollama",
                status="connected",
                message=f"Ollama is online and verified with {len(models)} installed model(s).",
                endpoint=self.endpoint,
                current_model=best_model,
                available_models=models,
                last_checked=now_str
            )

        except requests.exceptions.ConnectionError:
            return ProviderHealth(
                provider_name="ollama",
                status="offline",
                message="Cannot connect to Ollama daemon on http://localhost:11434. Service is not running.",
                endpoint=self.endpoint,
                last_checked=now_str,
                install_instructions=self.get_install_instructions()
            )
        except requests.exceptions.Timeout:
            return ProviderHealth(
                provider_name="ollama",
                status="offline",
                message="Connection timed out while reaching Ollama.",
                endpoint=self.endpoint,
                last_checked=now_str,
                install_instructions=self.get_install_instructions()
            )
        except Exception as e:
            return ProviderHealth(
                provider_name="ollama",
                status="offline",
                message=f"Error checking Ollama status: {str(e)}",
                endpoint=self.endpoint,
                last_checked=now_str,
                install_instructions=self.get_install_instructions()
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
        
        # Determine model
        target_model = model or self.selected_model
        if not target_model:
            available = self.list_available_models()
            target_model = self.select_best_model(available)
            self.selected_model = target_model

        if not target_model:
            return LLMOutput(
                raw_text="",
                is_fallback=True,
                provider_used="ollama",
                model_used="none",
                error="Ollama has no models installed. Please install a model using 'ollama run llama3.1:8b'."
            )

        # Build payload with format="json" for guaranteed JSON output mode in Ollama
        full_system = (
            f"{system_prompt}\n"
            "CRITICAL INSTRUCTION: You MUST output ONLY valid JSON without any markdown formatting, backticks, or preamble."
        )

        payload = {
            "model": target_model,
            "prompt": prompt,
            "system": full_system,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.3,
                "top_p": 0.9,
            }
        }

        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                resp = requests.post(
                    f"{self.endpoint}/api/generate",
                    json=payload,
                    timeout=timeout_seconds
                )
                if resp.status_code == 200:
                    data = resp.json()
                    response_text = data.get("response", "").strip()
                    elapsed_ms = int((time.time() - start_time) * 1000)

                    if not response_text:
                        raise ValueError("Ollama returned empty response string")

                    # If schema is provided, validate with Pydantic
                    structured = None
                    if schema_cls:
                        validated_obj = extract_and_validate_json(response_text, schema_cls)
                        structured = validated_obj.model_dump()
                    else:
                        structured = json.loads(response_text)

                    return LLMOutput(
                        raw_text=response_text,
                        structured_data=structured,
                        is_fallback=False,
                        provider_used="ollama",
                        model_used=target_model,
                        latency_ms=elapsed_ms
                    )
                else:
                    last_error = f"Ollama HTTP {resp.status_code}: {resp.text}"

            except requests.exceptions.Timeout:
                last_error = f"Ollama generation timed out after {timeout_seconds}s"
            except requests.exceptions.ConnectionError:
                last_error = f"Failed to connect to Ollama at {self.endpoint}"
                break # Don't retry if connection refused
            except Exception as e:
                last_error = f"Ollama error on attempt {attempt + 1}: {str(e)}"

            if attempt < self.max_retries:
                time.sleep(self.retry_delay_seconds)

        elapsed_ms = int((time.time() - start_time) * 1000)
        return LLMOutput(
            raw_text="",
            is_fallback=True,
            provider_used="ollama",
            model_used=target_model or "unknown",
            latency_ms=elapsed_ms,
            error=last_error
        )

    @staticmethod
    def get_install_instructions() -> str:
        return (
            "Windows Installation Instructions for Ollama:\n\n"
            "1. Using Windows Package Manager (PowerShell):\n"
            "   winget install Ollama.Ollama\n\n"
            "2. Or Download Installer directly:\n"
            "   Visit https://ollama.com/download/windows and run OllamaSetup.exe\n\n"
            "3. Pull and run a high-performance career coach model:\n"
            "   ollama run llama3.1:8b\n"
            "   (Alternative: ollama run qwen2.5:8b or ollama run mistral:7b)\n\n"
            "4. Verify Ollama is running in background at http://localhost:11434"
        )
