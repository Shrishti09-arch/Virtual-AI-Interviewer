import os
import sqlite3

DB_PATHS = ["career_coach.db", "backend/career_coach.db"]

def migrate_database(db_path: str):
    if not os.path.exists(db_path):
        print(f"[-] Database {db_path} does not exist, skipping.")
        return

    print(f"\n[+] Migrating SQLite database at {db_path} to Section 11 specifications...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # 1. Users table: id, name, email, password_hash, created_at
    cur.execute("PRAGMA table_info(users)")
    user_cols = [row[1] for row in cur.fetchall()]
    if "name" not in user_cols:
        print("  -> Adding column 'name' to users")
        cur.execute("ALTER TABLE users ADD COLUMN name TEXT")
        cur.execute("UPDATE users SET name = full_name WHERE name IS NULL AND full_name IS NOT NULL")
    if "password_hash" not in user_cols:
        print("  -> Adding column 'password_hash' to users")
        cur.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
        cur.execute("UPDATE users SET password_hash = hashed_password WHERE password_hash IS NULL AND hashed_password IS NOT NULL")

    # 2. Resumes table: id, user_id, original_filename, extracted_text, ats_score, created_at
    cur.execute("PRAGMA table_info(resumes)")
    resume_cols = [row[1] for row in cur.fetchall()]
    if "original_filename" not in resume_cols:
        print("  -> Adding column 'original_filename' to resumes")
        cur.execute("ALTER TABLE resumes ADD COLUMN original_filename TEXT")
        cur.execute("UPDATE resumes SET original_filename = file_name WHERE original_filename IS NULL AND file_name IS NOT NULL")
    if "extracted_text" not in resume_cols:
        print("  -> Adding column 'extracted_text' to resumes")
        cur.execute("ALTER TABLE resumes ADD COLUMN extracted_text TEXT")
        cur.execute("UPDATE resumes SET extracted_text = raw_text WHERE extracted_text IS NULL AND raw_text IS NOT NULL")
    if "ats_score" not in resume_cols:
        print("  -> Adding column 'ats_score' to resumes")
        cur.execute("ALTER TABLE resumes ADD COLUMN ats_score REAL DEFAULT 0.0")

    # 3. ResumeVersions table: id, resume_id, target_role, generated_content, created_at
    print("  -> Creating table 'resume_versions' if not exists")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS resume_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER NOT NULL REFERENCES resumes(id),
        target_role TEXT NOT NULL,
        generated_content TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 4. InterviewQuestions table: id, role, subject, question, difficulty, source, source_url, created_at
    # Check if old interview_questions had session_id (which was session questions)
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='interview_questions'")
    if cur.fetchone():
        cur.execute("PRAGMA table_info(interview_questions)")
        iq_cols = [row[1] for row in cur.fetchall()]
        if "session_id" in iq_cols and "interview_session_questions" not in [
            r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        ]:
            print("  -> Renaming old session questions table to 'interview_session_questions'")
            cur.execute("ALTER TABLE interview_questions RENAME TO interview_session_questions")

    print("  -> Creating technical question catalog table 'interview_questions'")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS interview_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT DEFAULT 'Full Stack Engineer',
        role_track TEXT DEFAULT 'Full Stack Engineer',
        subject TEXT DEFAULT 'Computer Science Fundamentals',
        question TEXT NOT NULL,
        question_text TEXT,
        difficulty TEXT DEFAULT 'Intermediate',
        source TEXT DEFAULT 'Official Educational Standard',
        source_name TEXT DEFAULT 'Official Educational Standard',
        source_url TEXT,
        category TEXT DEFAULT 'Computer Science',
        programming_language TEXT DEFAULT 'Python',
        question_type TEXT DEFAULT 'Theory',
        title TEXT,
        expected_keywords JSON DEFAULT '[]',
        sample_answer TEXT,
        hints JSON DEFAULT '[]',
        options JSON DEFAULT '[]',
        correct_option_index INTEGER,
        explanation TEXT,
        code_template TEXT,
        test_cases JSON DEFAULT '[]',
        source_type TEXT DEFAULT 'curated_educational',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Populate interview_questions from question_bank if available and empty
    cur.execute("SELECT COUNT(*) FROM interview_questions")
    iq_count = cur.fetchone()[0]
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='question_bank'")
    has_qb = cur.fetchone() is not None

    if iq_count == 0 and has_qb:
        print("  -> Populating 'interview_questions' from 'question_bank'")
        cur.execute("""
        INSERT INTO interview_questions (
            id, role, role_track, subject, question, question_text, difficulty, source, source_name,
            source_url, category, programming_language, question_type, title, expected_keywords,
            sample_answer, hints, options, correct_option_index, explanation, code_template,
            test_cases, source_type, created_at
        )
        SELECT
            id,
            COALESCE(role_track, 'Full Stack Engineer'),
            COALESCE(role_track, 'Full Stack Engineer'),
            subject,
            question_text,
            question_text,
            difficulty,
            COALESCE(source_name, 'Official Educational Standard'),
            COALESCE(source_name, 'Official Educational Standard'),
            source_url,
            category,
            programming_language,
            question_type,
            title,
            expected_keywords,
            sample_answer,
            hints,
            options,
            correct_option_index,
            explanation,
            code_template,
            test_cases,
            source_type,
            created_at
        FROM question_bank;
        """)

    # 5. PracticeSessions table: id, user_id, role, subject, score, created_at
    cur.execute("PRAGMA table_info(practice_sessions)")
    ps_cols = [row[1] for row in cur.fetchall()]
    if "role" not in ps_cols:
        print("  -> Adding column 'role' to practice_sessions")
        cur.execute("ALTER TABLE practice_sessions ADD COLUMN role TEXT")
        cur.execute("UPDATE practice_sessions SET role = job_role WHERE role IS NULL AND job_role IS NOT NULL")
    if "score" not in ps_cols:
        print("  -> Adding column 'score' to practice_sessions")
        cur.execute("ALTER TABLE practice_sessions ADD COLUMN score REAL DEFAULT 0.0")
        cur.execute("UPDATE practice_sessions SET score = accuracy WHERE score IS NULL OR score = 0.0")

    # 6. MockInterviews table: id, user_id, role, interview_type, transcript, overall_score, recording_path, created_at
    print("  -> Creating table 'mock_interviews'")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS mock_interviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id),
        role TEXT NOT NULL,
        interview_type TEXT DEFAULT 'Technical',
        transcript TEXT,
        overall_score REAL DEFAULT 0.0,
        recording_path TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Populate mock_interviews from interview_sessions if empty
    cur.execute("SELECT COUNT(*) FROM mock_interviews")
    if cur.fetchone()[0] == 0:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='interview_sessions'")
        if cur.fetchone():
            print("  -> Populating 'mock_interviews' from 'interview_sessions'")
            cur.execute("""
            INSERT OR IGNORE INTO mock_interviews (id, user_id, role, interview_type, transcript, overall_score, recording_path, created_at)
            SELECT id, user_id, role_title, interview_type, full_transcript, overall_score, NULL, created_at
            FROM interview_sessions;
            """)

    # 7. InterviewAnswers table: id, interview_id, question, answer, technical_score, communication_feedback
    print("  -> Creating table 'interview_answers'")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS interview_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        interview_id INTEGER NOT NULL REFERENCES mock_interviews(id),
        question TEXT NOT NULL,
        answer TEXT,
        technical_score REAL DEFAULT 0.0,
        communication_feedback TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Populate interview_answers from interview_session_questions if empty
    cur.execute("SELECT COUNT(*) FROM interview_answers")
    if cur.fetchone()[0] == 0:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='interview_session_questions'")
        if cur.fetchone():
            print("  -> Populating 'interview_answers' from 'interview_session_questions'")
            cur.execute("""
            INSERT OR IGNORE INTO interview_answers (id, interview_id, question, answer, technical_score, communication_feedback, created_at)
            SELECT id, session_id, question_text, candidate_answer, technical_accuracy, feedback, created_at
            FROM interview_session_questions;
            """)

    # 8. Roadmaps table: id, user_id, target_role, roadmap_content, progress, created_at
    print("  -> Creating table 'roadmaps'")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS roadmaps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id),
        target_role TEXT NOT NULL,
        roadmap_content TEXT NOT NULL,
        progress REAL DEFAULT 0.0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Populate roadmaps from career_roadmaps if empty
    cur.execute("SELECT COUNT(*) FROM roadmaps")
    if cur.fetchone()[0] == 0:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='career_roadmaps'")
        if cur.fetchone():
            print("  -> Populating 'roadmaps' from 'career_roadmaps'")
            cur.execute("""
            INSERT OR IGNORE INTO roadmaps (id, user_id, target_role, roadmap_content, progress, created_at)
            SELECT id, user_id, target_role, COALESCE(overview, 'Dynamic Career Roadmap'), overall_progress, created_at
            FROM career_roadmaps;
            """)

    conn.commit()
    conn.close()
    print(f"[+] Migration for {db_path} completed successfully!")

if __name__ == "__main__":
    for p in DB_PATHS:
        migrate_database(p)
