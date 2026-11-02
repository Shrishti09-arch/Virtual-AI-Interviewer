import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Float, Boolean, event
from app.database import Base

class InterviewQuestion(Base):
    """
    InterviewQuestions table adhering to Section 11 Database specification:
    - id
    - role
    - subject
    - question
    - difficulty
    - source
    - source_url
    - created_at
    """
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(100), default="Full Stack Engineer")
    role_track = Column(String(100), default="Full Stack Engineer")
    subject = Column(String(100), index=True, default="Computer Science Fundamentals")
    question = Column(Text, nullable=False)
    question_text = Column(Text, nullable=True)
    difficulty = Column(String(50), default="Intermediate")
    source = Column(String(100), default="Official Educational Standard")
    source_name = Column(String(100), default="Official Educational Standard")
    source_url = Column(String(255), nullable=True)
    
    # Extended Question Bank capabilities
    category = Column(String(100), index=True, default="Computer Science")
    programming_language = Column(String(50), default="Python")
    question_type = Column(String(50), default="Theory")
    title = Column(String(255), nullable=True)
    expected_keywords = Column(JSON, default=list)
    sample_answer = Column(Text, nullable=True)
    hints = Column(JSON, default=list)
    options = Column(JSON, default=list)
    correct_option_index = Column(Integer, nullable=True)
    explanation = Column(Text, nullable=True)
    code_template = Column(Text, nullable=True)
    test_cases = Column(JSON, default=list)
    source_type = Column(String(50), default="curated_educational")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, **kwargs):
        if "role_track" in kwargs and "role" not in kwargs:
            kwargs["role"] = kwargs["role_track"]
        elif "role" in kwargs and "role_track" not in kwargs:
            kwargs["role_track"] = kwargs["role"]

        if "question_text" in kwargs and "question" not in kwargs:
            kwargs["question"] = kwargs["question_text"]
        elif "question" in kwargs and "question_text" not in kwargs:
            kwargs["question_text"] = kwargs["question"]

        if "source_name" in kwargs and "source" not in kwargs:
            kwargs["source"] = kwargs["source_name"]
        elif "source" in kwargs and "source_name" not in kwargs:
            kwargs["source_name"] = kwargs["source"]

        if "title" not in kwargs or not kwargs["title"]:
            q_val = kwargs.get("question") or kwargs.get("question_text") or "Technical Question"
            kwargs["title"] = q_val[:80]

        super().__init__(**kwargs)


@event.listens_for(InterviewQuestion, "before_insert")
def sync_iq_fields_insert(mapper, connection, target):
    if target.role and not target.role_track:
        target.role_track = target.role
    elif target.role_track and not target.role:
        target.role = target.role_track

    if target.question and not target.question_text:
        target.question_text = target.question
    elif target.question_text and not target.question:
        target.question = target.question_text

    if target.source and not target.source_name:
        target.source_name = target.source
    elif target.source_name and not target.source:
        target.source = target.source_name


@event.listens_for(InterviewQuestion, "before_update")
def sync_iq_fields_update(mapper, connection, target):
    if target.role and not target.role_track:
        target.role_track = target.role
    elif target.role_track and not target.role:
        target.role = target.role_track

    if target.question and not target.question_text:
        target.question_text = target.question
    elif target.question_text and not target.question:
        target.question = target.question_text

    if target.source and not target.source_name:
        target.source_name = target.source
    elif target.source_name and not target.source:
        target.source = target.source_name


# Backward compatibility alias
QuestionBank = InterviewQuestion


class PracticeSession(Base):
    """
    PracticeSessions table adhering to Section 11 Database specification:
    - id
    - user_id
    - role
    - subject
    - score
    - created_at
    """
    __tablename__ = "practice_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String(100), nullable=True)
    job_role = Column(String(100), nullable=True)
    subject = Column(String(100), nullable=False)
    score = Column(Float, default=0.0)
    accuracy = Column(Float, default=0.0)
    programming_language = Column(String(50), default="Python")
    difficulty = Column(String(50), default="Intermediate")
    interview_type = Column(String(50), default="Comprehensive Mixed")
    total_questions = Column(Integer, default=5)
    current_index = Column(Integer, default=0)
    is_completed = Column(Boolean, default=False)
    question_ids = Column(JSON, default=list)
    answers = Column(JSON, default=list)
    correct_count = Column(Integer, default=0)
    incorrect_count = Column(Integer, default=0)
    topic_performance = Column(JSON, default=dict)
    weak_areas = Column(JSON, default=list)
    recommended_topics = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, **kwargs):
        if "job_role" in kwargs and "role" not in kwargs:
            kwargs["role"] = kwargs["job_role"]
        elif "role" in kwargs and "job_role" not in kwargs:
            kwargs["job_role"] = kwargs["role"]

        if "accuracy" in kwargs and "score" not in kwargs:
            kwargs["score"] = kwargs["accuracy"]
        elif "score" in kwargs and "accuracy" not in kwargs:
            kwargs["accuracy"] = kwargs["score"]
        super().__init__(**kwargs)


@event.listens_for(PracticeSession, "before_insert")
def sync_ps_fields_insert(mapper, connection, target):
    if target.role and not target.job_role:
        target.job_role = target.role
    elif target.job_role and not target.role:
        target.role = target.job_role

    if target.score is not None and target.accuracy is None:
        target.accuracy = target.score
    elif target.accuracy is not None and target.score is None:
        target.score = target.accuracy


@event.listens_for(PracticeSession, "before_update")
def sync_ps_fields_update(mapper, connection, target):
    if target.role and not target.job_role:
        target.job_role = target.role
    elif target.job_role and not target.role:
        target.role = target.job_role

    if target.score is not None and target.accuracy is None:
        target.accuracy = target.score
    elif target.accuracy is not None and target.score is None:
        target.score = target.accuracy


class PracticeSubmission(Base):
    __tablename__ = "practice_submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("interview_questions.id"), nullable=False)
    user_answer = Column(Text, nullable=False)
    score = Column(Float, default=0.0)
    feedback = Column(Text, nullable=True)
    strengths = Column(JSON, default=list)
    missing_concepts = Column(JSON, default=list)
    is_fallback = Column(Boolean, default=False)
    provider_used = Column(String(50), default="fallback_engine")
    model_used = Column(String(100), default="rule-based-heuristics-v1")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class UserQuestionHistory(Base):
    __tablename__ = "user_question_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("interview_questions.id"), nullable=False)
    attempted_at = Column(DateTime, default=datetime.datetime.utcnow)
