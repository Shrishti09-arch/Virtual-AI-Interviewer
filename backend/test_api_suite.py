from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_full_pipeline():
    print("--- 1. Testing Registration & Login ---", flush=True)
    reg_payload = {
        "email": "test.engineer@antigravity.ai",
        "password": "SecurePassword123!",
        "full_name": "Antigravity Candidate",
        "role_target": "Senior Full Stack Engineer",
        "experience_level": "4-7 years"
    }
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    if reg_res.status_code == 400:
        login_res = client.post("/api/v1/auth/login", json={
            "email": "test.engineer@antigravity.ai",
            "password": "SecurePassword123!"
        })
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        token = login_res.json()["access_token"]
    else:
        assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"
        token = reg_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    print("Login OK!", flush=True)

    print("--- 2. Testing Auth /me ---")
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    user_data = me_res.json()
    assert user_data["email"] == "test.engineer@antigravity.ai"
    print(f"Authenticated as: {user_data['full_name']}")

    print("--- 3. Testing Question Bank ---")
    q_res = client.get("/api/v1/practice/questions", headers=headers)
    assert q_res.status_code == 200
    questions = q_res.json()
    assert len(questions) > 0, "No questions in bank"
    first_q = questions[0]
    print(f"Fetched {len(questions)} questions. Sample: {first_q['title']}")

    print("--- 4. Testing Practice Submission & Evaluation ---")
    sub_res = client.post(
        f"/api/v1/practice/questions/{first_q['id']}/submit",
        headers=headers,
        json={
            "question_id": first_q["id"],
            "user_answer": "In production, we mitigate re-renders by wrapping pure child components in React.memo and stabilizing function callbacks using useCallback. For complex shared state, we favor atomic state management with Zustand or server state with TanStack Query to isolate state mutations."
        }
    )
    assert sub_res.status_code == 200, f"Practice submission failed: {sub_res.text}"
    eval_data = sub_res.json()
    assert "score" in eval_data
    print(f"Practice Score: {eval_data['score']}/100. Feedback: {eval_data['feedback'][:80]}...")

    print("--- 5. Testing Mock Interview Flow ---")
    start_res = client.post(
        "/api/v1/interviews/start",
        headers=headers,
        json={
            "role_title": "Senior Full Stack Engineer",
            "experience_level": "Senior / Lead",
            "interview_type": "Comprehensive",
            "total_questions": 3
        }
    )
    assert start_res.status_code == 200, f"Interview start failed: {start_res.text}"
    session = start_res.json()
    session_id = session["id"]
    assert len(session["questions"]) == 3
    print(f"Interview session started (ID: {session_id}) with {len(session['questions'])} questions.")

    # Answer Question 1
    q1 = session["questions"][0]
    ans_res = client.post(
        f"/api/v1/interviews/{session_id}/answer",
        headers=headers,
        json={
            "question_id": q1["id"],
            "candidate_answer": "When architecting distributed APIs, we implement a layered architecture with FastAPI. We utilize async def for non-blocking I/O, manage database connection pools via SQLAlchemy async engine, use Redis for caching frequent reads, and decouple background processing using Celery.",
            "time_spent_seconds": 65
        }
    )
    assert ans_res.status_code == 200, f"Answer submission failed: {ans_res.text}"
    ans_data = ans_res.json()
    print(f"Q1 Answered. Score: {ans_data['score']}, WPM: {ans_data['wpm']}")

    # Answer Question 2 with STAR format
    q2 = session["questions"][1]
    ans2_res = client.post(
        f"/api/v1/interviews/{session_id}/answer",
        headers=headers,
        json={
            "question_id": q2["id"],
            "candidate_answer": "In my last role, we were facing severe latency spikes during flash sales. My responsibility was to eliminate database contention. I implemented Redis caching with atomic Lua scripts and introduced read replicas. As a result, we reduced p99 latency by 55% and handled 100k peak RPM.",
            "time_spent_seconds": 75
        }
    )
    assert ans2_res.status_code == 200
    print(f"Q2 Answered (STAR). Score: {ans2_res.json()['score']}")

    # Complete Interview
    comp_res = client.post(f"/api/v1/interviews/{session_id}/complete", headers=headers)
    assert comp_res.status_code == 200
    final_session = comp_res.json()
    assert final_session["status"] == "completed"
    print(f"Interview Completed! Verdict: {final_session['verdict']}, Overall Score: {final_session['overall_score']}%")

    print("--- 6. Testing Resume ATS Analysis ---")
    sample_resume = """
    ALEX MORGAN - SENIOR FULL STACK ENGINEER
    Email: alex.morgan@example.com | Phone: 555-0199 | Location: San Francisco, CA
    LinkedIn: linkedin.com/in/alexmorgan | GitHub: github.com/alexmorgan

    PROFESSIONAL SUMMARY
    Innovative Senior Full Stack Engineer with 5+ years of experience building high-scale distributed systems using React, TypeScript, FastAPI, PostgreSQL, and Docker.

    WORK EXPERIENCE
    Senior Software Engineer - Apex Cloud
    • Architected microservices platform handling 50M requests daily, reducing latency by 45%.
    • Spearheaded migration to React 19 and Tailwind CSS, increasing page load speed by 30%.
    • Optimized PostgreSQL indexing and query execution, cutting database CPU utilization by 40%.

    TECHNICAL SKILLS
    Languages: Python, TypeScript, JavaScript, SQL, Go
    Frameworks: React, FastAPI, Next.js, Node.js, Tailwind CSS
    Databases & Cloud: PostgreSQL, Redis, Docker, Kubernetes, AWS, GitHub Actions

    EDUCATION
    B.S. in Computer Science - UC Berkeley
    """
    ats_res = client.post(
        "/api/v1/resumes/analyze-text",
        headers=headers,
        data={
            "target_role": "Senior Full Stack Software Engineer",
            "resume_text": sample_resume,
            "job_description": "We are seeking a Senior Full Stack Engineer proficient in React, FastAPI, Python, PostgreSQL, and Docker."
        }
    )
    assert ats_res.status_code == 200, f"ATS Analysis failed: {ats_res.text}"
    ats_data = ats_res.json()
    print(f"ATS Score: {ats_data['overall_ats_score']}/100. Matched Skills: {len(ats_data['matched_skills'])}")

    print("--- 7. Testing ATS PDF Resume Generation ---")
    pdf_payload = {
        "full_name": "Alex Morgan",
        "email": "alex.morgan@example.com",
        "phone": "+1 (555) 0199",
        "location": "San Francisco, CA",
        "linkedin": "linkedin.com/in/alexmorgan",
        "github": "github.com/alexmorgan",
        "target_role": "Senior Full Stack Software Engineer",
        "professional_summary": "High-impact Senior Engineer specializing in React, FastAPI, and PostgreSQL.",
        "skills": {
            "Languages": ["Python", "TypeScript", "SQL"],
            "Frameworks": ["React", "FastAPI", "Tailwind CSS"],
            "Databases & Cloud": ["PostgreSQL", "Redis", "Docker"]
        },
        "experience": [
            {
                "company": "Apex Cloud",
                "role": "Senior Software Engineer",
                "duration": "2023 - Present",
                "highlights": [
                    "Architected high-throughput API gateway handling 50M requests daily.",
                    "Optimized database connection pooling and query plans, improving response time by 40%."
                ]
            }
        ],
        "projects": [
            {
                "name": "Distributed Rate Limiter",
                "technologies": ["FastAPI", "Redis", "Docker"],
                "description": "Token bucket rate limiter middleware with sub-millisecond execution.",
                "link": "https://github.com/alexmorgan/rate-limiter"
            }
        ],
        "education": [
            {
                "degree": "B.S. in Computer Science",
                "institution": "UC Berkeley",
                "year": "2019 - 2023",
                "grade": "3.85 GPA"
            }
        ]
    }
    pdf_res = client.post("/api/v1/resumes/generate-pdf", headers=headers, json=pdf_payload)
    assert pdf_res.status_code == 200, f"PDF Generation failed: {pdf_res.text}"
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 1000, "Generated PDF is empty"
    print(f"Generated PDF Resume successfully! Size: {len(pdf_res.content)} bytes.")

    print("--- 8. Testing Career Roadmap Generation ---")
    road_res = client.post(
        "/api/v1/roadmaps/generate",
        headers=headers,
        json={
            "target_role": "Senior Full Stack Engineer",
            "current_level": "Mid-Level",
            "timeline_months": 6
        }
    )
    assert road_res.status_code == 200, f"Roadmap generation failed: {road_res.text}"
    roadmap = road_res.json()
    assert len(roadmap["milestones"]) > 0
    print(f"Generated Roadmap with {len(roadmap['milestones'])} milestone phases.")

    print("--- 9. Testing Analytics Dashboard ---")
    dash_res = client.get("/api/v1/analytics/dashboard", headers=headers)
    assert dash_res.status_code == 200, f"Dashboard analytics failed: {dash_res.text}"
    dash_data = dash_res.json()
    print(f"Readiness Score: {dash_data['readiness_score']}%, Total Interviews: {dash_data['interview_count']}")

    print("--- 10. Testing AI Provider Status ---")
    ai_res = client.get("/api/v1/ai-settings/status", headers=headers)
    assert ai_res.status_code == 200
    ai_status = ai_res.json()
    print(f"Active Provider: {ai_status['active_provider']}")

    print("\n==========================================")
    print("ALL 10 SUITE TESTS PASSED WITH 100% SUCCESS!")
    print("==========================================")

if __name__ == "__main__":
    test_full_pipeline()
