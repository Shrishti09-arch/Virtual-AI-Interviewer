"""
Unified Modular AI Service Orchestrator
Strictly Open-Source & Local AI Hierarchy: Ollama -> LM Studio -> Hugging Face -> Groq -> Fallback
"""
from app.services.ai.manager import ai_manager, PROVIDER_PRIORITY
from app.services.ai.schemas import (
    InterviewAnswerEvaluation,
    PracticeQuestionEvaluation,
    CareerRoadmapPlan,
    MilestoneSpec,
    extract_and_validate_json
)

__all__ = [
    "ai_manager",
    "PROVIDER_PRIORITY",
    "InterviewAnswerEvaluation",
    "PracticeQuestionEvaluation",
    "CareerRoadmapPlan",
    "MilestoneSpec",
    "extract_and_validate_json"
]
