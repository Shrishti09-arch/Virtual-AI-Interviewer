"""
LM Studio Local AI Provider Service
Handles OpenAI-compatible local endpoints running on localhost:1234
"""
from app.services.ai.lmstudio_provider import LMStudioProvider

lmstudio_service = LMStudioProvider()

__all__ = ["LMStudioProvider", "lmstudio_service"]
