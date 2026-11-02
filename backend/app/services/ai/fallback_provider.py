import time
import json
import re
from typing import Dict, Any, Optional, List
from app.services.ai.base import BaseAIProvider, ProviderHealth, LLMOutput
from app.services.ai.schemas import (
    InterviewAnswerEvaluation,
    PracticeQuestionEvaluation,
    CareerRoadmapPlan,
    extract_and_validate_json
)

class FallbackRuleProvider(BaseAIProvider):
    def get_provider_name(self) -> str:
        return "fallback_engine"

    def list_available_models(self) -> List[str]:
        return ["rule-based-heuristics-v1"]

    def check_health(self) -> ProviderHealth:
        return ProviderHealth(
            provider_name="fallback_engine",
            status="connected",
            message="Deterministic Rule-Based & Heuristics Fallback Engine is active. Used automatically whenever AI providers are offline.",
            endpoint="local://in-memory",
            current_model="rule-based-heuristics-v1",
            available_models=["rule-based-heuristics-v1"],
            last_checked=time.strftime("%Y-%m-%d %H:%M:%S")
        )

    def generate_structured(
        self,
        prompt: str,
        system_prompt: str,
        schema_cls: Optional[Any] = None,
        model: Optional[str] = None,
        timeout_seconds: float = 15.0
    ) -> LLMOutput:
        start_time = time.time()
        prompt_lower = prompt.lower()

        # 1. Practice or Interview Answer Evaluation
        if "interview" in prompt_lower or "evaluate" in prompt_lower or schema_cls in [InterviewAnswerEvaluation, PracticeQuestionEvaluation]:
            # Rule-based evaluation based on candidate answer length, keywords, and technical structure
            words = re.findall(r'\b\w+\b', prompt_lower)
            word_count = len(words)
            
            # Simple keyword depth detection
            keywords_found = []
            test_keywords = ["fastapi", "react", "redis", "postgresql", "docker", "latency", "async", "cache", "scale", "component", "state", "star", "result", "action", "architecture"]
            for kw in test_keywords:
                if kw in prompt_lower:
                    keywords_found.append(kw)

            base_score = 65.0
            if len(keywords_found) >= 3:
                base_score += 15.0
            if word_count > 40:
                base_score += 10.0
            base_score = round(min(92.0, max(45.0, base_score)), 1)

            eval_dict = {
                "score": base_score,
                "technical_accuracy": round(base_score, 1),
                "completeness": round(max(40.0, base_score - 4.0), 1),
                "feedback": (
                    "[Generated via Rule-Based Evaluation Engine - AI Provider Offline] "
                    "Your answer demonstrates core technical awareness. To raise your score further, "
                    "incorporate concrete architectural trade-offs, quantifiable benchmarks, and failure mitigation patterns."
                ),
                "strengths": [
                    "Logical explanation and relevant technical terminology",
                    "Clear articulation of primary solution components"
                ],
                "missing_concepts": [
                    "Quantifiable scale metrics (e.g., throughput, latency, queries per second)",
                    "Edge case handling under cascading component failure"
                ],
                "model_answer": (
                    "A production-grade answer outlines the architectural trade-offs: component decoupling via message queues, "
                    "idempotent transaction handling, multi-level caching strategies, and end-to-end distributed tracing."
                )
            }

            elapsed_ms = int((time.time() - start_time) * 1000)
            return LLMOutput(
                raw_text=json.dumps(eval_dict),
                structured_data=eval_dict,
                is_fallback=True, # Explicitly labeled as fallback
                provider_used="fallback_engine",
                model_used="rule-based-heuristics-v1",
                latency_ms=elapsed_ms
            )

        # 2. Career Roadmap Generation
        elif "roadmap" in prompt_lower or schema_cls == CareerRoadmapPlan:
            roadmap_dict = {
                "overview": (
                    "[Generated via Standard Curriculum Template - AI Provider Offline] "
                    "A phased 4-stage engineering roadmap designed to build mastery in full-stack architecture, "
                    "scalable distributed storage, and high-stakes technical interview execution."
                ),
                "key_focus_areas": [
                    "Modern Reactive UI & TypeScript",
                    "High-Throughput Backend & Relational Optimization",
                    "Distributed System Design & Caching",
                    "Production Telemetry, CI/CD & Behavioral Interview Prep"
                ],
                "milestones": [
                    {
                        "phase_number": 1,
                        "title": "Phase 1: Advanced Core Competencies & Foundations",
                        "duration": "Weeks 1-4",
                        "objectives": [
                            "Master asynchronous concurrency, event loop mechanics, and memory lifecycle.",
                            "Deep-dive into REST, GraphQL API design, caching layers, and database normalization.",
                            "Implement foundational data structures and standard algorithm patterns (Two Pointers, Sliding Window, DFS/BFS)."
                        ],
                        "recommended_projects": [
                            {
                                "name": "High-Throughput Rate Limiter",
                                "description": "Build a token-bucket rate limiter middleware using Redis and FastAPI.",
                                "tech_stack": ["FastAPI", "Redis", "Docker"]
                            }
                        ],
                        "learning_resources": [
                            {"title": "System Design Primer", "type": "Interactive Guide", "link": "https://github.com/donnemartin/system-design-primer"},
                            {"title": "Designing Data-Intensive Applications", "type": "Book", "link": "O'Reilly Media"}
                        ]
                    },
                    {
                        "phase_number": 2,
                        "title": "Phase 2: Full-Stack Integration & Scalable Storage",
                        "duration": "Weeks 5-8",
                        "objectives": [
                            "Build resilient microservices with event queues (Kafka or RabbitMQ).",
                            "Implement distributed session authentication, RBAC, and token refresh mechanisms.",
                            "Configure PostgreSQL indexing, query plan analysis (EXPLAIN ANALYZE), and read replicas."
                        ],
                        "recommended_projects": [
                            {
                                "name": "Distributed Real-Time Collaboration Canvas",
                                "description": "Full-stack whiteboard with WebSockets, optimistic UI updates, and conflict resolution.",
                                "tech_stack": ["React", "TypeScript", "WebSockets", "Node/Python"]
                            }
                        ],
                        "learning_resources": [
                            {"title": "PostgreSQL High Performance", "type": "Documentation", "link": "https://www.postgresql.org/docs/"}
                        ]
                    },
                    {
                        "phase_number": 3,
                        "title": "Phase 3: Production Engineering, Cloud & System Design",
                        "duration": "Weeks 9-16",
                        "objectives": [
                            "Master horizontal scaling, load balancers, CDN caching, and database sharding.",
                            "Containerize services with Docker multi-stage builds and Kubernetes deployments.",
                            "Implement end-to-end telemetry (Prometheus, Grafana, OpenTelemetry)."
                        ],
                        "recommended_projects": [
                            {
                                "name": "Cloud-Native Observability Dashboard",
                                "description": "Metrics aggregator with alert thresholds and live log streaming.",
                                "tech_stack": ["Python/Go", "Docker", "Prometheus", "React"]
                            }
                        ],
                        "learning_resources": [
                            {"title": "Kubernetes the Hard Way", "type": "Hands-on Lab", "link": "https://github.com/kelseyhightower/kubernetes-the-hard-way"}
                        ]
                    },
                    {
                        "phase_number": 4,
                        "title": "Phase 4: High-Stakes Mock Interviews & Behavioral Mastery",
                        "duration": "Weeks 17-24",
                        "objectives": [
                            "Execute 20+ full-length technical and architectural mock interviews.",
                            "Structure behavioral responses using the STAR method with quantifiable impact.",
                            "Refine resume bullet points with high-impact metrics (latency reduction, cost savings, scale)."
                        ],
                        "recommended_projects": [
                            {
                                "name": "Capstone Production Portfolio Deployment",
                                "description": "Deploy capstone projects with automated CI/CD pipeline and monitoring.",
                                "tech_stack": ["Terraform", "GitHub Actions", "Cloud Hosting"]
                            }
                        ],
                        "learning_resources": [
                            {"title": "Grokking the System Design Interview", "type": "Course", "link": "Educative"}
                        ]
                    }
                ]
            }

            elapsed_ms = int((time.time() - start_time) * 1000)
            return LLMOutput(
                raw_text=json.dumps(roadmap_dict),
                structured_data=roadmap_dict,
                is_fallback=True,
                provider_used="fallback_engine",
                model_used="rule-based-heuristics-v1",
                latency_ms=elapsed_ms
            )

        # Default Generic Fallback
        default_dict = {
            "status": "template_fallback",
            "message": "Template-generated response. Connect Ollama or local LLM in settings for dynamic AI generation."
        }
        elapsed_ms = int((time.time() - start_time) * 1000)
        return LLMOutput(
            raw_text=json.dumps(default_dict),
            structured_data=default_dict,
            is_fallback=True,
            provider_used="fallback_engine",
            model_used="rule-based-heuristics-v1",
            latency_ms=elapsed_ms
        )
