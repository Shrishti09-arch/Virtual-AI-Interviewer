"""
Groq Ultra-Fast LPU Inference Provider Service
High-speed fallback provider for Llama-3-70B/8B and Mixtral-8x7B open models
"""
from app.services.ai.groq_provider import GroqProvider

groq_service = GroqProvider()

__all__ = ["GroqProvider", "groq_service"]
