from app.services.ai.manager import ai_manager, PROVIDER_PRIORITY
from app.services.ai.ollama_provider import OllamaProvider
from app.services.ai.schemas import InterviewAnswerEvaluation, CareerRoadmapPlan, extract_and_validate_json
from app.services.ai.fallback_provider import FallbackRuleProvider

def test_ai_modular_system():
    print("=== Testing Strictly Non-OpenAI AI Modular Architecture ===", flush=True)

    # 1. Verify Provider Priority Hierarchy
    expected_priority = ["ollama", "lmstudio", "huggingface", "groq", "fallback_engine"]
    assert PROVIDER_PRIORITY == expected_priority, f"Unexpected priority: {PROVIDER_PRIORITY}"
    print("[PASS] Provider priority confirmed: Ollama (Primary) -> LM Studio -> Hugging Face -> Groq -> Fallback", flush=True)

    # 2. Test Ollama Health & Offline Safety
    ollama = OllamaProvider(endpoint="http://localhost:11434")
    health = ollama.check_health()
    assert health.provider_name == "ollama"
    assert health.status in ["connected", "offline", "no_models"]
    print(f"[PASS] Ollama Health Checked (Live verification): Status = '{health.status}'", flush=True)
    if health.status == "offline":
        assert "winget install Ollama.Ollama" in health.install_instructions
        print("[PASS] Verified Windows installation instructions are generated when Ollama is offline.", flush=True)

    # 3. Test Ollama Preferred Model Auto-Selection Logic
    mock_models = ["mistral:latest", "llama3.1:8b", "phi3:mini"]
    best = ollama.select_best_model(mock_models)
    assert best == "llama3.1:8b", f"Expected llama3.1:8b to be prioritized, got {best}"
    print(f"[PASS] Ollama auto-selected preferred model correctly: {best}", flush=True)

    mock_qwen = ["random-model", "qwen3:8b", "llama3.1:8b"]
    best_qwen = ollama.select_best_model(mock_qwen)
    assert best_qwen == "qwen3:8b", f"Expected qwen3:8b, got {best_qwen}"
    print(f"[PASS] Ollama auto-selected highest priority qwen3:8b correctly: {best_qwen}", flush=True)

    # 4. Test Fallback Rule Engine Structured Generation
    fallback = FallbackRuleProvider()
    out = fallback.generate_structured(
        prompt="Question: Explain ACID. Answer: Atomicity, Consistency, Isolation, Durability.",
        system_prompt="Evaluate answer.",
        schema_cls=InterviewAnswerEvaluation
    )
    assert out.is_fallback is True, "Fallback engine must explicitly mark is_fallback=True"
    assert out.provider_used == "fallback_engine"
    assert "score" in out.structured_data
    assert "technical_accuracy" in out.structured_data
    # Validate with Pydantic
    validated = InterviewAnswerEvaluation.model_validate(out.structured_data)
    assert validated.score > 0
    print(f"[PASS] Fallback Engine generated validated Pydantic InterviewAnswerEvaluation: Score {validated.score}%", flush=True)

    # 5. Test AI Manager End-to-End Structured Generation
    manager_out = ai_manager.generate_structured(
        prompt="Create roadmap for Full Stack Engineer",
        system_prompt="Create roadmap",
        schema_cls=CareerRoadmapPlan
    )
    assert manager_out.structured_data is not None
    assert "milestones" in manager_out.structured_data
    assert len(manager_out.structured_data["milestones"]) == 4
    print(f"[PASS] AI Manager coordinated structured roadmap generation: Provider '{manager_out.provider_used}', is_fallback={manager_out.is_fallback}", flush=True)

    # 6. Test JSON Extraction & Repair
    raw_markdown = """Here is the result:
```json
{
  "score": 88.5,
  "technical_accuracy": 90.0,
  "completeness": 85.0,
  "feedback": "Great response.",
  "strengths": ["Clear thinking"],
  "missing_concepts": ["Monitoring"],
  "model_answer": "Use circuit breakers."
}
```
Hope this helps!"""
    parsed = extract_and_validate_json(raw_markdown, InterviewAnswerEvaluation)
    assert parsed.score == 88.5
    print("[PASS] Robust JSON extraction from LLM markdown completed successfully.", flush=True)

    print("\n=======================================================")
    print("ALL AI MODULAR PROVIDER & FALLBACK TESTS PASSED 100%!")
    print("=======================================================", flush=True)

if __name__ == "__main__":
    test_ai_modular_system()
