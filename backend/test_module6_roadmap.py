import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.database import SessionLocal
from app.models.user import User
from app.models.roadmap import CareerRoadmap, RoadmapMilestone
from app.routers import roadmaps
from app.schemas.roadmap import (
    RoadmapGenerateRequest,
    TaskToggleRequest
)

def test_module6_roadmap():
    print("\n=======================================================")
    print("RUNNING COMPLETE MODULE 6 DYNAMIC CAREER ROADMAP TEST SUITE")
    print("=======================================================")

    db = SessionLocal()

    # 1. Setup test user
    user = db.query(User).filter(User.email == "module6_user@test.com").first()
    if not user:
        user = User(
            email="module6_user@test.com",
            hashed_password="hashed_pw_test",
            full_name="Morgan Chase",
            role_target="Full Stack Developer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 2. Test Dynamic Roadmap Generation for Full Stack Developer
    print("\n--- 1. Testing Dynamic Roadmap Generation & Study Plan ---")
    gen_req = RoadmapGenerateRequest(
        target_role="Full Stack Developer",
        current_level="Beginner",
        education="Computer Science Degree",
        existing_skills=["HTML", "Basic JavaScript"],
        daily_study_hours=3.0,
        career_goal="Land First Junior Full-Stack Engineer Role",
        timeline_months=6
    )

    roadmap = roadmaps.generate_career_roadmap(req=gen_req, current_user=user, db=db)
    roadmap_id = roadmap.id
    assert roadmap_id is not None
    assert roadmap.target_role == "Full Stack Developer"
    assert roadmap.daily_study_hours == 3.0
    assert len(roadmap.milestones) == 4
    assert roadmap.overall_progress == 0.0
    assert roadmap.total_tasks > 0

    print(f"[PASS] Roadmap #{roadmap_id} generated for {roadmap.target_role}:")
    print(f"       Total Tasks: {roadmap.total_tasks} | Initial Progress: {roadmap.overall_progress}%")
    print(f"       Overview: {roadmap.overview[:120]}...")
    print(f"       Daily Study Plan: {roadmap.daily_study_plan['total_daily_minutes']} mins daily across {len(roadmap.daily_study_plan['routine'])} blocks.")
    assert len(roadmap.daily_study_plan["routine"]) == 3
    assert len(roadmap.weekly_targets) >= 4

    # 3. Test Phase Details (Topics, Free Resources, Projects, Checklist)
    print("\n--- 2. Testing Phase Curriculum & Verified Free Resources ---")
    p1 = roadmap.milestones[0]
    assert len(p1.topics) >= 4, "Phase 1 should have granular topics"
    assert len(p1.practice_tasks) >= 2, "Phase 1 should have practice tasks"
    assert len(p1.recommended_projects) >= 1, "Phase 1 should have portfolio project"
    assert len(p1.learning_resources) >= 2, "Phase 1 should have free educational resources"
    assert len(p1.interview_questions) >= 2, "Phase 1 should have interview questions"
    assert len(p1.checklist) >= 4, "Phase 1 should have actionable checklist"

    print(f"[PASS] Phase 1: [{p1.title}] ({p1.duration}):")
    print(f"       Topics: {p1.topics[:3]}")
    print(f"       Project: {p1.recommended_projects[0]['name']} (Stack: {p1.recommended_projects[0]['tech_stack']})")
    print(f"       Free Resource: {p1.learning_resources[0]['title']} -> {p1.learning_resources[0]['link']}")
    assert p1.learning_resources[0]["link"].startswith("http")

    # 4. Test Interactive Task Checkoff & Automatic Progress Calculation
    print("\n--- 3. Testing Interactive Checklist Completion & Progress Recalculation ---")
    first_task = p1.checklist[0]
    task_id = first_task["id"]
    print(f"       Toggling task [{task_id}]: '{first_task['task']}' -> Completed")

    toggle_req = TaskToggleRequest(task_id=task_id, is_done=True)
    res = roadmaps.toggle_roadmap_checklist_task(
        roadmap_id=roadmap_id,
        milestone_id=p1.id,
        task_req=toggle_req,
        current_user=user,
        db=db
    )

    assert res["status"] == "success"
    assert res["is_done"] is True
    assert res["completed_tasks"] == 1
    assert res["phase_progress"] > 0.0
    assert res["overall_progress"] > 0.0

    print(f"[PASS] Task checked off:")
    print(f"       Phase 1 Progress: {res['phase_progress']}%")
    print(f"       Roadmap Overall Progress: {res['overall_progress']}% ({res['completed_tasks']}/{res['total_tasks']} tasks completed)")

    # Toggle second task in Phase 1
    second_task = p1.checklist[1]
    res2 = roadmaps.toggle_roadmap_checklist_task(
        roadmap_id=roadmap_id,
        milestone_id=p1.id,
        task_req=TaskToggleRequest(task_id=second_task["id"], is_done=True),
        current_user=user,
        db=db
    )
    assert res2["completed_tasks"] == 2
    assert res2["overall_progress"] > res["overall_progress"]
    print(f"[PASS] Second task checked off. New overall progress: {res2['overall_progress']}%")

    # 5. Test AI/ML Role Generation
    print("\n--- 4. Testing AI/ML Engineer Role Generation ---")
    ai_req = RoadmapGenerateRequest(
        target_role="AI/ML Engineer",
        current_level="Intermediate",
        education="STEM Degree",
        daily_study_hours=4.0,
        career_goal="Transition to Applied LLM / RAG Engineer",
        timeline_months=4
    )
    ai_roadmap = roadmaps.generate_career_roadmap(req=ai_req, current_user=user, db=db)
    assert ai_roadmap.target_role == "AI/ML Engineer"
    assert len(ai_roadmap.milestones) == 4
    ai_p3 = ai_roadmap.milestones[2]
    assert "RAG" in ai_p3.title or "Retrieval" in ai_p3.title or "Vector" in ai_p3.title
    print(f"[PASS] AI/ML Roadmap generated. Phase 3: [{ai_p3.title}]")
    print(f"       Project: {ai_p3.recommended_projects[0]['name']}")

    # 6. Test User Roadmaps Retrieval
    print("\n--- 5. Testing Roadmap Retrieval ---")
    user_roadmaps = roadmaps.get_user_roadmaps(current_user=user, db=db)
    assert len(user_roadmaps) >= 2
    print(f"[PASS] Retrieved {len(user_roadmaps)} persistent roadmaps for user.")

    db.close()
    print("\n=======================================================")
    print("ALL MODULE 6 DYNAMIC CAREER ROADMAP TESTS PASSED 100%!")
    print("=======================================================")

if __name__ == "__main__":
    test_module6_roadmap()
