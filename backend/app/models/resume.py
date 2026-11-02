import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Float, event
from sqlalchemy.orm import relationship
from app.database import Base

class Resume(Base):
    """
    Resumes table adhering to Section 11 Database specification:
    - id
    - user_id
    - original_filename
    - extracted_text
    - ats_score
    - created_at
    """
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    original_filename = Column(String(255), nullable=True)
    file_name = Column(String(255), nullable=True)
    extracted_text = Column(Text, nullable=True)
    raw_text = Column(Text, nullable=True)
    ats_score = Column(Float, default=0.0)
    title = Column(String(255), default="My Resume")
    target_role = Column(String(255), nullable=True)
    target_company = Column(String(255), nullable=True)
    parsed_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    versions = relationship("ResumeVersion", back_populates="resume", cascade="all, delete-orphan")
    analyses = relationship("ResumeAnalysis", back_populates="resume", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        if "file_name" in kwargs and "original_filename" not in kwargs:
            kwargs["original_filename"] = kwargs["file_name"]
        elif "original_filename" in kwargs and "file_name" not in kwargs:
            kwargs["file_name"] = kwargs["original_filename"]

        if "raw_text" in kwargs and "extracted_text" not in kwargs:
            kwargs["extracted_text"] = kwargs["raw_text"]
        elif "extracted_text" in kwargs and "raw_text" not in kwargs:
            kwargs["raw_text"] = kwargs["extracted_text"]
        super().__init__(**kwargs)


@event.listens_for(Resume, "before_insert")
def sync_resume_fields_insert(mapper, connection, target):
    if target.original_filename and not target.file_name:
        target.file_name = target.original_filename
    elif target.file_name and not target.original_filename:
        target.original_filename = target.file_name

    if target.extracted_text and not target.raw_text:
        target.raw_text = target.extracted_text
    elif target.raw_text and not target.extracted_text:
        target.extracted_text = target.raw_text


@event.listens_for(Resume, "before_update")
def sync_resume_fields_update(mapper, connection, target):
    if target.original_filename and not target.file_name:
        target.file_name = target.original_filename
    elif target.file_name and not target.original_filename:
        target.original_filename = target.file_name

    if target.extracted_text and not target.raw_text:
        target.raw_text = target.extracted_text
    elif target.raw_text and not target.extracted_text:
        target.extracted_text = target.raw_text


class ResumeVersion(Base):
    """
    ResumeVersions table adhering to Section 11 Database specification:
    - id
    - resume_id
    - target_role
    - generated_content
    - created_at
    """
    __tablename__ = "resume_versions"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False, index=True)
    target_role = Column(String(255), nullable=False)
    generated_content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    resume = relationship("Resume", back_populates="versions")


class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    target_role = Column(String(255), nullable=False)
    job_description = Column(Text, nullable=True)
    
    # Scores
    overall_ats_score = Column(Float, default=0.0)
    keyword_match_score = Column(Float, default=0.0)
    structure_score = Column(Float, default=0.0)
    impact_score = Column(Float, default=0.0)
    
    # Detailed analytics
    matched_skills = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    formatting_issues = Column(JSON, default=list)
    action_verb_suggestions = Column(JSON, default=list)
    section_breakdown = Column(JSON, default=dict)
    detailed_feedback = Column(Text, nullable=True)

    # Enhanced Module 1 ATS & AI Correction Fields
    section_scores = Column(JSON, default=dict)
    grammar_errors = Column(JSON, default=list)
    weak_sentences = Column(JSON, default=list)
    corrections = Column(JSON, default=list)
    readability_metrics = Column(JSON, default=dict)
    disclaimer = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    resume = relationship("Resume", back_populates="analyses")
