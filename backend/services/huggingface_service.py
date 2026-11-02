"""
Hugging Face Inference API Provider Service
Fall-through remote open-source provider (Qwen/Mistral/Llama/DeepSeek via HF Router)
"""
from app.services.ai.huggingface_provider import HuggingFaceProvider

huggingface_service = HuggingFaceProvider()

__all__ = ["HuggingFaceProvider", "huggingface_service"]
