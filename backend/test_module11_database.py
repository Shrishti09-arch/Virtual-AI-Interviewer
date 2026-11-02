import sys
import os
import datetime

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.database import SessionLocal, engine
from app.models import (
    User,
    Resume,
    ResumeVersion,
    InterviewQuestion,
    PracticeSession,
    MockInterview,
    InterviewAnswer,
    Roadmap,
)
from app.services.auth_service import get_password_hash, verify_password

def test_module11_database():
    print("\n=======================================================")
    print("RUNNING COMPLETE SECTION 11 DATABASE & DATA ISOLATION TEST")
    print("=======================================================")

    db = SessionLocal()

    # -------------------------------------------------------------
    # 1. Test SQLite Schema & Table Existence for All 8 Tables
    # -------------------------------------------------------------
    print("\n--- 1. Verifying 8 Tables and Required Columns in SQLite ---")
    required_tables = {
        "users": ["id", "name", "email", "password_hash", "created_at"],
        "resumes": ["id", "user_id", "original_filename", "extracted_text", "ats_score", "created_at"],
        "resume_versions": ["id", "resume_id", "target_role", "generated_content", "created_at"],
        "interview_questions": ["id", "role", "subject", "question", "difficulty", "source", "source_url", "created_at"],
        "practice_sessions": ["id", "user_id", "role", "subject", "score", "created_at"],
        "mock_interviews": ["id", "user_id", "role", "interview_type", "transcript", "overall_score", "recording_path", "created_at"],
        "interview_answers": ["id", "interview_id", "question", "answer", "technical_score", "communication_feedback"],
        "roadmaps": ["id", "user_id", "target_role", "roadmap_content", "progress", "created_at"]
    }

    import sqlite3
    db_file = "career_coach.db"
    con = sqlite3.connect(db_file)
    cur = con.cursor()

    for table, expected_cols in required_tables.items():
        cur.execute(f"PRAGMA table_info({table})")
        actual_cols = [r[1] for r in cur.fetchall()]
        assert len(actual_cols) > 0, f"Table '{table}' does not exist in SQLite!"
        for col in expected_cols:
            assert col in actual_cols, f"Column '{col}' missing from table '{table}'! Actual: {actual_cols}"
        print(f"[PASS] Table '{table}': {expected_cols} verified in SQLite.")
    con.close()

    # -------------------------------------------------------------
    # 2. Test Password Hashing (Never Store Plaintext Passwords)
    # -------------------------------------------------------------
    print("\n--- 2. Verifying Secure Password Hashing & Anti-Plaintext Guard ---")
    plain_pw = "SuperSecurePassword#2026!"
    hashed_pw = get_password_hash(plain_pw)

    assert hashed_pw != plain_pw, "Password was not hashed!"
    assert not hashed_pw.startswith(plain_pw), "Password hash contains plaintext prefix!"
    assert verify_password(plain_pw, hashed_pw) is True, "Password verification failed for correct password!"
    assert verify_password("WrongPassword123", hashed_pw) is False, "Password verification succeeded for wrong password!"

    # Create User A with hashed password
    user_a = db.query(User).filter(User.email == "user_a_sec11@careercoach.io").first()
    if user_a:
        db.delete(user_a)
        db.commit()

    user_a = User(
        name="Candidate Alpha",
        email="user_a_sec11@careercoach.io",
        password_hash=hashed_pw
    )
    db.add(user_a)
    db.commit()
    db.refresh(user_a)

    assert user_a.id is not None
    assert user_a.name == "Candidate Alpha"
    assert user_a.full_name == "Candidate Alpha", "Bidirectional sync name <-> full_name failed"
    assert user_a.password_hash == hashed_pw
    assert user_a.hashed_password == hashed_pw, "Bidirectional sync password_hash <-> hashed_password failed"
    assert plain_pw not in user_a.password_hash
    print(f"[PASS] User A created with hashed password: {user_a.password_hash[:25]}... (No plaintext)")

    # Create User B for Data Isolation Testing
    user_b = db.query(User).filter(User.email == "user_b_sec11@careercoach.io").first()
    if user_b:
        db.delete(user_b)
        db.commit()

    user_b = User(
        name="Candidate Beta",
        email="user_b_sec11@careercoach.io",
        password_hash=get_password_hash("BetaPassword#2026!")
    )
    db.add(user_b)
    db.commit()
    db.refresh(user_b)
    print(f"[PASS] User B created (ID: {user_b.id})")

    # -------------------------------------------------------------
    # 3. Test SQLAlchemy Insertion for all 8 Models
    # -------------------------------------------------------------
    print("\n--- 3. Testing SQLAlchemy ORM Operations on Section 11 Tables ---")

    # Table 2: Resumes
    res_a = Resume(
        user_id=user_a.id,
        original_filename="candidate_alpha_cv.pdf",
        extracted_text="Experienced Full Stack Software Engineer specializing in Python, FastAPI, React.",
        ats_score=85.5
    )
    db.add(res_a)
    db.commit()
    db.refresh(res_a)
    assert res_a.id is not None
    assert res_a.original_filename == "candidate_alpha_cv.pdf"
    assert res_a.file_name == "candidate_alpha_cv.pdf", "Bidirectional sync original_filename <-> file_name failed"
    assert res_a.extracted_text.startswith("Experienced Full Stack")
    assert res_a.raw_text == res_a.extracted_text, "Bidirectional sync extracted_text <-> raw_text failed"
    assert res_a.ats_score == 85.5
    print(f"[PASS] Resumes: Inserted Resume #{res_a.id} for user_id={res_a.user_id}")

    # Table 3: ResumeVersions
    ver_a = ResumeVersion(
        resume_id=res_a.id,
        target_role="AI/ML Engineer",
        generated_content="Role-optimized ATS CV: Specializing in PyTorch, Ollama, Transformers, and FastAPI microservices."
    )
    db.add(ver_a)
    db.commit()
    db.refresh(ver_a)
    assert ver_a.id is not None
    assert ver_a.resume_id == res_a.id
    assert ver_a.target_role == "AI/ML Engineer"
    assert "PyTorch" in ver_a.generated_content
    print(f"[PASS] ResumeVersions: Inserted Version #{ver_a.id} linked to resume_id={ver_a.resume_id}")

    # Table 4: InterviewQuestions (Technical Question Bank)
    q_item = InterviewQuestion(
        role="Full Stack Developer",
        subject="System Design",
        question="Explain how Redis caching prevents cache stampede using mutex locking.",
        difficulty="Advanced",
        source="Distributed Systems Standards",
        source_url="https://redis.io/docs/manual/patterns/"
    )
    db.add(q_item)
    db.commit()
    db.refresh(q_item)
    assert q_item.id is not None
    assert q_item.role == "Full Stack Developer"
    assert q_item.role_track == "Full Stack Developer", "Bidirectional sync role <-> role_track failed"
    assert q_item.question.startswith("Explain how Redis")
    assert q_item.question_text == q_item.question, "Bidirectional sync question <-> question_text failed"
    assert q_item.source == "Distributed Systems Standards"
    assert q_item.source_name == q_item.source, "Bidirectional sync source <-> source_name failed"
    print(f"[PASS] InterviewQuestions: Inserted Catalog Question #{q_item.id} ({q_item.subject})")

    # Table 5: PracticeSessions
    prac_a = PracticeSession(
        user_id=user_a.id,
        role="Backend Developer",
        subject="System Design",
        score=90.0
    )
    db.add(prac_a)
    db.commit()
    db.refresh(prac_a)
    assert prac_a.id is not None
    assert prac_a.role == "Backend Developer"
    assert prac_a.job_role == "Backend Developer", "Bidirectional sync role <-> job_role failed"
    assert prac_a.score == 90.0
    assert prac_a.accuracy == 90.0, "Bidirectional sync score <-> accuracy failed"
    print(f"[PASS] PracticeSessions: Inserted PracticeSession #{prac_a.id} for user_id={prac_a.user_id}")

    # Table 6: MockInterviews
    mock_a = MockInterview(
        user_id=user_a.id,
        role="Senior Python Engineer",
        interview_type="Technical",
        transcript="AI: Welcome! Walk me through Python GIL and multiprocessing. Candidate: The GIL...",
        overall_score=88.5,
        recording_path="/recordings/user_a_session_101.webm"
    )
    db.add(mock_a)
    db.commit()
    db.refresh(mock_a)
    assert mock_a.id is not None
    assert mock_a.user_id == user_a.id
    assert mock_a.role == "Senior Python Engineer"
    assert mock_a.overall_score == 88.5
    print(f"[PASS] MockInterviews: Inserted MockInterview #{mock_a.id} for user_id={mock_a.user_id}")

    # Table 7: InterviewAnswers
    ans_a = InterviewAnswer(
        interview_id=mock_a.id,
        question="How does Python GIL affect CPU-bound multi-threaded programs?",
        answer="In CPython, the GIL allows only one thread to execute Python bytecode at a time, preventing true CPU parallelism across threads.",
        technical_score=95.0,
        communication_feedback="Crisp articulation of CPython internals and CPU vs I/O bound threading differences."
    )
    db.add(ans_a)
    db.commit()
    db.refresh(ans_a)
    assert ans_a.id is not None
    assert ans_a.interview_id == mock_a.id
    assert ans_a.technical_score == 95.0
    assert "CPython" in ans_a.answer
    print(f"[PASS] InterviewAnswers: Inserted Answer #{ans_a.id} linked to interview_id={ans_a.interview_id}")

    # Table 8: Roadmaps
    road_a = Roadmap(
        user_id=user_a.id,
        target_role="Full Stack Developer",
        roadmap_content='{"phases": [{"title": "Phase 1: React & FastApi", "weeks": "1-4"}], "milestones_count": 4}',
        progress=45.0
    )
    db.add(road_a)
    db.commit()
    db.refresh(road_a)
    assert road_a.id is not None
    assert road_a.user_id == user_a.id
    assert road_a.target_role == "Full Stack Developer"
    assert road_a.progress == 45.0
    print(f"[PASS] Roadmaps: Inserted Roadmap #{road_a.id} for user_id={road_a.user_id}")

    # -------------------------------------------------------------
    # 4. Test Strict User-Level Data Isolation
    # -------------------------------------------------------------
    print("\n--- 4. Verifying Strict User-Level Data Isolation ---")

    # User B queries their own resumes: must be 0
    b_resumes = db.query(Resume).filter(Resume.user_id == user_b.id).all()
    assert len(b_resumes) == 0, f"Data leak! User B retrieved User A's resumes: {b_resumes}"
    print(f"[PASS] User B query for Resumes returned 0 records (isolated from User A).")

    # User B queries for User A's resume by ID scoped to User B
    b_cross_resume = db.query(Resume).filter(
        Resume.id == res_a.id,
        Resume.user_id == user_b.id
    ).first()
    assert b_cross_resume is None, "Data leak! User B retrieved User A's specific resume!"
    print(f"[PASS] User B cannot access User A's resume #{res_a.id}.")

    # User B queries their own mock interviews: must be 0
    b_interviews = db.query(MockInterview).filter(MockInterview.user_id == user_b.id).all()
    assert len(b_interviews) == 0, f"Data leak! User B retrieved User A's mock interviews: {b_interviews}"
    print(f"[PASS] User B query for MockInterviews returned 0 records (isolated from User A).")

    # User B queries for User A's mock interview by ID scoped to User B
    b_cross_interview = db.query(MockInterview).filter(
        MockInterview.id == mock_a.id,
        MockInterview.user_id == user_b.id
    ).first()
    assert b_cross_interview is None, "Data leak! User B accessed User A's mock interview!"
    print(f"[PASS] User B cannot access User A's mock interview #{mock_a.id}.")

    # User B queries their own practice sessions: must be 0
    b_practice = db.query(PracticeSession).filter(PracticeSession.user_id == user_b.id).all()
    assert len(b_practice) == 0, f"Data leak! User B retrieved User A's practice sessions: {b_practice}"
    print(f"[PASS] User B query for PracticeSessions returned 0 records (isolated from User A).")

    # User B queries their own roadmaps: must be 0
    b_roadmaps = db.query(Roadmap).filter(Roadmap.user_id == user_b.id).all()
    assert len(b_roadmaps) == 0, f"Data leak! User B retrieved User A's roadmaps: {b_roadmaps}"
    print(f"[PASS] User B query for Roadmaps returned 0 records (isolated from User A).")

    # User B queries for User A's roadmap by ID scoped to User B
    b_cross_roadmap = db.query(Roadmap).filter(
        Roadmap.id == road_a.id,
        Roadmap.user_id == user_b.id
    ).first()
    assert b_cross_roadmap is None, "Data leak! User B accessed User A's roadmap!"
    print(f"[PASS] User B cannot access User A's roadmap #{road_a.id}.")

    # Clean up test users
    db.delete(ans_a)
    db.delete(mock_a)
    db.delete(prac_a)
    db.delete(q_item)
    db.delete(ver_a)
    db.delete(res_a)
    db.delete(road_a)
    db.delete(user_a)
    db.delete(user_b)
    db.commit()

    print("\n=======================================================")
    print("ALL SECTION 11 DATABASE TESTS PASSED SUCCESSFULLY (100%)!")
    print("=======================================================\n")

if __name__ == "__main__":
    test_module11_database()
