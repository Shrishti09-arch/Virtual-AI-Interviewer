from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

class ProviderHealth(BaseModel):
    provider_name: str
    status: str # "connected", "offline", "unconfigured", "no_models"
    message: str
    endpoint: str
    current_model: Optional[str] = None
    available_models: List[str] = []
    last_checked: Optional[str] = None
    install_instructions: Optional[str] = None

class LLMOutput(BaseModel):
    raw_text: str
    structured_data: Optional[Dict[str, Any]] = None
    is_fallback: bool = False
    provider_used: str
    model_used: str
    latency_ms: int = 0
    error: Optional[str] = None

class BaseAIProvider(ABC):
    @abstractmethod
    def get_provider_name(self) -> str:
        pass

    @abstractmethod
    def check_health(self) -> ProviderHealth:
        pass

    @abstractmethod
    def list_available_models(self) -> List[str]:
        pass

    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        system_prompt: str,
        schema_cls: Optional[Any] = None,
        model: Optional[str] = None,
        timeout_seconds: float = 15.0
    ) -> LLMOutput:
        pass
