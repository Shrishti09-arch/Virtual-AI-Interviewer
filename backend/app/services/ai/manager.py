import logging
from typing import Dict, Any, Optional, List
from app.services.ai.base import BaseAIProvider, ProviderHealth, LLMOutput
from app.services.ai.ollama_provider import OllamaProvider
from app.services.ai.lmstudio_provider import LMStudioProvider
from app.services.ai.huggingface_provider import HuggingFaceProvider
from app.services.ai.groq_provider import GroqProvider
from app.services.ai.fallback_provider import FallbackRuleProvider
from app.config import settings

logger = logging.getLogger(__name__)

# Priority order requested:
# 1. Ollama (Primary)
# 2. LM Studio (Secondary)
# 3. Hugging Face
# 4. Groq Free
# 5. Fallback Engine
PROVIDER_PRIORITY = ["ollama", "lmstudio", "huggingface", "groq", "fallback_engine"]

class AIProviderManager:
    def __init__(self):
        self.ollama = OllamaProvider(
            endpoint=settings.OLLAMA_BASE_URL,
            selected_model=settings.OLLAMA_MODEL
        )
        self.lmstudio = LMStudioProvider(
            endpoint=settings.LM_STUDIO_BASE_URL,
            selected_model=settings.LM_STUDIO_MODEL
        )
        self.huggingface = HuggingFaceProvider(
            api_key=settings.HUGGINGFACE_API_KEY,
            selected_model=settings.HUGGINGFACE_MODEL
        )
        self.groq = GroqProvider(
            api_key=settings.GROQ_API_KEY,
            selected_model=settings.GROQ_MODEL
        )
        self.fallback = FallbackRuleProvider()

        self._providers: Dict[str, BaseAIProvider] = {
            "ollama": self.ollama,
            "lmstudio": self.lmstudio,
            "huggingface": self.huggingface,
            "groq": self.groq,
            "fallback_engine": self.fallback
        }

    def get_provider(self, name: str) -> Optional[BaseAIProvider]:
        return self._providers.get(name)

    def check_all_health(self, user_override: Optional[Dict[str, Any]] = None) -> Dict[str, ProviderHealth]:
        """
        Actively probes each AI provider to verify live connectivity.
        Never reports connected without an active ping verification.
        """
        # Apply user overrides if any (e.g. user custom groq key or ollama endpoint)
        if user_override:
            if "ollama_endpoint" in user_override and user_override["ollama_endpoint"]:
                self.ollama.endpoint = user_override["ollama_endpoint"].rstrip("/")
            if "groq_api_key" in user_override and user_override["groq_api_key"]:
                self.groq.api_key = user_override["groq_api_key"]

        results = {}
        for name, provider in self._providers.items():
            results[name] = provider.check_health()
        return results

    def select_ollama_model(self, model_name: str) -> bool:
        """Allows switching Ollama active model."""
        available = self.ollama.list_available_models()
        if model_name in available:
            self.ollama.selected_model = model_name
            return True
        self.ollama.selected_model = model_name
        return False

    def generate_structured(
        self,
        prompt: str,
        system_prompt: str,
        schema_cls: Optional[Any] = None,
        preferred_provider: Optional[str] = None,
        preferred_model: Optional[str] = None,
        user_config: Optional[Dict[str, Any]] = None
    ) -> LLMOutput:
        """
        Executes structured generation using the preferred provider,
        or falls down the priority chain:
        Ollama -> LM Studio -> Hugging Face -> Groq -> Fallback Engine.
        """
        if user_config:
            if user_config.get("groq_api_key"):
                self.groq.api_key = user_config["groq_api_key"]
            if user_config.get("ollama_endpoint"):
                self.ollama.endpoint = user_config["ollama_endpoint"].rstrip("/")

        # Determine attempt sequence
        attempts = []
        if preferred_provider and preferred_provider in self._providers and preferred_provider != "smart_fallback":
            attempts.append(preferred_provider)

        # Append priority chain avoiding duplicates
        for p in PROVIDER_PRIORITY:
            if p not in attempts:
                attempts.append(p)

        last_error = None
        for prov_name in attempts:
            provider = self._providers[prov_name]
            
            # Skip if unconfigured cloud provider
            if prov_name == "groq" and not self.groq.api_key:
                continue
            if prov_name == "huggingface" and not self.huggingface.api_key:
                continue

            # Don't try offline providers if health check fails
            if prov_name in ["ollama", "lmstudio"]:
                health = provider.check_health()
                if health.status != "connected":
                    logger.info(f"Skipping {prov_name}: status is {health.status} ({health.message})")
                    last_error = f"{prov_name} is {health.status}"
                    continue

            logger.info(f"Attempting structured generation with provider: {prov_name}")
            output = provider.generate_structured(
                prompt=prompt,
                system_prompt=system_prompt,
                schema_cls=schema_cls,
                model=preferred_model if prov_name == preferred_provider else None
            )

            # If succeeded (or fallback provider provided structured data), return immediately
            if output.structured_data:
                if not output.is_fallback or prov_name == "fallback_engine":
                    return output

            last_error = output.error
            logger.warning(f"Provider {prov_name} generation failed: {output.error}. Attempting next in priority.")

        # If all failed, use Rule-Based Fallback Engine
        logger.info("All AI providers unavailable or failed. Generating via Fallback Rule Engine.")
        fallback_output = self.fallback.generate_structured(
            prompt=prompt,
            system_prompt=system_prompt,
            schema_cls=schema_cls
        )
        fallback_output.error = f"AI providers offline. {last_error or ''}".strip()
        return fallback_output

ai_manager = AIProviderManager()
