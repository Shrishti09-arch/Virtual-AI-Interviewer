"""
Question Bank, Technical Practice & Safe Code Execution Service
Manages question generation, retrieval, duplicate detection, history tracking,
MCQ / Theory evaluation, and sandboxed code execution across 14 CS/Software subjects.
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.services.practice_service import PracticeService, practice_service
from app.services.sandbox_executor import SandboxExecutor, SecurityViolationError


class QuestionService:
    """
    Unified Question Service providing technical question generation,
    question bank queries, duplicate detection, and sandboxed code verification.
    """

    @classmethod
    def get_supported_metadata(cls) -> Dict[str, Any]:
        """Returns supported roles, subjects, question types, and difficulties."""
        return practice_service.get_supported_metadata()

    @classmethod
    def start_practice_session(
        cls,
        db: Session,
        user_id: int,
        role: str,
        subject: str,
        difficulty: str,
        interview_type: str = "Technical",
        programming_language: Optional[str] = None,
        total_questions: int = 5
    ) -> Dict[str, Any]:
        """Initializes a new interactive technical practice session with unique questions."""
        return practice_service.start_session(
            db=db,
            user_id=user_id,
            role=role,
            subject=subject,
            difficulty=difficulty,
            interview_type=interview_type,
            programming_language=programming_language,
            total_questions=total_questions
        )

    @classmethod
    def submit_answer(
        cls,
        db: Session,
        session_id: int,
        user_id: int,
        question_id: int,
        user_answer: str,
        code_solution: Optional[str] = None,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """Submits an answer (MCQ option, theory text, or code solution) and returns evaluation."""
        return practice_service.submit_answer(
            db=db,
            session_id=session_id,
            user_id=user_id,
            question_id=question_id,
            user_answer=user_answer,
            code_solution=code_solution,
            language=language
        )

    @classmethod
    def get_session_report(cls, db: Session, session_id: int, user_id: int) -> Dict[str, Any]:
        """Computes comprehensive final report with accuracy, topic breakdown, and recommendations."""
        return practice_service.get_session_report(db=db, session_id=session_id, user_id=user_id)

    @classmethod
    def execute_code(
        cls,
        code: str,
        language: str,
        test_cases: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Executes candidate code inside the restricted subprocess sandbox."""
        return SandboxExecutor.execute(
            language=language,
            code=code,
            test_cases=test_cases or []
        )


question_service = QuestionService()

__all__ = ["QuestionService", "question_service", "SandboxExecutor", "SecurityViolationError"]
