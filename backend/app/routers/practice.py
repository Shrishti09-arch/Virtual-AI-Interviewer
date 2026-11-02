from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.practice import QuestionBank, PracticeSubmission, PracticeSession
from app.schemas.practice import (
    QuestionBankItem,
    PracticeSubmitRequest,
    PracticeEvaluationResponse,
    StartPracticeSessionRequest,
    PracticeSessionStateResponse,
    PracticeAnswerSubmitRequest,
    PracticeSessionAnswerResponse,
    ExecuteCodeRequest,
    PracticeMetadataResponse
)
from app.services.auth_service import get_current_user
from app.services.interview_service import interview_service
from app.services.practice_service import practice_service
from app.services.sandbox_executor import sandbox_executor

router = APIRouter(prefix="/practice", tags=["Question Bank & Interactive Practice"])

@router.get("/metadata", response_model=PracticeMetadataResponse)
def get_practice_metadata():
    """Returns available subjects (14 subjects), difficulties, types, and languages."""
    return practice_service.get_supported_metadata()

@router.get("/questions", response_model=List[QuestionBankItem])
def get_questions(
    category: Optional[str] = None,
    subject: Optional[str] = None,
    difficulty: Optional[str] = None,
    question_type: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Fetches questions from question bank with extensive multi-dimensional filtering."""
    query = db.query(QuestionBank)
    if category and isinstance(category, str) and category != "All":
        query = query.filter(QuestionBank.category == category)
    if subject and isinstance(subject, str) and subject != "All":
        query = query.filter(QuestionBank.subject == subject)
    if difficulty and isinstance(difficulty, str) and difficulty != "All":
        query = query.filter(QuestionBank.difficulty == difficulty)
    if question_type and isinstance(question_type, str) and question_type != "All":
        query = query.filter(QuestionBank.question_type == question_type)
    if search and isinstance(search, str):
        query = query.filter(
            (QuestionBank.title.ilike(f"%{search}%")) |
            (QuestionBank.question_text.ilike(f"%{search}%"))
        )
    return query.order_by(QuestionBank.id.asc()).all()

@router.get("/questions/{question_id}", response_model=QuestionBankItem)
def get_single_question(question_id: int, db: Session = Depends(get_db)):
    """Fetches a single question by ID."""
    q = db.query(QuestionBank).filter(QuestionBank.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    return q

@router.post("/execute-code")
def run_code_in_sandbox(
    payload: ExecuteCodeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Safely executes candidate code in an isolated subprocess sandbox.
    Never executes untrusted code in the main application process.
    """
    result = sandbox_executor.execute(
        language=payload.language,
        code=payload.code,
        test_cases=payload.test_cases
    )
    return result

@router.post("/session/start", response_model=PracticeSessionStateResponse)
def start_practice_session(
    payload: StartPracticeSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initializes an intelligent interactive practice session with unique,
    non-repeating questions, AST-safe sandboxing, and progress tracking.
    """
    session_data = practice_service.start_session(
        db=db,
        user_id=current_user.id,
        job_role=payload.job_role,
        subject=payload.subject,
        programming_language=payload.programming_language,
        difficulty=payload.difficulty,
        total_questions=payload.total_questions,
        interview_type=payload.interview_type,
        user_llm_provider=current_user.llm_preference,
        api_key=current_user.groq_api_key,
        ollama_endpoint=current_user.ollama_endpoint
    )
    return session_data

@router.get("/session/{session_id}", response_model=PracticeSessionStateResponse)
def get_practice_session_state(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetches current state of an ongoing or completed practice session."""
    session = db.query(PracticeSession).filter(
        PracticeSession.id == session_id,
        PracticeSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Practice session not found.")

    active_q = None
    if not session.is_completed and session.current_index < session.total_questions:
        qid = session.question_ids[session.current_index]
        q_obj = db.query(QuestionBank).filter(QuestionBank.id == qid).first()
        if q_obj:
            active_q = practice_service.format_active_question(q_obj, session.current_index, session.total_questions)

    return {
        "session_id": session.id,
        "job_role": session.job_role,
        "subject": session.subject,
        "programming_language": session.programming_language,
        "difficulty": session.difficulty,
        "interview_type": session.interview_type,
        "total_questions": session.total_questions,
        "current_index": session.current_index,
        "is_completed": session.is_completed,
        "active_question": active_q
    }

@router.post("/session/{session_id}/answer", response_model=PracticeSessionAnswerResponse)
def submit_session_answer(
    session_id: int,
    payload: PracticeAnswerSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submits answer for active question (MCQ, Theory, or Coding),
    evaluates using AI/Sandbox, and advances session.
    """
    try:
        result = practice_service.submit_answer(
            db=db,
            session_id=session_id,
            user_id=current_user.id,
            question_id=payload.question_id,
            answer_payload=payload.dict(),
            user_llm_provider=current_user.llm_preference,
            api_key=current_user.groq_api_key,
            ollama_endpoint=current_user.ollama_endpoint
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Answer submission failed: {str(e)}")

@router.get("/session/{session_id}/report")
def get_session_final_report(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetches final performance breakdown, weak areas, and recommendations for a completed session."""
    try:
        report = practice_service.get_session_report(db, session_id, current_user.id)
        return report
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))

@router.get("/sessions")
def list_user_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists history of practice sessions for current user."""
    sessions = db.query(PracticeSession).filter(
        PracticeSession.user_id == current_user.id
    ).order_by(PracticeSession.created_at.desc()).all()

    return [
        {
            "id": s.id,
            "job_role": s.job_role,
            "subject": s.subject,
            "difficulty": s.difficulty,
            "total_questions": s.total_questions,
            "is_completed": s.is_completed,
            "accuracy": s.accuracy,
            "created_at": s.created_at
        }
        for s in sessions
    ]

# Backward compatible single question submission
@router.post("/questions/{question_id}/submit", response_model=PracticeEvaluationResponse)
def submit_practice_answer(
    question_id: int,
    submission_in: PracticeSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    question = db.query(QuestionBank).filter(QuestionBank.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    eval_result = interview_service.evaluate_answer(
        question_text=question.question_text,
        category=question.category,
        candidate_answer=submission_in.user_answer,
        time_spent_seconds=90,
        user_llm_provider=current_user.llm_preference,
        api_key=current_user.groq_api_key,
        ollama_endpoint=current_user.ollama_endpoint
    )

    practice_record = PracticeSubmission(
        user_id=current_user.id,
        question_id=question.id,
        user_answer=submission_in.user_answer,
        score=eval_result["score"],
        feedback=eval_result["feedback"],
        strengths=eval_result.get("strengths", []),
        missing_concepts=eval_result.get("missing_concepts", []),
        is_fallback=eval_result.get("is_fallback", False),
        provider_used=eval_result.get("provider_used", "fallback_engine"),
        model_used=eval_result.get("model_used", "rule-based-heuristics-v1")
    )
    db.add(practice_record)
    db.commit()
    db.refresh(practice_record)

    return practice_record

@router.get("/submissions", response_model=List[PracticeEvaluationResponse])
def get_user_submissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(PracticeSubmission).filter(
        PracticeSubmission.user_id == current_user.id
    ).order_by(PracticeSubmission.created_at.desc()).all()
