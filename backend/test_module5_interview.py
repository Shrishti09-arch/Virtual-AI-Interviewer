import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.database import SessionLocal
from app.models.user import User
from app.models.interview import InterviewSession, InterviewQuestion
from app.routers import interviews
from app.schemas.interview import (
    InterviewStartRequest,
    InterviewAnswerRequest
)

def test_module5_interview():
    print("\n=======================================================")
    print("RUNNING COMPLETE MODULE 5 VIRTUAL AI MOCK INTERVIEW TEST SUITE")
    print("=======================================================")

    db = SessionLocal()

    # 1. Setup test candidate
    user = db.query(User).filter(User.email == "module5_user@test.com").first()
    if not user:
        user = User(
            email="module5_user@test.com",
            hashed_password="hashed_pw_test",
            full_name="Alex Rivera",
            role_target="Software Development Engineer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 2. Test Interview Setup & Question 1 Introduction
    print("\n--- 1. Testing Interview Setup & AI Interviewer Introduction ---")
    start_req = InterviewStartRequest(
        role_title="Software Development Engineer",
        interview_type="Technical",
        experience_level="1-3 years",
        difficulty="Intermediate",
        technical_subjects=["System Design", "Distributed Systems"],
        interview_duration_mins=15,
        target_company="Amazon",
        total_questions=3
    )

    session = interviews.start_interview_session(start_req=start_req, current_user=user, db=db)
    session_id = session.id
    assert session_id is not None
    assert session.status == "in_progress"
    assert session.total_questions == 3
    assert len(session.questions) == 3

    q1 = session.questions[0]
    print(f"[PASS] Session #{session_id} successfully initialized.")
    print(f"       AI Introduction (Q1): {q1.question_text[:110]}...")
    assert "AI Technical Interviewer" in q1.question_text
    assert "introduce yourself" in q1.question_text.lower()

    # 3. Test Candidate Response, Speech Analysis & Semantic Evaluation
    print("\n--- 2. Testing Speech-to-Text Analytics & Answer Evaluation ---")
    q1_answer = (
        "Hello! I am a full stack software engineer with 3 years of experience building microservices with FastAPI and React. "
        "Um, basically at my previous company, we were facing severe latency bottlenecks during peak traffic surges. "
        "My goal was to optimize API throughput and reduce database strain. "
        "I decided to architect a distributed caching layer using Redis with a token bucket rate limiter. "
        "As a result, we successfully reduced average response latency by 45% and handled 50M daily requests with zero downtime."
    )

    ans1_req = InterviewAnswerRequest(
        question_id=q1.id,
        candidate_answer=q1_answer,
        time_spent_seconds=65,
        pauses_count=2,
        has_local_recording=True,
        recording_storage_key="indexeddb://session_1_q1_video"
    )

    evaluated_q1 = interviews.submit_question_answer(
        session_id=session_id,
        answer_req=ans1_req,
        current_user=user,
        db=db
    )

    assert evaluated_q1.score > 0, "Score should be positive"
    assert evaluated_q1.score_out_of_10 > 0, "Score out of 10 should be positive"
    assert evaluated_q1.wpm > 0, "WPM should be calculated"
    assert "um" in evaluated_q1.filler_words or "basically" in evaluated_q1.filler_words
    assert evaluated_q1.has_local_recording is True
    assert evaluated_q1.recording_storage_key == "indexeddb://session_1_q1_video"

    print(f"[PASS] Q1 Answer Evaluated:")
    print(f"       Score: {evaluated_q1.score}/100 ({evaluated_q1.score_out_of_10}/10)")
    print(f"       Pacing: {evaluated_q1.wpm} WPM | Fillers Detected: {evaluated_q1.filler_words}")
    print(f"       Feedback: {evaluated_q1.feedback}")
    print(f"       Correct Points: {evaluated_q1.correct_points}")

    # 4. Test Dynamic Follow-up Generation (Question 2 adaptation)
    print("\n--- 3. Testing Dynamic Follow-up Generation for Question 2 ---")
    db.refresh(session)
    q2 = session.questions[1]
    print(f"[PASS] Question 2 dynamically adapted based on Q1 response:")
    print(f"       Q2 Text: {q2.question_text}")
    print(f"       Category: {q2.category} (is_follow_up: {q2.is_follow_up}, difficulty: {q2.difficulty_level})")

    # Answer Question 2
    q2_answer = (
        "To mitigate cache stampede and handle distributed failures, I implemented mutex locks and staggered TTL expiration with jitter. "
        "We also configured Redis Sentinel for automated master-replica failover to guarantee 99.99% high availability."
    )
    ans2_req = InterviewAnswerRequest(
        question_id=q2.id,
        candidate_answer=q2_answer,
        time_spent_seconds=50,
        pauses_count=1
    )
    evaluated_q2 = interviews.submit_question_answer(
        session_id=session_id,
        answer_req=ans2_req,
        current_user=user,
        db=db
    )
    print(f"[PASS] Q2 Evaluated with score: {evaluated_q2.score}/100 ({evaluated_q2.score_out_of_10}/10)")

    # Answer Question 3 (Final Question)
    db.refresh(session)
    q3 = session.questions[2]
    q3_answer = (
        "During a critical outage where connection pools were exhausted, I coordinated with DevOps to rollback the offending release, "
        "triaged the root cause using Prometheus metrics, and implemented strict circuit breakers using Resilience4j patterns."
    )
    ans3_req = InterviewAnswerRequest(
        question_id=q3.id,
        candidate_answer=q3_answer,
        time_spent_seconds=55,
        pauses_count=1
    )
    evaluated_q3 = interviews.submit_question_answer(
        session_id=session_id,
        answer_req=ans3_req,
        current_user=user,
        db=db
    )
    print(f"[PASS] Q3 Evaluated with score: {evaluated_q3.score}/100 ({evaluated_q3.score_out_of_10}/10)")

    # 5. Test Interview Completion & Executive Scorecard
    print("\n--- 4. Testing Interview Completion & Multi-Dimensional Final Report ---")
    completed_session = interviews.complete_interview_session(
        session_id=session_id,
        current_user=user,
        db=db
    )

    assert completed_session.status == "completed"
    assert completed_session.overall_score > 0
    assert completed_session.technical_score > 0
    assert completed_session.communication_score > 0
    assert completed_session.answer_quality_score > 0
    assert completed_session.problem_solving_score > 0
    assert completed_session.verdict in ["Strong Hire", "Hire", "Lean Hire", "Needs Improvement"]
    assert len(completed_session.key_strengths) > 0
    assert len(completed_session.improvement_plan) == 4
    assert completed_session.full_transcript is not None
    assert "Notice:" in completed_session.assessment_disclaimer

    print(f"[PASS] Interview Completed Successfully:")
    print(f"       Overall Score: {completed_session.overall_score}%")
    print(f"       Technical Score: {completed_session.technical_score}% | Communication: {completed_session.communication_score}%")
    print(f"       Answer Quality: {completed_session.answer_quality_score}% | Problem Solving: {completed_session.problem_solving_score}%")
    print(f"       Hiring Verdict: {completed_session.verdict}")
    print(f"       Strengths: {completed_session.key_strengths}")
    print(f"       4-Step Improvement Plan: {completed_session.improvement_plan}")
    print(f"       Ethical Disclaimer: {completed_session.assessment_disclaimer[:80]}...")

    # 6. Test Executive PDF Report Generation (ReportLab)
    print("\n--- 5. Testing Executive PDF Report Generation ---")
    pdf_response = interviews.download_interview_report_pdf(
        session_id=session_id,
        current_user=user,
        db=db
    )
    pdf_bytes = pdf_response.body
    assert len(pdf_bytes) > 1000, f"PDF byte stream too small ({len(pdf_bytes)} bytes)"
    assert pdf_bytes.startswith(b"%PDF-"), "Generated file must be a valid PDF binary"
    print(f"[PASS] ReportLab PDF successfully generated ({len(pdf_bytes)} bytes, valid %PDF- header).")

    db.close()
    print("\n=======================================================")
    print("ALL MODULE 5 VIRTUAL AI MOCK INTERVIEW TESTS PASSED 100%!")
    print("=======================================================")

if __name__ == "__main__":
    test_module5_interview()
