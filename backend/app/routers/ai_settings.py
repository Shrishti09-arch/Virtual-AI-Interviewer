from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.ai.manager import ai_manager, PROVIDER_PRIORITY
from app.services.ai.schemas import InterviewAnswerEvaluation
from app.core.security import mask_api_key

router = APIRouter(prefix="/ai-settings", tags=["Modular AI Providers"])

class ProviderModelSelectRequest(BaseModel):
    provider: str
    model_name: str

class ProviderTestRequest(BaseModel):
    provider: str
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    model_name: Optional[str] = None

@router.get("/status")
def get_all_provider_statuses(current_user: User = Depends(get_current_user)):
    user_override = {
        "ollama_endpoint": current_user.ollama_endpoint,
        "groq_api_key": current_user.groq_api_key
    }
    health_results = ai_manager.check_all_health(user_override=user_override)
    
    # Format response with provider health
    providers_data = {}
    for name, health in health_results.items():
        providers_data[name] = health.model_dump()

    # Determine currently effective provider according to user setting or priority
    effective_provider = current_user.llm_preference or "ollama"
    # If user selected an offline provider, determine auto-fallback in priority order
    auto_active = effective_provider
    if effective_provider != "fallback_engine":
        current_health = health_results.get(effective_provider)
        if not current_health or current_health.status != "connected":
            # Walk priority chain
            for p in PROVIDER_PRIORITY:
                h = health_results.get(p)
                if h and h.status == "connected":
                    auto_active = p
                    break

    return {
        "active_provider": auto_active,
        "configured_preference": current_user.llm_preference or "ollama",
        "active_effective_provider": auto_active,
        "provider_priority": PROVIDER_PRIORITY,
        "providers": providers_data,
        "masked_groq_key": mask_api_key(current_user.groq_api_key) if current_user.groq_api_key else None,
        "no_openai_guarantee": True,
        "ollama_primary": True
    }

@router.post("/select-model")
def select_provider_model(
    req: ProviderModelSelectRequest,
    current_user: User = Depends(get_current_user)
):
    provider = ai_manager.get_provider(req.provider)
    if not provider:
        raise HTTPException(status_code=404, detail=f"Provider '{req.provider}' not recognized")

    if req.provider == "ollama":
        ai_manager.select_ollama_model(req.model_name)
    else:
        provider.selected_model = req.model_name

    return {
        "status": "success",
        "provider": req.provider,
        "selected_model": req.model_name
    }

@router.post("/test")
def test_provider_connection(
    req: ProviderTestRequest,
    current_user: User = Depends(get_current_user)
):
    provider = ai_manager.get_provider(req.provider)
    if not provider:
        raise HTTPException(status_code=404, detail="Unknown provider")

    # Override endpoint/key if tested from UI
    if req.provider == "ollama" and req.endpoint:
        provider.endpoint = req.endpoint.rstrip("/")
    if req.provider == "groq" and req.api_key:
        provider.api_key = req.api_key

    # Check live health
    health = provider.check_health()
    if health.status != "connected" and req.provider != "fallback_engine":
        return {
            "success": False,
            "status": health.status,
            "message": health.message,
            "install_instructions": health.install_instructions,
            "latency_ms": 0
        }

    # Test structured generation
    test_prompt = "Question: Explain React reconciliation. Answer: React compares Virtual DOM trees in O(n) using keys."
    output = provider.generate_structured(
        prompt=test_prompt,
        system_prompt="You are an expert technical interviewer evaluating an answer.",
        schema_cls=InterviewAnswerEvaluation,
        model=req.model_name
    )

    return {
        "success": not output.is_fallback,
        "status": "connected" if not output.is_fallback else "failed",
        "message": f"Successfully verified structured JSON response from {req.provider} ({output.model_used}) in {output.latency_ms}ms" if not output.is_fallback else output.error,
        "provider_used": output.provider_used,
        "model_used": output.model_used,
        "latency_ms": output.latency_ms,
        "is_fallback": output.is_fallback,
        "sample_output": output.structured_data
    }

@router.get("/ollama-help")
def get_ollama_installation_guide():
    return {
        "title": "Ollama Windows Setup & Recommended Models Guide",
        "quick_install": "winget install Ollama.Ollama",
        "download_url": "https://ollama.com/download/windows",
        "recommended_models": [
            {
                "name": "llama3.1:8b",
                "command": "ollama run llama3.1:8b",
                "size": "4.7 GB",
                "description": "Meta Llama 3.1 8B - Outstanding reasoning for interview coaching and system design."
            },
            {
                "name": "qwen3:8b (or qwen2.5:8b)",
                "command": "ollama run qwen2.5:8b",
                "size": "4.7 GB",
                "description": "Alibaba Qwen 2.5 8B - Top-tier coding and algorithmic answer analysis."
            },
            {
                "name": "mistral:7b",
                "command": "ollama run mistral:7b",
                "size": "4.1 GB",
                "description": "Mistral 7B Instruct - High precision and fast local inference speed."
            }
        ],
        "verification": "Run 'curl http://localhost:11434/api/tags' to verify running instance."
    }
