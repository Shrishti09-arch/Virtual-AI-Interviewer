import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class MockInterview(Base):
    """
    MockInterviews table adhering to Section 11 Database specification:
    - id
    - user_id
    - role
    - interview_type
    - transcript
    - overall_score
    - recording_path
    - created_at
    """
    __tablename__ = "mock_interviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String(255), nullable=False)
    interview_type = Column(String(50), default="Technical")
    transcript = Column(Text, nullable=True)
    overall_score = Column(Float, default=0.0)
    recording_path = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    answers = relationship("InterviewAnswer", back_populates="interview", cascade="all, delete-orphan")


class InterviewAnswer(Base):
    """
    InterviewAnswers table adhering to Section 11 Database specification:
    - id
    - interview_id
    - question
    - answer
    - technical_score
    - communication_feedback
    """
    __tablename__ = "interview_answers"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("mock_interviews.id"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    technical_score = Column(Float, default=0.0)
    communication_feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    interview = relationship("MockInterview", back_populates="answers")


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role_title = Column(String(255), nullable=False)
    experience_level = Column(String(50), default="Mid-Level") # Student/Fresher, 1-3 years, 4-7 years, 8+ years
    interview_type = Column(String(50), default="Technical") # Technical, HR, Behavioral, Managerial, AI/ML, Coding, Company-specific
    difficulty = Column(String(50), default="Intermediate") # Beginner, Intermediate, Advanced, Expert
    technical_subjects = Column(JSON, default=list) # List of technical subjects covered
    interview_duration_mins = Column(Integer, default=15)
    target_company = Column(String(100), nullable=True) # e.g. Google, Amazon, Meta
    status = Column(String(50), default="in_progress") # in_progress, completed, abandoned
    total_questions = Column(Integer, default=5)
    current_question_index = Column(Integer, default=0)
    duration_seconds = Column(Integer, default=0)
    
    # Aggregated Performance Scores (0-100)
    overall_score = Column(Float, default=0.0)
    technical_score = Column(Float, default=0.0)
    communication_score = Column(Float, default=0.0)
    behavioral_score = Column(Float, default=0.0)
    answer_quality_score = Column(Float, default=0.0)
    problem_solving_score = Column(Float, default=0.0)
    verdict = Column(String(50), default="Pending") # Strong Hire, Hire, Lean Hire, Needs Improvement
    
    # Qualitative Feedback & Action Plan
    overall_summary = Column(Text, nullable=True)
    key_strengths = Column(JSON, default=list)
    areas_to_improve = Column(JSON, default=list)
    recommended_topics = Column(JSON, default=list)
    improvement_plan = Column(JSON, default=list)
    full_transcript = Column(Text, nullable=True)
    assessment_disclaimer = Column(Text, default="Notice: Audio, video, and speech analyses are heuristic indicators designed for career coaching. Antigravity AI does not claim to detect personality, honesty, or cognitive suitability from facial appearance.")
    
    # Communication Analytics
    total_filler_words = Column(Integer, default=0)
    average_wpm = Column(Float, default=0.0)
    clarity_rating = Column(String(50), default="Good")

    # Security: Explicit Candidate Recording Consent & Isolated Private Storage
    recording_consent = Column(Boolean, default=True)
    recording_consent_timestamp = Column(DateTime, nullable=True)
    recording_path = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    questions = relationship("InterviewSessionQuestion", back_populates="session", cascade="all, delete-orphan", order_by="InterviewSessionQuestion.question_order")


class InterviewSessionQuestion(Base):
    __tablename__ = "interview_session_questions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False, index=True)
    question_order = Column(Integer, default=1)
    category = Column(String(100), default="Technical")
    question_text = Column(Text, nullable=False)
    is_follow_up = Column(Boolean, default=False)
    difficulty_level = Column(String(50), default="Intermediate")
    
    # Candidate Response & Video Reference
    candidate_answer = Column(Text, nullable=True)
    time_spent_seconds = Column(Integer, default=0)
    has_local_recording = Column(Boolean, default=False)
    recording_storage_key = Column(String(255), nullable=True) # Browser IndexedDB storage key
    
    # Evaluation Metrics
    score = Column(Float, default=0.0) # 0-100
    score_out_of_10 = Column(Float, default=0.0) # 0-10
    technical_accuracy = Column(Float, default=0.0)
    completeness = Column(Float, default=0.0)
    problem_solving_rating = Column(Float, default=0.0)
    feedback = Column(Text, nullable=True)
    correct_points = Column(JSON, default=list)
    incorrect_points = Column(JSON, default=list)
    missing_concepts = Column(JSON, default=list)
    model_answer = Column(Text, nullable=True)
    ideal_answer = Column(Text, nullable=True)
    improvement_suggestions = Column(Text, nullable=True)
    
    # Speech & Communication metrics
    filler_words = Column(JSON, default=dict) # e.g. {"um": 2, "like": 1}
    repeated_words = Column(JSON, default=list) # e.g. ["the the", "I I"]
    pauses_count = Column(Integer, default=0)
    wpm = Column(Float, default=0.0)
    vocabulary_score = Column(Float, default=0.0)
    star_analysis = Column(JSON, default=dict) # Situation, Task, Action, Result flags
    
    # AI Provider Metadata
    is_fallback = Column(Boolean, default=False)
    provider_used = Column(String(50), default="fallback_engine")
    model_used = Column(String(100), default="rule-based-heuristics-v1")
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    answered_at = Column(DateTime, nullable=True)

    session = relationship("InterviewSession", back_populates="questions")


# Backward compatibility alias
InterviewQuestion = InterviewSessionQuestion
