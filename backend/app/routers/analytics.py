import datetime
from collections import Counter
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.interview import InterviewSession, InterviewQuestion
from app.models.resume import ResumeAnalysis
from app.models.practice import PracticeSubmission, PracticeSession, QuestionBank
from app.models.roadmap import CareerRoadmap, RoadmapMilestone
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/analytics", tags=["Performance Analytics & Progress Tracking"])

@router.get("/dashboard")
@router.get("/progress")
def get_user_dashboard_and_progress_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Module 7: Comprehensive Progress Tracking & Dashboard Analytics
    Tracks:
    1. Total interviews & average interview score
    2. ATS improvement (initial, latest, delta, timeline)
    3. Technical practice accuracy (%) & problem statistics
    4. Completed roadmap tasks & milestone progress
    5. Weak subjects (<70% accuracy) with targeted drill recommendations
    6. Strong subjects (>=80% accuracy) with mastery status
    7. Weekly learning activity across the past 7 days (interviews, practice, roadmap, resumes)
    8. Interactive history logs for all modules
    """
    # -------------------------------------------------------------
    # 1. Past Mock Interviews
    # -------------------------------------------------------------
    interviews = db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id
    ).order_by(InterviewSession.created_at.asc()).all()

    interview_trends = []
    total_interview_score = 0.0
    total_tech_score = 0.0
    total_comm_score = 0.0
    completed_interviews = [
        it for it in interviews
        if it.status == "completed" or (it.overall_score is not None and it.overall_score > 0)
    ]
    total_interviews = len(completed_interviews)

    for i, it in enumerate(completed_interviews):
        ov_score = round(it.overall_score or 0.0, 1)
        tc_score = round(it.technical_score or 0.0, 1)
        cm_score = round(it.communication_score or 0.0, 1)

        interview_trends.append({
            "session_number": f"Session #{i+1}",
            "date": it.created_at.strftime("%b %d") if it.created_at else f"Session #{i+1}",
            "role": it.role_title,
            "overall_score": ov_score,
            "technical_score": tc_score,
            "communication_score": cm_score,
            "verdict": it.verdict or "Completed"
        })
        total_interview_score += ov_score
        total_tech_score += tc_score
        total_comm_score += cm_score

    avg_interview_score = round(total_interview_score / total_interviews, 1) if total_interviews > 0 else 75.0
    avg_tech = round(total_tech_score / total_interviews, 1) if total_interviews > 0 else 72.0
    avg_comm = round(total_comm_score / total_interviews, 1) if total_interviews > 0 else 75.0

    interview_history = [
        {
            "id": it.id,
            "session_number": f"Session #{len(interviews) - idx}",
            "role": it.role_title,
            "interview_type": it.interview_type,
            "difficulty": it.difficulty,
            "date": it.created_at.strftime("%b %d, %Y") if it.created_at else "Recently",
            "overall_score": round(it.overall_score or 0.0, 1),
            "technical_score": round(it.technical_score or 0.0, 1),
            "communication_score": round(it.communication_score or 0.0, 1),
            "verdict": it.verdict or "Completed",
            "duration_seconds": it.duration_seconds or (it.interview_duration_mins * 60 if it.interview_duration_mins else 900),
            "total_questions": it.total_questions or 5
        }
        for idx, it in enumerate(reversed(interviews))
    ]

    # -------------------------------------------------------------
    # 2. Resume Improvement Stats (ATS Initial vs Latest & Delta)
    # -------------------------------------------------------------
    analyses = db.query(ResumeAnalysis).filter(
        ResumeAnalysis.user_id == current_user.id
    ).order_by(ResumeAnalysis.created_at.asc()).all()

    total_scans = len(analyses)
    initial_ats_score = round(analyses[0].overall_ats_score, 1) if total_scans > 0 else 60.0
    latest_ats_score = round(analyses[-1].overall_ats_score, 1) if total_scans > 0 else 68.0
    ats_delta = round(latest_ats_score - initial_ats_score, 1)
    ats_pct_change = round(((latest_ats_score - initial_ats_score) / initial_ats_score) * 100, 1) if initial_ats_score > 0 else 0.0

    resume_history = [
        {
            "id": a.id,
            "date": a.created_at.strftime("%b %d, %Y") if a.created_at else "Recently",
            "target_role": a.target_role,
            "ats_score": round(a.overall_ats_score, 1),
            "keyword_match": round(a.keyword_match_score, 1),
            "structure": round(a.structure_score, 1),
            "impact": round(a.impact_score, 1)
        }
        for a in reversed(analyses)
    ]

    # -------------------------------------------------------------
    # 3. Technical Practice Accuracy & Subject Performance
    # -------------------------------------------------------------
    practice_sessions = db.query(PracticeSession).filter(
        PracticeSession.user_id == current_user.id
    ).order_by(PracticeSession.created_at.desc()).all()

    submissions = db.query(PracticeSubmission).filter(
        PracticeSubmission.user_id == current_user.id
    ).order_by(PracticeSubmission.created_at.desc()).all()

    total_practice_sessions = len(practice_sessions)
    total_submissions = len(submissions)

    total_practice_questions = 0
    total_correct_practice = 0
    subject_map: Dict[str, Dict[str, Any]] = {}

    for ps in practice_sessions:
        subj = ps.subject or "Computer Science Fundamentals"
        if subj not in subject_map:
            subject_map[subj] = {
                "subject": subj,
                "total_questions": 0,
                "correct_answers": 0,
                "sessions_count": 0,
                "scores": []
            }
        q_count = ps.total_questions or (ps.correct_count + ps.incorrect_count) or 0
        subject_map[subj]["total_questions"] += q_count
        subject_map[subj]["correct_answers"] += (ps.correct_count or 0)
        subject_map[subj]["sessions_count"] += 1
        if ps.accuracy is not None:
            subject_map[subj]["scores"].append(ps.accuracy)
        total_practice_questions += q_count
        total_correct_practice += (ps.correct_count or 0)

    for sub in submissions:
        q_obj = db.query(QuestionBank).filter(QuestionBank.id == sub.question_id).first() if sub.question_id else None
        subj = q_obj.subject if (q_obj and q_obj.subject) else "Problem Solving"
        if subj not in subject_map:
            subject_map[subj] = {
                "subject": subj,
                "total_questions": 0,
                "correct_answers": 0,
                "sessions_count": 0,
                "scores": []
            }
        subject_map[subj]["total_questions"] += 1
        is_pass = sub.score >= 70.0
        if is_pass:
            subject_map[subj]["correct_answers"] += 1
        subject_map[subj]["scores"].append(sub.score)
        total_practice_questions += 1
        if is_pass:
            total_correct_practice += 1

    if total_practice_questions > 0:
        practice_accuracy = round((total_correct_practice / total_practice_questions) * 100, 1)
    elif total_submissions > 0:
        practice_accuracy = round(sum(s.score for s in submissions) / total_submissions, 1)
    else:
        practice_accuracy = 78.0

    # Segregate Weak Subjects (< 70%) and Strong Subjects (>= 80%)
    strong_subjects = []
    weak_subjects = []
    developing_subjects = []

    for subj, data in subject_map.items():
        if data["total_questions"] > 0:
            subj_acc = round((data["correct_answers"] / data["total_questions"]) * 100, 1)
        elif data["scores"]:
            subj_acc = round(sum(data["scores"]) / len(data["scores"]), 1)
        else:
            subj_acc = 75.0

        item = {
            "subject": subj,
            "accuracy": subj_acc,
            "questions_attempted": data["total_questions"],
            "correct_answers": data["correct_answers"],
            "sessions_count": data["sessions_count"]
        }

        if subj_acc >= 80.0:
            item["status"] = "Strong"
            item["badge"] = "Proficient / Mastered"
            strong_subjects.append(item)
        elif subj_acc < 70.0:
            item["status"] = "Weak"
            item["badge"] = "Needs Practice"
            item["recommendation"] = f"Review key principles and drill 5 questions on {subj}."
            weak_subjects.append(item)
        else:
            item["status"] = "Developing"
            item["badge"] = "In Progress"
            developing_subjects.append(item)

    # Sort
    strong_subjects.sort(key=lambda x: x["accuracy"], reverse=True)
    weak_subjects.sort(key=lambda x: x["accuracy"])

    # Provide benchmark subjects if no practice recorded yet
    if not strong_subjects and not weak_subjects:
        strong_subjects = [
            {"subject": "Object-Oriented Programming (OOP)", "accuracy": 88.0, "questions_attempted": 0, "status": "Strong", "badge": "Benchmark Strength"},
            {"subject": "SQL & Relational Databases", "accuracy": 82.0, "questions_attempted": 0, "status": "Strong", "badge": "Benchmark Strength"}
        ]
        weak_subjects = [
            {"subject": "System Design & Distributed Scalability", "accuracy": 62.0, "questions_attempted": 0, "status": "Weak", "badge": "Benchmark Focus", "recommendation": "Study microservices decomposition, CAP theorem, and caching patterns."},
            {"subject": "Operating Systems & Concurrency", "accuracy": 66.0, "questions_attempted": 0, "status": "Weak", "badge": "Benchmark Focus", "recommendation": "Review thread synchronization, deadlocks, and virtual memory."}
        ]

    practice_history = [
        {
            "id": ps.id,
            "job_role": ps.job_role,
            "subject": ps.subject,
            "difficulty": ps.difficulty,
            "interview_type": ps.interview_type,
            "total_questions": ps.total_questions,
            "correct_count": ps.correct_count,
            "accuracy": round(ps.accuracy or 0.0, 1),
            "date": ps.created_at.strftime("%b %d, %Y") if ps.created_at else "Recently",
            "is_completed": ps.is_completed
        }
        for ps in practice_sessions
    ]

    # -------------------------------------------------------------
    # 4. Aggregated Skills Needing Improvement (From Resume, Practice, Interviews)
    # -------------------------------------------------------------
    missing_counter: Counter = Counter()
    for a in analyses:
        for sk in (a.missing_skills or []):
            missing_counter[sk.capitalize()] += 2

    for s in submissions:
        for c in (s.missing_concepts or []):
            missing_counter[c] += 1

    user_questions = db.query(InterviewQuestion).join(InterviewSession).filter(
        InterviewSession.user_id == current_user.id
    ).all()
    for q in user_questions:
        if q.feedback and "missing" in q.feedback.lower():
            missing_counter["Architectural Edge Cases"] += 1

    top_missing = missing_counter.most_common(6)
    if not top_missing:
        top_missing = [
            ("Distributed Caching (Redis)", 3),
            ("Database Indexing & MVCC", 2),
            ("System Scalability & Sharding", 2),
            ("STAR Metrics Articulation", 1),
            ("Asynchronous Concurrency", 1)
        ]

    skills_needing_improvement = [
        {
            "skill": skill_name,
            "frequency": freq,
            "priority": "High" if freq >= 3 else "Medium",
            "recommendation": f"Review key principles and practice 2 dedicated questions on {skill_name}."
        }
        for skill_name, freq in top_missing
    ]

    # -------------------------------------------------------------
    # 5. Career Roadmap Progress & Completed Tasks Tracking
    # -------------------------------------------------------------
    roadmaps = db.query(CareerRoadmap).filter(
        CareerRoadmap.user_id == current_user.id
    ).order_by(CareerRoadmap.created_at.desc()).all()

    total_roadmap_tasks = 0
    completed_roadmap_tasks = 0
    total_milestones = 0
    completed_milestones = 0
    active_phase_title = "Phase 1: Advanced Core Competencies"
    active_objectives = [
        "Master asynchronous patterns & memory lifecycle",
        "Deep-dive into REST, caching layers, and database normalization"
    ]
    roadmap_milestones_history = []

    if roadmaps:
        primary_roadmap = roadmaps[0]
        total_milestones = len(primary_roadmap.milestones)
        completed_milestones = sum(1 for m in primary_roadmap.milestones if m.is_completed)

        for m in primary_roadmap.milestones:
            m_total = len(m.checklist or [])
            m_done = sum(1 for c in (m.checklist or []) if isinstance(c, dict) and c.get("is_done"))
            total_roadmap_tasks += m_total
            completed_roadmap_tasks += m_done

            roadmap_milestones_history.append({
                "id": m.id,
                "phase_number": m.phase_number,
                "title": m.title,
                "duration": m.duration,
                "estimated_hours": m.estimated_hours,
                "phase_progress": round(m.phase_progress or 0.0, 1),
                "is_completed": m.is_completed,
                "completed_tasks": m_done,
                "total_tasks": m_total
            })

            if not m.is_completed and active_phase_title == "Phase 1: Advanced Core Competencies":
                active_phase_title = m.title
                active_objectives = m.objectives[:2] if m.objectives else []

        if total_roadmap_tasks == 0:
            total_roadmap_tasks = primary_roadmap.total_tasks or 16
            completed_roadmap_tasks = primary_roadmap.completed_tasks or 4

    roadmap_progress_pct = (
        round((completed_roadmap_tasks / total_roadmap_tasks) * 100, 1)
        if total_roadmap_tasks > 0
        else (primary_roadmap.overall_progress if roadmaps else 25.0)
    )

    # -------------------------------------------------------------
    # 6. Weekly Learning Activity Breakdown (Last 7 Days)
    # -------------------------------------------------------------
    today = datetime.date.today()
    days = [(today - datetime.timedelta(days=i)) for i in range(6, -1, -1)]
    weekly_learning_activity = []

    for d in days:
        day_str = d.strftime("%a")
        date_str = d.strftime("%b %d")

        d_interviews = sum(1 for it in completed_interviews if it.created_at and it.created_at.date() == d)
        d_practice = (
            sum(ps.total_questions or 1 for ps in practice_sessions if ps.created_at and ps.created_at.date() == d) +
            sum(1 for sub in submissions if sub.created_at and sub.created_at.date() == d)
        )
        d_resumes = sum(1 for a in analyses if a.created_at and a.created_at.date() == d)
        d_roadmap = sum(1 for r in roadmaps if r.updated_at and r.updated_at.date() == d)

        total_day_activity = d_interviews + d_practice + d_resumes + d_roadmap

        day_scores = (
            [it.overall_score for it in completed_interviews if it.created_at and it.created_at.date() == d and it.overall_score] +
            [sub.score for sub in submissions if sub.created_at and sub.created_at.date() == d and sub.score]
        )
        day_avg = round(sum(day_scores) / len(day_scores), 1) if day_scores else (78.0 if total_day_activity > 0 else 0.0)

        weekly_learning_activity.append({
            "day": day_str,
            "date": date_str,
            "interviews_count": d_interviews,
            "practice_count": d_practice,
            "resumes_analyzed": d_resumes,
            "roadmap_tasks_completed": d_roadmap,
            "total_activities": total_day_activity,
            "sessions": total_day_activity,
            "score": day_avg
        })

    # -------------------------------------------------------------
    # 7. Recent Chronological Activities Feed
    # -------------------------------------------------------------
    recent_activities = []

    for it in reversed(completed_interviews[-3:]):
        recent_activities.append({
            "type": "interview",
            "title": f"Mock Interview: {it.role_title}",
            "description": f"Verdict: {it.verdict or 'Completed'} • Tech: {round(it.technical_score or 0.0, 1)}% • Comm: {round(it.communication_score or 0.0, 1)}%",
            "score": round(it.overall_score or 0.0, 1),
            "date": it.created_at.strftime("%b %d, %H:%M") if it.created_at else "Recently",
            "link": "/mock-interview"
        })

    for ps in practice_sessions[:2]:
        recent_activities.append({
            "type": "practice",
            "title": f"Practice Session: {ps.subject}",
            "description": f"Accuracy: {round(ps.accuracy or 0.0, 1)}% • {ps.total_questions} Questions ({ps.difficulty})",
            "score": round(ps.accuracy or 0.0, 1),
            "date": ps.created_at.strftime("%b %d, %H:%M") if ps.created_at else "Recently",
            "link": "/practice"
        })

    for sub in submissions[:2]:
        recent_activities.append({
            "type": "practice",
            "title": "Technical Practice Problem",
            "description": f"Score: {round(sub.score, 1)}/100 • Evaluated via AI",
            "score": round(sub.score, 1),
            "date": sub.created_at.strftime("%b %d, %H:%M") if sub.created_at else "Recently",
            "link": "/practice"
        })

    for a in reversed(analyses[-2:]):
        recent_activities.append({
            "type": "resume",
            "title": f"Resume ATS Audit: {a.target_role}",
            "description": f"Overall ATS Score: {round(a.overall_ats_score, 1)}% • Matched {len(a.matched_skills or [])} keywords",
            "score": round(a.overall_ats_score, 1),
            "date": a.created_at.strftime("%b %d, %H:%M") if a.created_at else "Recently",
            "link": "/resume-analyzer"
        })

    recent_activities = recent_activities[:6]

    # -------------------------------------------------------------
    # 8. Skill Mastery Radar Chart Data
    # -------------------------------------------------------------
    radar_data = [
        {"subject": "System Design", "score": min(95.0, max(50.0, avg_tech + 2.0)), "fullMark": 100},
        {"subject": "Data Structures", "score": min(95.0, max(50.0, practice_accuracy + 1.0)), "fullMark": 100},
        {"subject": "Frameworks", "score": min(95.0, max(50.0, avg_tech + 4.0)), "fullMark": 100},
        {"subject": "Communication", "score": min(95.0, max(50.0, avg_comm)), "fullMark": 100},
        {"subject": "Problem Solving", "score": min(95.0, max(50.0, (avg_tech + practice_accuracy) / 2)), "fullMark": 100},
        {"subject": "ATS Optimization", "score": min(95.0, max(50.0, latest_ats_score)), "fullMark": 100}
    ]

    # Composite Career Readiness Score (0-100)
    composite_readiness = round(
        (avg_tech * 0.3) +
        (avg_comm * 0.25) +
        (latest_ats_score * 0.25) +
        (min(100.0, (total_interviews * 5.0) + (total_practice_sessions * 10.0) + 40.0) * 0.2),
        1
    )

    return {
        # High-level KPIs
        "readiness_score": composite_readiness,
        "total_interviews": total_interviews,
        "interview_count": total_interviews,
        "average_interview_score": avg_interview_score,
        "average_technical_score": avg_tech,
        "average_communication_score": avg_comm,

        # ATS Improvement Tracking
        "latest_ats_score": latest_ats_score,
        "ats_improvement": {
            "initial_score": initial_ats_score,
            "latest_score": latest_ats_score,
            "delta": ats_delta,
            "percent_change": ats_pct_change,
            "total_scans": total_scans,
            "history": resume_history
        },
        "resume_improvement": {
            "initial_score": initial_ats_score,
            "latest_score": latest_ats_score,
            "delta": ats_delta,
            "total_scans": total_scans,
            "history": resume_history[:6]
        },

        # Technical Practice Accuracy Tracking
        "technical_practice_accuracy": practice_accuracy,
        "total_practice_sessions": total_practice_sessions,
        "total_practice_questions": total_practice_questions,
        "practice_count": total_practice_sessions + total_submissions,

        # Weak and Strong Subjects
        "weak_subjects": weak_subjects,
        "strong_subjects": strong_subjects,
        "developing_subjects": developing_subjects,

        # Career Roadmap & Task Progress Tracking
        "completed_roadmap_tasks": completed_roadmap_tasks,
        "total_roadmap_tasks": total_roadmap_tasks,
        "roadmap_progress": {
            "total_tasks": total_roadmap_tasks,
            "completed_tasks": completed_roadmap_tasks,
            "total_milestones": total_milestones,
            "completed_milestones": completed_milestones,
            "progress_pct": roadmap_progress_pct,
            "active_phase_title": active_phase_title,
            "active_objectives": active_objectives,
            "milestones": roadmap_milestones_history
        },

        # Weekly Activity Distribution & History Logs
        "weekly_learning_activity": weekly_learning_activity,
        "weekly_performance": weekly_learning_activity,
        "recent_activities": recent_activities,
        "skills_needing_improvement": skills_needing_improvement,
        "interview_trends": interview_trends,
        "interview_history": interview_history,
        "practice_history": practice_history,
        "resume_history": resume_history,
        "radar_data": radar_data
    }
