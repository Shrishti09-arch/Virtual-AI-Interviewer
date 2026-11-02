"""
Ollama Local AI Provider Service
Handles local llama3, mistral, qwen model execution via REST API
"""
from app.services.ai.ollama_provider import OllamaProvider

ollama_service = OllamaProvider()

__all__ = ["OllamaProvider", "ollama_service"]
