import os
import sqlite3

db_paths = ["career_coach.db", "backend/career_coach.db"]

columns = [
    ("interview_questions", "is_fallback", "BOOLEAN DEFAULT 0"),
    ("interview_questions", "provider_used", "VARCHAR(50) DEFAULT 'fallback_engine'"),
    ("interview_questions", "model_used", "VARCHAR(100) DEFAULT 'rule-based-heuristics-v1'"),
    ("practice_submissions", "is_fallback", "BOOLEAN DEFAULT 0"),
    ("practice_submissions", "provider_used", "VARCHAR(50) DEFAULT 'fallback_engine'"),
    ("practice_submissions", "model_used", "VARCHAR(100) DEFAULT 'rule-based-heuristics-v1'"),
    ("resume_analyses", "section_scores", "JSON DEFAULT '{}'"),
    ("resume_analyses", "grammar_errors", "JSON DEFAULT '[]'"),
    ("resume_analyses", "weak_sentences", "JSON DEFAULT '[]'"),
    ("resume_analyses", "corrections", "JSON DEFAULT '[]'"),
    ("resume_analyses", "readability_metrics", "JSON DEFAULT '{}'"),
    ("resume_analyses", "disclaimer", "TEXT"),
    # Module 4: Question Bank columns
    ("question_bank", "subject", "VARCHAR(100) DEFAULT 'Computer Science Fundamentals'"),
    ("question_bank", "programming_language", "VARCHAR(50) DEFAULT 'Python'"),
    ("question_bank", "question_type", "VARCHAR(50) DEFAULT 'Theory'"),
    ("question_bank", "options", "JSON DEFAULT '[]'"),
    ("question_bank", "correct_option_index", "INTEGER DEFAULT NULL"),
    ("question_bank", "explanation", "TEXT DEFAULT ''"),
    ("question_bank", "code_template", "TEXT DEFAULT ''"),
    ("question_bank", "test_cases", "JSON DEFAULT '[]'"),
    ("question_bank", "source_type", "VARCHAR(50) DEFAULT 'curated_educational'"),
    ("question_bank", "source_name", "VARCHAR(100) DEFAULT 'Official Educational Documentation'"),
    ("question_bank", "source_url", "VARCHAR(255) DEFAULT ''"),
    # Module 5: Virtual AI Mock Interview columns
    ("interview_sessions", "difficulty", "VARCHAR(50) DEFAULT 'Intermediate'"),
    ("interview_sessions", "technical_subjects", "JSON DEFAULT '[]'"),
    ("interview_sessions", "interview_duration_mins", "INTEGER DEFAULT 15"),
    ("interview_sessions", "target_company", "VARCHAR(100) DEFAULT NULL"),
    ("interview_sessions", "current_question_index", "INTEGER DEFAULT 0"),
    ("interview_sessions", "answer_quality_score", "FLOAT DEFAULT 0.0"),
    ("interview_sessions", "problem_solving_score", "FLOAT DEFAULT 0.0"),
    ("interview_sessions", "recommended_topics", "JSON DEFAULT '[]'"),
    ("interview_sessions", "improvement_plan", "JSON DEFAULT '[]'"),
    ("interview_sessions", "full_transcript", "TEXT DEFAULT NULL"),
    ("interview_sessions", "assessment_disclaimer", "TEXT DEFAULT 'Notice: Audio, video, and speech analyses are heuristic indicators designed for career coaching. Antigravity AI does not claim to detect personality, honesty, or cognitive suitability from facial appearance.'"),
    ("interview_questions", "is_follow_up", "BOOLEAN DEFAULT 0"),
    ("interview_questions", "difficulty_level", "VARCHAR(50) DEFAULT 'Intermediate'"),
    ("interview_questions", "has_local_recording", "BOOLEAN DEFAULT 0"),
    ("interview_questions", "recording_storage_key", "VARCHAR(255) DEFAULT NULL"),
    ("interview_questions", "score_out_of_10", "FLOAT DEFAULT 0.0"),
    ("interview_questions", "problem_solving_rating", "FLOAT DEFAULT 0.0"),
    ("interview_questions", "correct_points", "JSON DEFAULT '[]'"),
    ("interview_questions", "incorrect_points", "JSON DEFAULT '[]'"),
    ("interview_questions", "missing_concepts", "JSON DEFAULT '[]'"),
    ("interview_questions", "ideal_answer", "TEXT DEFAULT NULL"),
    ("interview_questions", "improvement_suggestions", "TEXT DEFAULT NULL"),
    ("interview_questions", "repeated_words", "JSON DEFAULT '[]'"),
    ("interview_questions", "pauses_count", "INTEGER DEFAULT 0"),
    ("interview_questions", "vocabulary_score", "FLOAT DEFAULT 0.0"),
    # Module 6: Career Roadmap columns
    ("career_roadmaps", "education", "VARCHAR(100) DEFAULT 'Computer Science Degree'"),
    ("career_roadmaps", "existing_skills", "JSON DEFAULT '[]'"),
    ("career_roadmaps", "daily_study_hours", "FLOAT DEFAULT 2.0"),
    ("career_roadmaps", "career_goal", "VARCHAR(255) DEFAULT 'Land First Professional Software Role'"),
    ("career_roadmaps", "daily_study_plan", "JSON DEFAULT '{}'"),
    ("career_roadmaps", "weekly_targets", "JSON DEFAULT '[]'"),
    ("career_roadmaps", "overall_progress", "FLOAT DEFAULT 0.0"),
    ("career_roadmaps", "total_tasks", "INTEGER DEFAULT 0"),
    ("career_roadmaps", "completed_tasks", "INTEGER DEFAULT 0"),
    ("career_roadmaps", "updated_at", "DATETIME"),
    ("roadmap_milestones", "estimated_hours", "INTEGER DEFAULT 50"),
    ("roadmap_milestones", "topics", "JSON DEFAULT '[]'"),
    ("roadmap_milestones", "practice_tasks", "JSON DEFAULT '[]'"),
    ("roadmap_milestones", "interview_questions", "JSON DEFAULT '[]'"),
    ("roadmap_milestones", "checklist", "JSON DEFAULT '[]'"),
    ("roadmap_milestones", "phase_progress", "FLOAT DEFAULT 0.0"),
]

for db_path in db_paths:
    if not os.path.exists(db_path):
        continue
    print(f"Migrating {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for table, col_name, col_def in columns:
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}")
            print(f"[{db_path}] Added column {col_name} to {table}")
        except sqlite3.OperationalError:
            pass

    # Create practice_sessions table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS practice_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        job_role VARCHAR(100) NOT NULL,
        subject VARCHAR(100) NOT NULL,
        programming_language VARCHAR(50) DEFAULT 'Python',
        difficulty VARCHAR(50) DEFAULT 'Intermediate',
        interview_type VARCHAR(50) DEFAULT 'Comprehensive Mixed',
        total_questions INTEGER DEFAULT 5,
        current_index INTEGER DEFAULT 0,
        is_completed BOOLEAN DEFAULT 0,
        question_ids JSON DEFAULT '[]',
        answers JSON DEFAULT '[]',
        correct_count INTEGER DEFAULT 0,
        incorrect_count INTEGER DEFAULT 0,
        accuracy FLOAT DEFAULT 0.0,
        topic_performance JSON DEFAULT '{}',
        weak_areas JSON DEFAULT '[]',
        recommended_topics JSON DEFAULT '[]',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # Create user_question_history table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_question_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        attempted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(question_id) REFERENCES question_bank(id)
    )
    """)

    conn.commit()
    conn.close()
    print(f"Migrated {db_path} successfully.")

print("All migrations complete!")
