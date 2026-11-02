from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class InterviewStartRequest(BaseModel):
    role_title: str = "Software Development Engineer"
    experience_level: str = "1-3 years" # Student/Fresher, 1-3 years, 4-7 years, 8+ years
    interview_type: str = "Technical" # Technical, HR, Behavioral, Managerial, AI/ML, Coding, Company-specific
    difficulty: str = "Intermediate" # Beginner, Intermediate, Advanced, Expert
    technical_subjects: List[str] = ["Data Structures and Algorithms", "System Design"]
    interview_duration_mins: int = 15
    target_company: Optional[str] = None # e.g. Google, Amazon, Meta, Microsoft
    total_questions: int = Field(5, ge=2, le=10)
    recording_consent: bool = Field(True, description="Candidate explicit consent to record audio/video for coaching evaluation")

class InterviewAnswerRequest(BaseModel):
    question_id: int
    candidate_answer: str
    time_spent_seconds: int = 60
    pauses_count: int = 0
    has_local_recording: bool = False
    recording_storage_key: Optional[str] = None

class InterviewQuestionResponse(BaseModel):
    id: int
    session_id: int
    question_order: int
    category: str
    question_text: str
    is_follow_up: bool = False
    difficulty_level: str = "Intermediate"
    candidate_answer: Optional[str] = None
    time_spent_seconds: int = 0
    has_local_recording: bool = False
    recording_storage_key: Optional[str] = None
    score: float = 0.0
    score_out_of_10: float = 0.0
    technical_accuracy: float = 0.0
    completeness: float = 0.0
    problem_solving_rating: float = 0.0
    feedback: Optional[str] = None
    correct_points: List[str] = []
    incorrect_points: List[str] = []
    missing_concepts: List[str] = []
    model_answer: Optional[str] = None
    ideal_answer: Optional[str] = None
    improvement_suggestions: Optional[str] = None
    filler_words: Dict[str, int] = {}
    repeated_words: List[str] = []
    pauses_count: int = 0
    wpm: float = 0.0
    vocabulary_score: float = 0.0
    star_analysis: Dict[str, Any] = {}
    is_fallback: bool = False
    provider_used: Optional[str] = "fallback_engine"
    model_used: Optional[str] = "rule-based-heuristics-v1"

    class Config:
        from_attributes = True

class InterviewSessionResponse(BaseModel):
    id: int
    role_title: str
    experience_level: str
    interview_type: str
    difficulty: str = "Intermediate"
    technical_subjects: List[str] = []
    interview_duration_mins: int = 15
    target_company: Optional[str] = None
    status: str
    total_questions: int
    current_question_index: int = 0
    duration_seconds: int
    overall_score: float
    technical_score: float
    communication_score: float
    behavioral_score: float
    answer_quality_score: float = 0.0
    problem_solving_score: float = 0.0
    verdict: str
    overall_summary: Optional[str] = None
    key_strengths: List[str] = []
    areas_to_improve: List[str] = []
    recommended_topics: List[str] = []
    improvement_plan: List[str] = []
    full_transcript: Optional[str] = None
    assessment_disclaimer: Optional[str] = None
    total_filler_words: int = 0
    average_wpm: float = 0.0
    clarity_rating: str = "Good"
    recording_consent: bool = True
    recording_path: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    questions: List[InterviewQuestionResponse] = []

    class Config:
        from_attributes = True

class AudioTranscribeResponse(BaseModel):
    transcript: str
    duration_seconds: float = 0.0
    wpm: float = 0.0
    filler_words: Dict[str, int] = {}
    repeated_words: List[str] = []
    confidence: float = 1.0
    method: str = "browser_speech"
