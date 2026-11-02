"""
Unit and Integration Tests for Strictly Non-OpenAI AI Architecture
Verifies provider priority, JSON structure validation, Ollama detection, and Fallback engine.
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.ai.manager import ai_manager, PROVIDER_PRIORITY
from app.services.ai.ollama_provider import OllamaProvider
from app.services.ai.schemas import InterviewAnswerEvaluation, CareerRoadmapPlan
from app.services.ai.fallback_provider import FallbackRuleProvider


class TestAIHierarchy(unittest.TestCase):
    def test_ai_provider_priority(self):
        expected_priority = ["ollama", "lmstudio", "huggingface", "groq", "fallback_engine"]
        self.assertEqual(PROVIDER_PRIORITY, expected_priority)

    def test_ollama_model_selection(self):
        ollama = OllamaProvider(endpoint="http://localhost:11434")
        mock_models = ["mistral:latest", "llama3.1:8b", "phi3:mini"]
        best = ollama.select_best_model(mock_models)
        self.assertEqual(best, "llama3.1:8b")

    def test_fallback_engine_structured_evaluation(self):
        fallback = FallbackRuleProvider()
        out = fallback.generate_structured(
            prompt="Question: Explain ACID. Answer: Atomicity, Consistency, Isolation, Durability.",
            system_prompt="Evaluate answer.",
            schema_cls=InterviewAnswerEvaluation
        )
        self.assertTrue(out.is_fallback)
        self.assertEqual(out.provider_used, "fallback_engine")
        self.assertIn("score", out.structured_data)
        validated = InterviewAnswerEvaluation.model_validate(out.structured_data)
        self.assertGreater(validated.score, 0)
        self.assertGreater(len(validated.strengths), 0)


if __name__ == "__main__":
    unittest.main()
