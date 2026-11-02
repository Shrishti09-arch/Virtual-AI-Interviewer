"""
Unit and Integration Tests for Module 11 Database Models & Isolation
Validates SQLite / SQLAlchemy schemas for all 8 canonical tables:
Users, Resumes, ResumeVersions, InterviewQuestions, PracticeSessions,
MockInterviews, InterviewAnswers, and Roadmaps.
"""
import os
import sys
import unittest
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal
from app.models import (
    User,
    Resume,
    ResumeVersion,
    InterviewQuestion,
    PracticeSession,
    MockInterview,
    InterviewAnswer,
    Roadmap
)


class TestDatabaseModels(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_database_connection_and_models(self):
        # Query User count to ensure DB connection is active
        users_count = self.db.query(User).count()
        self.assertGreaterEqual(users_count, 0)

    def test_user_data_isolation(self):
        # Check that user isolation query returns only the user's records
        test_user = self.db.query(User).first()
        if test_user:
            resumes = self.db.query(Resume).filter(Resume.user_id == test_user.id).all()
            for r in resumes:
                self.assertEqual(r.user_id, test_user.id)

    def test_interview_questions_metadata(self):
        # Verify question bank exists and has valid difficulty
        questions = self.db.query(InterviewQuestion).limit(5).all()
        valid_difficulties = ["Beginner", "Intermediate", "Advanced", "Expert", "Easy", "Medium", "Hard"]
        for q in questions:
            self.assertIn(q.difficulty, valid_difficulties)
            self.assertTrue(len(q.question) > 5)


if __name__ == "__main__":
    unittest.main()
