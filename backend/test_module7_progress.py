import sys
import os
import datetime

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.database import SessionLocal
from app.models.user import User
from app.models.interview import InterviewSession, InterviewQuestion
from app.models.resume import Resume, ResumeAnalysis
from app.models.practice import PracticeSession, PracticeSubmission
from app.models.roadmap import CareerRoadmap, RoadmapMilestone
from app.routers import analytics

def test_module7_progress():
    print("\n=======================================================")
    print("RUNNING COMPLETE MODULE 7 PROGRESS TRACKING & ANALYTICS TEST")
    print("=======================================================")

    db = SessionLocal()

    # 1. Setup test user
    user = db.query(User).filter(User.email == "module7_user@test.com").first()
    if not user:
        user = User(
            email="module7_user@test.com",
            hashed_password="hashed_pw_test",
            full_name="Alex Mercer",
            role_target="Full Stack Developer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Clean existing user data for reproducible testing
    db.query(InterviewQuestion).filter(InterviewQuestion.session_id.in_(
        db.query(InterviewSession.id).filter(InterviewSession.user_id == user.id)
    )).delete(synchronize_session=False)
    db.query(InterviewSession).filter(InterviewSession.user_id == user.id).delete()
    db.query(ResumeAnalysis).filter(ResumeAnalysis.user_id == user.id).delete()
    db.query(Resume).filter(Resume.user_id == user.id).delete()
    db.query(PracticeSession).filter(PracticeSession.user_id == user.id).delete()
    db.query(PracticeSubmission).filter(PracticeSubmission.user_id == user.id).delete()
    db.query(RoadmapMilestone).filter(RoadmapMilestone.roadmap_id.in_(
        db.query(CareerRoadmap.id).filter(CareerRoadmap.user_id == user.id)
    )).delete(synchronize_session=False)
    db.query(CareerRoadmap).filter(CareerRoadmap.user_id == user.id).delete()
    db.commit()

    # 2. Seed Mock Interviews
    print("\n--- 1. Seeding Mock Interviews ---")
    intv1 = InterviewSession(
        user_id=user.id,
        role_title="Senior Python Developer",
        experience_level="Mid-Level",
        interview_type="Technical",
        difficulty="Intermediate",
        status="completed",
        overall_score=85.0,
        technical_score=90.0,
        communication_score=80.0,
        verdict="Strong Hire",
        duration_seconds=900,
        total_questions=5,
        created_at=datetime.datetime.utcnow() - datetime.timedelta(days=2)
    )
    intv2 = InterviewSession(
        user_id=user.id,
        role_title="Full Stack Developer",
        experience_level="Mid-Level",
        interview_type="Technical",
        difficulty="Intermediate",
        status="completed",
        overall_score=75.0,
        technical_score=70.0,
        communication_score=80.0,
        verdict="Hire",
        duration_seconds=720,
        total_questions=5,
        created_at=datetime.datetime.utcnow() - datetime.timedelta(days=1)
    )
    db.add_all([intv1, intv2])
    db.commit()
    print("[PASS] 2 completed mock interview sessions seeded.")

    # 3. Seed Resumes & ATS Scans (Initial vs Latest)
    print("\n--- 2. Seeding Resumes & ATS Scans ---")
    res_obj = Resume(
        user_id=user.id,
        title="Alex Mercer CV",
        target_role="Full Stack Developer"
    )
    db.add(res_obj)
    db.commit()
    db.refresh(res_obj)

    scan1 = ResumeAnalysis(
        resume_id=res_obj.id,
        user_id=user.id,
        target_role="Backend Developer",
        overall_ats_score=62.0,
        keyword_match_score=60.0,
        structure_score=65.0,
        impact_score=60.0,
        missing_skills=["Kubernetes", "Redis"],
        created_at=datetime.datetime.utcnow() - datetime.timedelta(days=3)
    )
    scan2 = ResumeAnalysis(
        resume_id=res_obj.id,
        user_id=user.id,
        target_role="Full Stack Developer",
        overall_ats_score=84.0,
        keyword_match_score=85.0,
        structure_score=85.0,
        impact_score=82.0,
        missing_skills=["GraphQL"],
        created_at=datetime.datetime.utcnow()
    )
    db.add_all([scan1, scan2])
    db.commit()
    print("[PASS] Initial scan (62.0) and latest scan (84.0) seeded.")

    # 4. Seed Practice Sessions (Strong vs Weak Subjects)
    print("\n--- 3. Seeding Practice Sessions (Strong vs Weak Subjects) ---")
    # Strong subject: Python (5/5 = 100%)
    ps_strong = PracticeSession(
        user_id=user.id,
        job_role="Python Developer",
        subject="Python",
        difficulty="Intermediate",
        interview_type="Comprehensive Mixed",
        total_questions=5,
        current_index=5,
        is_completed=True,
        correct_count=5,
        incorrect_count=0,
        accuracy=100.0,
        created_at=datetime.datetime.utcnow() - datetime.timedelta(days=1)
    )
    # Weak subject: Computer Networks (2/5 = 40%)
    ps_weak = PracticeSession(
        user_id=user.id,
        job_role="Network & Backend",
        subject="Computer Networks",
        difficulty="Intermediate",
        interview_type="Comprehensive Mixed",
        total_questions=5,
        current_index=5,
        is_completed=True,
        correct_count=2,
        incorrect_count=3,
        accuracy=40.0,
        created_at=datetime.datetime.utcnow()
    )
    db.add_all([ps_strong, ps_weak])
    db.commit()
    print("[PASS] Python (100% accuracy) and Computer Networks (40% accuracy) sessions seeded.")

    # 5. Seed Career Roadmap & Completed Tasks
    print("\n--- 4. Seeding Career Roadmap & Checklist Tasks ---")
    roadmap = CareerRoadmap(
        user_id=user.id,
        target_role="Full Stack Developer",
        current_level="Intermediate",
        daily_study_hours=2.5,
        total_tasks=8,
        completed_tasks=4,
        overall_progress=50.0,
        updated_at=datetime.datetime.utcnow()
    )
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)

    m1 = RoadmapMilestone(
        roadmap_id=roadmap.id,
        phase_number=1,
        title="Phase 1: Full-Stack Foundations",
        duration="Weeks 1-4",
        estimated_hours=40,
        phase_progress=100.0,
        is_completed=True,
        checklist=[
            {"id": "c1", "task": "Async I/O Patterns", "is_done": True},
            {"id": "c2", "task": "RESTful API Contracts", "is_done": True},
            {"id": "c3", "task": "PostgreSQL Indexing", "is_done": True},
            {"id": "c4", "task": "Unit & Integration Tests", "is_done": True}
        ]
    )
    m2 = RoadmapMilestone(
        roadmap_id=roadmap.id,
        phase_number=2,
        title="Phase 2: Scalability & Cloud Architecture",
        duration="Weeks 5-8",
        estimated_hours=40,
        phase_progress=0.0,
        is_completed=False,
        checklist=[
            {"id": "c5", "task": "Distributed Caching with Redis", "is_done": False},
            {"id": "c6", "task": "Docker & Kubernetes Deployment", "is_done": False},
            {"id": "c7", "task": "Load Balancing & Rate Limiting", "is_done": False},
            {"id": "c8", "task": "CI/CD Pipeline Automation", "is_done": False}
        ]
    )
    db.add_all([m1, m2])
    db.commit()
    print("[PASS] Roadmap with 4/8 tasks completed (50%) seeded.")

    # 6. Execute Analytics Function & Verify Metrics
    print("\n--- 5. Executing Analytics Function & Asserting Progress Metrics ---")
    res = analytics.get_user_dashboard_and_progress_analytics(current_user=user, db=db)

    # 1. Total Interviews & Average Score
    assert res["total_interviews"] == 2, f"Expected 2 interviews, got {res['total_interviews']}"
    assert res["average_interview_score"] == 80.0, f"Expected 80.0 avg score, got {res['average_interview_score']}"
    assert res["average_technical_score"] == 80.0
    assert res["average_communication_score"] == 80.0
    print(f"[PASS] Total Interviews: {res['total_interviews']} | Avg Score: {res['average_interview_score']}%")

    # 2. ATS Improvement Tracking
    assert res["ats_improvement"]["initial_score"] == 62.0
    assert res["ats_improvement"]["latest_score"] == 84.0
    assert res["ats_improvement"]["delta"] == 22.0
    assert res["ats_improvement"]["percent_change"] == 35.5
    assert len(res["ats_improvement"]["history"]) == 2
    print(f"[PASS] ATS Improvement: {res['ats_improvement']['initial_score']} -> {res['ats_improvement']['latest_score']} (Delta: +{res['ats_improvement']['delta']} pts, +{res['ats_improvement']['percent_change']}%)")

    # 3. Technical Practice Accuracy
    # Total questions = 10, correct = 7 -> 70.0%
    assert res["technical_practice_accuracy"] == 70.0, f"Expected 70.0% accuracy, got {res['technical_practice_accuracy']}%"
    assert res["total_practice_sessions"] == 2
    assert res["total_practice_questions"] == 10
    print(f"[PASS] Technical Practice Accuracy: {res['technical_practice_accuracy']}% ({res['total_practice_questions']} questions across {res['total_practice_sessions']} sessions)")

    # 4. Completed Roadmap Tasks
    assert res["completed_roadmap_tasks"] == 4, f"Expected 4 completed tasks, got {res['completed_roadmap_tasks']}"
    assert res["total_roadmap_tasks"] == 8, f"Expected 8 total tasks, got {res['total_roadmap_tasks']}"
    assert res["roadmap_progress"]["progress_pct"] == 50.0
    assert res["roadmap_progress"]["completed_milestones"] == 1
    assert res["roadmap_progress"]["total_milestones"] == 2
    print(f"[PASS] Roadmap Tasks: {res['completed_roadmap_tasks']} of {res['total_roadmap_tasks']} completed ({res['roadmap_progress']['progress_pct']}%)")

    # 5. Strong Subjects (>= 80%) & Weak Subjects (< 70%)
    strong_names = [s["subject"] for s in res["strong_subjects"]]
    weak_names = [w["subject"] for w in res["weak_subjects"]]
    assert "Python" in strong_names, f"Python should be in strong subjects: {strong_names}"
    assert "Computer Networks" in weak_names, f"Computer Networks should be in weak subjects: {weak_names}"

    python_item = next(s for s in res["strong_subjects"] if s["subject"] == "Python")
    assert python_item["accuracy"] == 100.0
    assert python_item["status"] == "Strong"

    cn_item = next(w for w in res["weak_subjects"] if w["subject"] == "Computer Networks")
    assert cn_item["accuracy"] == 40.0
    assert cn_item["status"] == "Weak"
    assert "recommendation" in cn_item
    print(f"[PASS] Strong Subjects (>=80%): {[(s['subject'], s['accuracy']) for s in res['strong_subjects']]}")
    print(f"[PASS] Weak Subjects (<70%): {[(w['subject'], w['accuracy'], w['recommendation']) for w in res['weak_subjects']]}")

    # 6. Weekly Learning Activity (7 Days Distribution)
    assert len(res["weekly_learning_activity"]) == 7, "Should have 7 daily activity records"
    total_week_activities = sum(d["total_activities"] for d in res["weekly_learning_activity"])
    assert total_week_activities > 0, "Should have activities recorded in the past 7 days"
    print(f"[PASS] Weekly Learning Activity: 7 days tracked, total activity items = {total_week_activities}")

    # 7. Comprehensive History Logs
    assert len(res["interview_history"]) == 2
    assert len(res["practice_history"]) == 2
    assert len(res["resume_history"]) == 2
    assert len(res["roadmap_progress"]["milestones"]) == 2
    print("[PASS] Comprehensive History Logs verified for Interviews, Practice, Resumes, and Roadmap Milestones.")

    print("\n=======================================================")
    print("ALL MODULE 7 PROGRESS TRACKING & ANALYTICS TESTS PASSED!")
    print("=======================================================\n")

if __name__ == "__main__":
    test_module7_progress()
