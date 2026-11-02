"""
Interview Answer Evaluation & Assessment Engine
Evaluates interview answers across technical correctness, conceptual depth, relevance,
explanation quality, and problem-solving with transparent scoring and actionable feedback.
"""
from typing import Dict, Any, List, Optional
from app.services.interview_service import InterviewService


class EvaluationService:
    """
    Multi-dimensional AI assessment engine for interview responses.
    Evaluates responses against ground-truth rubrics while honoring diverse valid explanations.
    """

    @classmethod
    def evaluate_answer(
        cls,
        question: Optional[str] = None,
        answer: Optional[str] = None,
        question_text: Optional[str] = None,
        candidate_answer: Optional[str] = None,
        role: str = "Software Engineer",
        category: str = "Technical",
        time_spent_seconds: int = 60,
        pauses_count: int = 0,
        user_llm_provider: Optional[str] = None,
        api_key: Optional[str] = None,
        ollama_endpoint: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Evaluate candidate response on a multi-dimensional scale (0-100).
        """
        q_text = question_text or question or ""
        ans_text = candidate_answer or answer or ""
        cat = category or role
        return InterviewService.evaluate_answer(
            question_text=q_text,
            category=cat,
            candidate_answer=ans_text,
            time_spent_seconds=time_spent_seconds,
            pauses_count=pauses_count,
            user_llm_provider=user_llm_provider,
            api_key=api_key,
            ollama_endpoint=ollama_endpoint
        )

    @classmethod
    def generate_final_summary(
        cls,
        evaluations: List[Dict[str, Any]],
        communication_scores: Optional[List[Dict[str, Any]]] = None,
        role: str = "Software Engineer",
        interview_type: str = "Technical"
    ) -> Dict[str, Any]:
        """
        Aggregate individual question evaluations and communication metrics
        into a finalized executive performance report with composite scores and improvement plan.
        """
        return InterviewService.generate_interview_summary(
            evaluations=evaluations,
            communication_scores=communication_scores or [],
            role=role,
            interview_type=interview_type
        )

    @classmethod
    def generate_pdf_report(cls, session_data: Any) -> bytes:
        """
        Produce a high-resolution, branded PDF interview report for candidate download.
        """
        return InterviewService.generate_pdf_report(session_data)


evaluation_service = EvaluationService()

__all__ = ["EvaluationService", "evaluation_service"]
