from app.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.practice import QuestionBank
from app.services.seed_service import seed_question_bank
from app.services.auth_service import get_password_hash, verify_password, create_access_token
from app.services.resume_service import resume_service
from app.services.interview_service import interview_service
from app.services.roadmap_service import roadmap_service
from app.routers import auth, resumes, interviews, practice, roadmaps, analytics, ai_settings
from app.schemas.user import UserRegister, UserLogin
from app.schemas.interview import InterviewStartRequest, InterviewAnswerRequest
from app.schemas.resume import ResumeGenerateRequest
from app.schemas.practice import PracticeSubmitRequest
from app.schemas.roadmap import RoadmapGenerateRequest, MilestoneToggleRequest

def run_all_tests():
    db = SessionLocal()
    try:
        print("=== 1. Testing Database & Seed Service ===", flush=True)
        Base.metadata.create_all(bind=engine)
        seed_question_bank(db)
        q_count = db.query(QuestionBank).count()
        assert q_count >= 10, f"Expected at least 10 questions, got {q_count}"
        print(f"[PASS] Question bank seeded successfully with {q_count} questions.", flush=True)

        print("\n=== 2. Testing User Registration & Authentication ===", flush=True)
        test_email = "direct.test@careercoach.ai"
        user = db.query(User).filter(User.email == test_email).first()
        if not user:
            reg_in = UserRegister(
                email=test_email,
                password="SecurePassword2026!",
                full_name="Alex Direct Candidate",
                role_target="Senior Full Stack Software Engineer",
                experience_level="4-7 years"
            )
            token_obj = auth.register(reg_in, db=db)
            assert token_obj.access_token is not None
            user = db.query(User).filter(User.email == test_email).first()
        assert user is not None
        assert verify_password("SecurePassword2026!", user.hashed_password)
        print(f"[PASS] User registered & verified successfully: ID {user.id}, {user.email}", flush=True)

        print("\n=== 3. Testing Practice Questions & AI Grading ===", flush=True)
        questions = practice.get_questions(category="All", difficulty="All", search=None, db=db)
        assert len(questions) > 0
        first_q = questions[0]
        print(f"[PASS] Retrieved questions. Testing question '{first_q.title}'", flush=True)

        sub_in = PracticeSubmitRequest(
            question_id=first_q.id,
            user_answer="We wrap pure child components in React.memo and memoize callback handlers using useCallback to maintain referential integrity. For shared global state, we leverage Zustand with selector functions to minimize component subscribers."
        )
        eval_result = practice.submit_practice_answer(first_q.id, sub_in, current_user=user, db=db)
        assert eval_result.score > 0
        assert len(eval_result.feedback) > 0
        print(f"[PASS] Practice solution evaluated: Score {eval_result.score}/100.", flush=True)

        print("\n=== 4. Testing Mock Interview Engine (Video/Audio/STAR) ===", flush=True)
        start_req = InterviewStartRequest(
            role_title="Senior Full Stack Software Engineer",
            experience_level="Senior / Lead",
            interview_type="Comprehensive",
            total_questions=3
        )
        session = interviews.start_interview_session(start_req, current_user=user, db=db)
        assert session.id is not None
        assert len(session.questions) == 3
        print(f"[PASS] Mock interview session #{session.id} generated with {len(session.questions)} questions.", flush=True)

        # Answer question 1
        q1 = session.questions[0]
        ans1_req = InterviewAnswerRequest(
            question_id=q1.id,
            candidate_answer="In our distributed architecture, we structure FastAPI with async endpoints for I/O operations, maintain persistent database connection pooling with SQLAlchemy, utilize Redis caching for hot paths, and emit asynchronous event tasks via Celery.",
            time_spent_seconds=60
        )
        ans1_res = interviews.submit_question_answer(session.id, ans1_req, current_user=user, db=db)
        assert ans1_res.score > 0
        print(f"[PASS] Q1 evaluated: Score {ans1_res.score}/100, WPM: {ans1_res.wpm}", flush=True)

        # Answer question 2 with STAR markers
        q2 = session.questions[1]
        ans2_req = InterviewAnswerRequest(
            question_id=q2.id,
            candidate_answer="In my previous role, our team faced a severe database connection exhaustion outage during high traffic. My goal was to eliminate connection leaks and restore service. I implemented connection pooling with circuit breakers and read replicas. As a result, we reduced p99 query latency by 45% and restored 99.99% uptime.",
            time_spent_seconds=70
        )
        ans2_res = interviews.submit_question_answer(session.id, ans2_req, current_user=user, db=db)
        assert ans2_res.score > 0
        print(f"[PASS] Q2 (STAR) evaluated: Score {ans2_res.score}/100. Star situation: {ans2_res.star_analysis.get('situation', {}).get('detected')}", flush=True)

        # Complete session
        comp_session = interviews.complete_interview_session(session.id, current_user=user, db=db)
        assert comp_session.status == "completed"
        assert comp_session.verdict in ["Strong Hire", "Hire", "Lean Hire", "Needs Improvement"]
        print(f"[PASS] Interview completed! Verdict: '{comp_session.verdict}', Overall Score: {comp_session.overall_score}%", flush=True)

        print("\n=== 5. Testing Resume ATS Parsing & Keyword Analysis ===", flush=True)
        sample_resume = """
        ALEX MORGAN - SENIOR FULL STACK ENGINEER
        Email: alex.morgan@example.com | Phone: 555-0199 | Location: San Francisco, CA
        LinkedIn: linkedin.com/in/alexmorgan | GitHub: github.com/alexmorgan

        PROFESSIONAL SUMMARY
        Innovative Full Stack Software Engineer with 5+ years building distributed applications using React, TypeScript, FastAPI, PostgreSQL, and Docker.

        PROFESSIONAL EXPERIENCE
        Senior Software Engineer - Apex Cloud (2022 - Present)
        • Architected microservices platform handling 50M requests daily, reducing latency by 45%.
        • Spearheaded migration to React 19 and Tailwind CSS, increasing page load speed by 30%.
        • Optimized PostgreSQL indexing and query execution, cutting database CPU utilization by 40%.

        TECHNICAL SKILLS
        Languages: Python, TypeScript, JavaScript, SQL, Go
        Frameworks: React, FastAPI, Next.js, Node.js, Tailwind CSS
        Databases & Cloud: PostgreSQL, Redis, Docker, Kubernetes, AWS, GitHub Actions

        EDUCATION
        B.S. in Computer Science - UC Berkeley (2018 - 2022)
        """
        ats_analysis = resumes.analyze_resume_text(
            target_role="Full Stack Software Engineer",
            resume_text=sample_resume,
            job_description="Seeking a Full Stack Engineer experienced with React, FastAPI, PostgreSQL, and Docker.",
            current_user=user,
            db=db
        )
        assert ats_analysis.overall_ats_score > 0
        assert len(ats_analysis.matched_skills) > 0
        print(f"[PASS] ATS Audit: Score {ats_analysis.overall_ats_score}/100. Matched {len(ats_analysis.matched_skills)} skills.", flush=True)

        print("\n=== 6. Testing ATS-Friendly PDF Resume Generation (ReportLab) ===", flush=True)
        pdf_gen_req = ResumeGenerateRequest(
            full_name="Alex Morgan",
            email="alex.morgan@example.com",
            phone="+1 (555) 0199",
            location="San Francisco, CA",
            linkedin="linkedin.com/in/alexmorgan",
            github="github.com/alexmorgan",
            target_role="Full Stack Software Engineer",
            professional_summary="Performance-oriented Software Engineer with 5+ years of experience in distributed systems.",
            skills={
                "Languages": ["Python", "TypeScript", "JavaScript", "SQL"],
                "Frameworks": ["React", "FastAPI", "Next.js", "Tailwind CSS"],
                "Databases & Cloud": ["PostgreSQL", "Redis", "Docker", "AWS"]
            },
            experience=[
                {
                    "company": "Apex Cloud",
                    "role": "Senior Engineer",
                    "duration": "2023 - Present",
                    "highlights": [
                        "Architected real-time WebSocket platform serving 100k concurrent users.",
                        "Decreased p99 response times by 40% through Redis caching and query indexing."
                    ]
                }
            ],
            education=[
                {
                    "institution": "UC Berkeley",
                    "degree": "B.S. in Computer Science",
                    "year": "2018 - 2022",
                    "grade": "3.85 GPA"
                }
            ],
            projects=[
                {
                    "name": "High-Throughput Rate Limiter",
                    "technologies": ["FastAPI", "Redis", "Docker"],
                    "description": "Token bucket rate limiter middleware with sub-millisecond overhead.",
                    "link": "https://github.com/alexmorgan/rate-limiter"
                }
            ]
        )
        pdf_response = resumes.generate_ats_pdf(pdf_gen_req, current_user=user)
        assert pdf_response.media_type == "application/pdf"
        assert len(pdf_response.body) > 2000, "PDF content too small"
        print(f"[PASS] ReportLab generated valid ATS PDF resume: {len(pdf_response.body)} bytes.", flush=True)

        print("\n=== 7. Testing Personalized Career Roadmap & Milestones ===", flush=True)
        road_req = RoadmapGenerateRequest(
            target_role="Senior Full Stack Software Engineer",
            current_level="1-3 years",
            timeline_months=6
        )
        roadmap = roadmaps.generate_roadmap(road_req, current_user=user, db=db)
        assert roadmap.id is not None
        assert len(roadmap.milestones) == 4
        print(f"[PASS] Career Roadmap generated: 4 distinct phased milestones.", flush=True)

        # Toggle first milestone
        m1 = roadmap.milestones[0]
        toggle_res = roadmaps.toggle_milestone(m1.id, MilestoneToggleRequest(is_completed=True), current_user=user, db=db)
        assert toggle_res["is_completed"] is True
        print(f"[PASS] Milestone toggled successfully.", flush=True)

        print("\n=== 8. Testing Analytics Dashboard Aggregations ===", flush=True)
        dash_data = analytics.get_user_dashboard_analytics(current_user=user, db=db)
        assert dash_data["readiness_score"] > 0
        assert dash_data["interview_count"] >= 1
        assert len(dash_data["radar_data"]) == 6
        print(f"[PASS] Analytics computed: Career Readiness {dash_data['readiness_score']}%, Radar Dimensions: {len(dash_data['radar_data'])}", flush=True)

        print("\n=== 9. Testing AI Provider Settings & Status ===", flush=True)
        provider_data = ai_settings.get_all_provider_statuses(current_user=user)
        assert "providers" in provider_data
        print(f"[PASS] AI Settings fetched: Active provider: {provider_data['active_provider']}", flush=True)

        print("\n=======================================================", flush=True)
        print("ALL 9 BACKEND PIPELINE & SERVICE INTEGRATION TESTS PASSED!", flush=True)
        print("=======================================================", flush=True)

    finally:
        db.close()

if __name__ == "__main__":
    run_all_tests()
