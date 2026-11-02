from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.roadmap import CareerRoadmap, RoadmapMilestone
from app.schemas.roadmap import (
    RoadmapGenerateRequest,
    RoadmapResponse,
    TaskToggleRequest,
    MilestoneToggleRequest
)
from app.services.auth_service import get_current_user
from app.services.roadmap_service import roadmap_service

router = APIRouter(prefix="/roadmaps", tags=["AI Dynamic Career Roadmaps"])

@router.post("/generate", response_model=RoadmapResponse)
def generate_career_roadmap(
    req: RoadmapGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dynamically generates personalized career roadmap tailored to role,
    daily study hours, existing skills, and career milestones.
    """
    # 1. Generate roadmap data via service
    data = roadmap_service.generate_career_roadmap(
        target_role=req.target_role,
        current_level=req.current_level,
        education=req.education,
        existing_skills=req.existing_skills or current_user.skills or [],
        daily_study_hours=req.daily_study_hours,
        career_goal=req.career_goal,
        timeline_months=req.timeline_months,
        user_llm_provider=current_user.llm_preference,
        api_key=current_user.groq_api_key,
        ollama_endpoint=current_user.ollama_endpoint
    )

    # 2. Save CareerRoadmap in DB
    new_roadmap = CareerRoadmap(
        user_id=current_user.id,
        target_role=data["target_role"],
        current_level=data["current_level"],
        education=data["education"],
        existing_skills=data["existing_skills"],
        daily_study_hours=data["daily_study_hours"],
        career_goal=data["career_goal"],
        timeline_months=data["timeline_months"],
        overview=data["overview"],
        key_focus_areas=data["key_focus_areas"],
        daily_study_plan=data["daily_study_plan"],
        weekly_targets=data["weekly_targets"],
        overall_progress=0.0,
        total_tasks=data["total_tasks"],
        completed_tasks=0
    )
    db.add(new_roadmap)
    db.commit()
    db.refresh(new_roadmap)

    # 3. Save Milestone Phases in DB
    for m in data.get("milestones", []):
        milestone_obj = RoadmapMilestone(
            roadmap_id=new_roadmap.id,
            phase_number=m["phase_number"],
            title=m["title"],
            duration=m["duration"],
            estimated_hours=m.get("estimated_hours", 50),
            objectives=m.get("objectives", []),
            topics=m.get("topics", []),
            practice_tasks=m.get("practice_tasks", []),
            recommended_projects=m.get("recommended_projects", []),
            learning_resources=m.get("learning_resources", []),
            interview_questions=m.get("interview_questions", []),
            checklist=m.get("checklist", []),
            phase_progress=0.0,
            is_completed=False
        )
        db.add(milestone_obj)

    db.commit()
    db.refresh(new_roadmap)
    return new_roadmap

@router.get("/", response_model=List[RoadmapResponse])
def get_user_roadmaps(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists all career roadmaps for current user, ordered by creation date."""
    return db.query(CareerRoadmap).filter(
        CareerRoadmap.user_id == current_user.id
    ).order_by(CareerRoadmap.created_at.desc()).all()

@router.get("/{roadmap_id}", response_model=RoadmapResponse)
def get_single_roadmap(
    roadmap_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetches a single career roadmap with all milestones and checklist progress."""
    roadmap = db.query(CareerRoadmap).filter(
        CareerRoadmap.id == roadmap_id,
        CareerRoadmap.user_id == current_user.id
    ).first()

    if not roadmap:
        raise HTTPException(status_code=404, detail="Career roadmap not found.")
    return roadmap

@router.put("/{roadmap_id}/milestones/{milestone_id}/task")
def toggle_roadmap_checklist_task(
    roadmap_id: int,
    milestone_id: int,
    task_req: TaskToggleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Marks a checklist task as completed or incomplete, automatically
    recalculating milestone progress and overall roadmap progress percentage.
    """
    try:
        result = roadmap_service.toggle_task_and_recalculate_progress(
            db=db,
            roadmap_id=roadmap_id,
            milestone_id=milestone_id,
            task_id=task_req.task_id,
            is_done=task_req.is_done,
            user_id=current_user.id
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task toggle failed: {str(e)}")

@router.put("/milestones/{milestone_id}/toggle")
def toggle_milestone(
    milestone_id: int,
    toggle_in: MilestoneToggleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Legacy milestone completion toggle (maintained for backward compatibility)."""
    milestone = db.query(RoadmapMilestone).join(CareerRoadmap).filter(
        RoadmapMilestone.id == milestone_id,
        CareerRoadmap.user_id == current_user.id
    ).first()

    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    milestone.is_completed = toggle_in.is_completed
    milestone.phase_progress = 100.0 if toggle_in.is_completed else 0.0

    # Mark all checklist items matching state
    if milestone.checklist:
        checklist_items = list(milestone.checklist)
        for item in checklist_items:
            item["is_done"] = toggle_in.is_completed
        milestone.checklist = checklist_items

    db.commit()
    return {"status": "success", "is_completed": milestone.is_completed}

@router.delete("/{roadmap_id}")
def delete_roadmap(
    roadmap_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletes a career roadmap."""
    roadmap = db.query(CareerRoadmap).filter(
        CareerRoadmap.id == roadmap_id,
        CareerRoadmap.user_id == current_user.id
    ).first()

    if not roadmap:
        raise HTTPException(status_code=404, detail="Career roadmap not found.")

    db.delete(roadmap)
    db.commit()
    return {"status": "success", "message": "Roadmap deleted successfully."}
