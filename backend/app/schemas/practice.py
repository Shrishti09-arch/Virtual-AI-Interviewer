from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class QuestionBankItem(BaseModel):
    id: int
    category: str
    subject: Optional[str] = "Computer Science Fundamentals"
    difficulty: str
    role_track: str
    programming_language: Optional[str] = "Python"
    question_type: Optional[str] = "Theory"
    title: str
    question_text: str
    expected_keywords: List[str] = []
    sample_answer: Optional[str] = ""
    hints: List[str] = []
    options: List[str] = []
    correct_option_index: Optional[int] = None
    explanation: Optional[str] = ""
    code_template: Optional[str] = ""
    test_cases: List[Dict[str, Any]] = []
    source_type: Optional[str] = "curated_educational"
    source_name: Optional[str] = "Official Educational Standard"
    source_url: Optional[str] = None

    class Config:
        from_attributes = True

class PracticeSubmitRequest(BaseModel):
    question_id: int
    user_answer: str

class PracticeEvaluationResponse(BaseModel):
    id: int
    question_id: int
    score: float # 0 - 100
    feedback: str
    strengths: List[str] = []
    missing_concepts: List[str] = []
    is_fallback: bool = False
    provider_used: Optional[str] = "fallback_engine"
    model_used: Optional[str] = "rule-based-heuristics-v1"
    created_at: datetime

    class Config:
        from_attributes = True

# --- Module 4 Interactive Practice Session Schemas ---

class StartPracticeSessionRequest(BaseModel):
    job_role: str = "Software Development Engineer"
    subject: str = "Data Structures and Algorithms"
    programming_language: str = "Python"
    difficulty: str = "Intermediate"
    total_questions: int = 5
    interview_type: str = "Comprehensive Mixed"

class PracticeAnswerSubmitRequest(BaseModel):
    question_id: int
    answer_type: Optional[str] = "theory" # mcq, coding, theory
    selected_option_index: Optional[int] = None
    user_answer: Optional[str] = None
    code: Optional[str] = None
    language: Optional[str] = None

class ExecuteCodeRequest(BaseModel):
    code: str
    language: str = "python"
    test_cases: List[Dict[str, Any]] = []

class PracticeSessionStateResponse(BaseModel):
    session_id: int
    job_role: str
    subject: str
    programming_language: str
    difficulty: str
    interview_type: str
    total_questions: int
    current_index: int
    is_completed: bool
    active_question: Optional[Dict[str, Any]] = None

class PracticeSessionAnswerResponse(BaseModel):
    evaluation: Dict[str, Any]
    current_index: int
    total_questions: int
    is_completed: bool
    next_question: Optional[Dict[str, Any]] = None
    final_report: Optional[Dict[str, Any]] = None

class PracticeMetadataResponse(BaseModel):
    subjects: List[str]
    difficulties: List[str]
    interview_types: List[str]
    languages: List[str]
