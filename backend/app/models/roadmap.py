import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from app.database import Base

class Roadmap(Base):
    """
    Roadmaps table adhering to Section 11 Database specification:
    - id
    - user_id
    - target_role
    - roadmap_content
    - progress
    - created_at
    """
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    target_role = Column(String(255), nullable=False)
    roadmap_content = Column(Text, nullable=False)
    progress = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class CareerRoadmap(Base):
    __tablename__ = "career_roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    target_role = Column(String(255), nullable=False)
    current_level = Column(String(100), default="Fresher / Entry-Level") # Beginner, Intermediate, Advanced
    education = Column(String(100), default="Computer Science Degree")
    existing_skills = Column(JSON, default=list)
    daily_study_hours = Column(Float, default=2.0)
    career_goal = Column(String(255), default="Land First Professional Software Role")
    timeline_months = Column(Integer, default=6)
    overview = Column(Text, nullable=True)
    key_focus_areas = Column(JSON, default=list)
    daily_study_plan = Column(JSON, default=dict) # {"routine": [...], "breakdown": [...]}
    weekly_targets = Column(JSON, default=list) # ["Week 1: ...", "Week 2: ..."]
    overall_progress = Column(Float, default=0.0) # 0.0 - 100.0%
    total_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    milestones = relationship("RoadmapMilestone", back_populates="roadmap", cascade="all, delete-orphan", order_by="RoadmapMilestone.phase_number")


class RoadmapMilestone(Base):
    __tablename__ = "roadmap_milestones"

    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("career_roadmaps.id"), nullable=False, index=True)
    phase_number = Column(Integer, default=1)
    title = Column(String(255), nullable=False)
    duration = Column(String(100), default="Weeks 1-4")
    estimated_hours = Column(Integer, default=50)
    objectives = Column(JSON, default=list)
    topics = Column(JSON, default=list) # Granular topics
    practice_tasks = Column(JSON, default=list) # Concrete exercises
    recommended_projects = Column(JSON, default=list) # [{name, description, tech_stack}]
    learning_resources = Column(JSON, default=list) # [{title, type, link}]
    interview_questions = Column(JSON, default=list) # Top questions for this phase
    checklist = Column(JSON, default=list) # [{"id": "chk_1", "task": "...", "is_done": False}]
    phase_progress = Column(Float, default=0.0) # 0.0 - 100.0%
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    roadmap = relationship("CareerRoadmap", back_populates="milestones")
