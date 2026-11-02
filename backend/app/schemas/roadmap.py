from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class RoadmapGenerateRequest(BaseModel):
    target_role: str = "Software Development Engineer"
    current_level: str = "Beginner" # Beginner, Intermediate, Advanced
    education: str = "Computer Science Degree" # CS Degree, STEM Degree, Non-Tech, Bootcamp, Self-Taught, Masters
    existing_skills: List[str] = []
    daily_study_hours: float = 2.0 # 1, 2, 3, 4, 6+
    career_goal: str = "Land First Professional Software Role"
    timeline_months: int = Field(6, ge=1, le=24)

class ChecklistTaskItem(BaseModel):
    id: str
    task: str
    is_done: bool = False

class MilestoneItem(BaseModel):
    id: int
    roadmap_id: int
    phase_number: int
    title: str
    duration: str
    estimated_hours: int = 50
    objectives: List[str] = []
    topics: List[str] = []
    practice_tasks: List[str] = []
    recommended_projects: List[Dict[str, Any]] = []
    learning_resources: List[Dict[str, Any]] = []
    interview_questions: List[str] = []
    checklist: List[Dict[str, Any]] = []
    phase_progress: float = 0.0
    is_completed: bool = False

    class Config:
        from_attributes = True

class RoadmapResponse(BaseModel):
    id: int
    target_role: str
    current_level: str
    education: str = "Computer Science Degree"
    existing_skills: List[str] = []
    daily_study_hours: float = 2.0
    career_goal: str = "Land First Professional Software Role"
    timeline_months: int
    overview: str
    key_focus_areas: List[str] = []
    daily_study_plan: Dict[str, Any] = {}
    weekly_targets: List[str] = []
    overall_progress: float = 0.0
    total_tasks: int = 0
    completed_tasks: int = 0
    milestones: List[MilestoneItem] = []
    created_at: datetime

    class Config:
        from_attributes = True

class TaskToggleRequest(BaseModel):
    task_id: str
    is_done: bool

class MilestoneToggleRequest(BaseModel):
    is_completed: bool
