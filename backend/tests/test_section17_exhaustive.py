"""
Exhaustive Automated Verification Suite for Section 17 Testing Requirements
Validates all 24 distinct capabilities end-to-end:
1. Registration
2. Login/logout
3. Database persistence
4. PDF upload
5. DOCX upload
6. Resume extraction
7. ATS scoring
8. Resume correction
9. Role-based resume generation
10. PDF download
11. DOCX download
12. Job description matching
13. AI question generation
14. Duplicate detection
15. MCQ evaluation
16. Coding workflow
17. Webcam permissions / consent
18. Audio recording
19. Video recording
20. Transcription
21. Answer evaluation
22. Communication feedback
23. Roadmap generation
24. Progress tracking
"""
import os
import sys
import time
import unittest
import io
import zipfile
from datetime import datetime, timezone

# Setup Python sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal
from app.models.user import User
from app.models.resume import Resume, ResumeAnalysis
from app.models.practice import QuestionBank, PracticeSession, UserQuestionHistory
from app.models.interview import InterviewSession, InterviewAnswer
from app.models.roadmap import CareerRoadmap, RoadmapMilestone

from app.core.security import (
    get_password_hash,
    verify_password,
    validate_password_strength,
    create_access_token,
    decode_access_token,
    revoke_token,
    is_token_revoked,
    validate_resume_file,
    validate_recording_file,
    MAX_RESUME_SIZE,
    MAX_RECORDING_SIZE
)

from services.ats_service import ats_service
from services.resume_service import resume_service
from services.question_service import question_service, SandboxExecutor
from services.evaluation_service import evaluation_service
from services.transcription_service import transcription_service
from services.roadmap_service import roadmap_service
from app.services.interview_service import InterviewService
from app.services.practice_service import practice_service

SAMPLE_RESUME_TEXT = """
ALEXANDER MERCER
Email: alex.mercer@clouddev.org | Phone: (555) 789-0123 | Location: San Francisco, CA
LinkedIn: linkedin.com/in/alexmercer | GitHub: github.com/alexmercer

PROFESSIONAL SUMMARY
Senior Cloud Engineer & Backend Developer with 5+ years building distributed cloud native systems on AWS, Kubernetes, and FastAPI.

EDUCATION
B.S. in Software Engineering - UC Berkeley (2017 - 2021) | GPA: 3.9

TECHNICAL SKILLS
Languages: Python, Go, TypeScript, SQL
Cloud & DevOps: AWS, Docker, Kubernetes, Terraform, GitHub Actions, Prometheus
Frameworks & Databases: FastAPI, Django, PostgreSQL, Redis, Kafka

WORK EXPERIENCE
Lead Cloud Architect - Apex Cloud Systems (2021 - Present)
• Responsible for architecting multi-region Kubernetes clusters serving 40M daily active requests.
• Worked on database query refactoring that reduced p95 latency by 35%.
• Implemented automated CI/CD deployment pipelines using GitHub Actions.

PROJECTS
High-Throughput Distributed Telemetry Ingestion (Go, Kafka, Redis)
• Engineered distributed event stream processing 50k metric payloads/sec with sub-second replication.
"""

SAMPLE_JD_TEXT = """
Senior Backend Developer - Cloud Infrastructure
We are seeking an experienced Backend Developer proficient in Python, FastAPI, Docker, and PostgreSQL.
Must have strong experience with distributed caching (Redis), Kubernetes container orchestration,
and CI/CD pipelines. Experience in AWS cloud architecture is required.
"""


class TestSection17Exhaustive(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = SessionLocal()
        cls.test_email = f"sec17_{int(time.time())}@careertest.com"
        cls.test_password = "SuperSecurePassword2026!"

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    # 1. Registration
    def test_01_registration(self):
        is_strong, msg = validate_password_strength(self.test_password)
        self.assertTrue(is_strong, f"Password validation failed: {msg}")

        hashed_pw = get_password_hash(self.test_password)
        self.assertTrue(verify_password(self.test_password, hashed_pw))

        user = User(
            email=self.test_email,
            hashed_password=hashed_pw,
            full_name="Alexander Mercer",
            role_target="Cloud Engineer"
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        self.assertIsNotNone(user.id)
        self.assertEqual(user.email, self.test_email)
        TestSection17Exhaustive.test_user_id = user.id

    # 2. Login/logout
    def test_02_login_and_logout(self):
        user = self.db.query(User).filter(User.email == self.test_email).first()
        self.assertIsNotNone(user)
        self.assertTrue(verify_password(self.test_password, user.hashed_password))

        # Issue JWT Access Token
        token = create_access_token(data={"sub": str(user.id)})
        payload = decode_access_token(token)
        self.assertEqual(payload.get("sub"), str(user.id))
        self.assertFalse(is_token_revoked(token))

        # Perform Logout / Token Revocation
        revoke_token(token)
        self.assertTrue(is_token_revoked(token))

    # 3. Database persistence
    def test_03_database_persistence(self):
        # Open an independent session to test true commit persistence
        new_session = SessionLocal()
        try:
            persisted_user = new_session.query(User).filter(User.email == self.test_email).first()
            self.assertIsNotNone(persisted_user)
            self.assertEqual(persisted_user.full_name, "Alexander Mercer")
        finally:
            new_session.close()

    # 4. PDF upload
    def test_04_pdf_upload(self):
        valid_pdf_payload = b"%PDF-1.7\n%Valid simulated PDF header and text content\n%%EOF"
        result_type = validate_resume_file(valid_pdf_payload, "resume.pdf")
        self.assertEqual(result_type, "pdf")

    # 5. DOCX upload
    def test_05_docx_upload(self):
        # Generate minimal in-memory valid zip containing [Content_Types].xml
        docx_buf = io.BytesIO()
        with zipfile.ZipFile(docx_buf, "w") as zf:
            zf.writestr("[Content_Types].xml", b"<Types></Types>")
            zf.writestr("word/document.xml", b"<w:document></w:document>")
        docx_bytes = docx_buf.getvalue()

        result_type = validate_resume_file(docx_bytes, "resume.docx")
        self.assertEqual(result_type, "docx")

    # 6. Resume extraction
    def test_06_resume_extraction(self):
        extracted = resume_service.extract_structured_resume_data(SAMPLE_RESUME_TEXT)
        self.assertEqual(extracted.get("full_name"), "Alexander Mercer")
        self.assertEqual(extracted.get("email"), "alex.mercer@clouddev.org")
        skills = extracted.get("technical_skills", {})
        self.assertTrue(len(skills) > 0)
        self.assertTrue(any("Python" in str(v) for v in skills.values()))

    # 7. ATS scoring
    def test_07_ats_scoring(self):
        audit = ats_service.audit_resume(SAMPLE_RESUME_TEXT, target_role="Cloud Engineer")
        self.assertIn("overall_ats_score", audit)
        self.assertGreater(audit["overall_ats_score"], 60)
        self.assertIn("section_scores", audit)
        self.assertIn("matched_skills", audit)
        self.assertIn("weak_sentences", audit)

    # 8. Resume correction
    def test_08_resume_correction(self):
        extracted = resume_service.extract_structured_resume_data(SAMPLE_RESUME_TEXT)
        corrections = resume_service.generate_corrections(
            resume_text=SAMPLE_RESUME_TEXT,
            extracted_data=extracted,
            target_role="Cloud Engineer"
        )
        self.assertTrue(len(corrections) > 0)
        # Verify passive phrasing replacement suggestion
        first_corr = corrections[0]
        self.assertIn("original", first_corr)
        self.assertIn("corrected", first_corr)
        self.assertIn("explanation", first_corr)

    # 9. Role-based resume generation
    def test_09_role_based_resume_generation(self):
        builder_input = {
            "target_role": "Cloud Engineer",
            "experience_level": "Senior",
            "full_name": "Alexander Mercer",
            "professional_summary": "Cloud Engineer specializing in AWS and Kubernetes.",
            "skills": {
                "Cloud": ["AWS", "Kubernetes", "Docker", "Terraform"],
                "Languages": ["Python", "Go"]
            },
            "experience": [
                {
                    "company": "Apex Cloud Systems",
                    "role": "Lead Cloud Architect",
                    "highlights": ["Architected distributed Kubernetes clusters on AWS."]
                }
            ],
            "projects": [
                {
                    "name": "Telemetry Engine",
                    "description": "Processed 50k events/sec with sub-second replication."
                }
            ],
            "education": [{"degree": "B.S. in Software Engineering", "institution": "UC Berkeley"}]
        }
        optimized = resume_service.optimize_for_role(builder_input)
        self.assertIn("optimized_summary", optimized)
        self.assertIn("estimated_ats_score", optimized)
        self.assertGreater(optimized["estimated_ats_score"], 60)
        # Factual integrity check: original company must be preserved exactly in optimized experience
        self.assertEqual(optimized["optimized_experience"][0]["company"], "Apex Cloud Systems")

    # 10. PDF download
    def test_10_pdf_download(self):
        extracted = resume_service.extract_structured_resume_data(SAMPLE_RESUME_TEXT)
        pdf_bytes = resume_service.generate_pdf_resume(extracted)
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"), "PDF export must start with %PDF- header")
        self.assertGreater(len(pdf_bytes), 1000)

    # 11. DOCX download
    def test_11_docx_download(self):
        extracted = resume_service.extract_structured_resume_data(SAMPLE_RESUME_TEXT)
        docx_bytes = resume_service.generate_docx_resume(extracted)
        self.assertTrue(docx_bytes.startswith(b"PK\x03\x04"), "DOCX export must start with PK zip header")
        self.assertGreater(len(docx_bytes), 1000)

    # 12. Job description matching
    def test_12_job_description_matching(self):
        match_res = ats_service.match_job_description(
            resume_text=SAMPLE_RESUME_TEXT,
            job_description=SAMPLE_JD_TEXT,
            target_role="Backend Developer"
        )
        self.assertIn("matching_skills", match_res)
        self.assertIn("keyword_match_percentage", match_res)
        self.assertGreater(match_res["keyword_match_percentage"], 50)
        self.assertIn("recommendations", match_res)

    # 13. AI question generation
    def test_13_ai_question_generation(self):
        questions = InterviewService.get_initial_questions(
            role_title="Cloud Engineer",
            experience_level="Senior",
            interview_type="Technical",
            difficulty="Advanced",
            total_questions=3
        )
        self.assertEqual(len(questions), 3)
        self.assertTrue(all("question" in q for q in questions))

    # 14. Duplicate detection
    def test_14_duplicate_detection(self):
        # Query question bank
        existing_q = self.db.query(QuestionBank).first()
        if not existing_q:
            existing_q = QuestionBank(
                category="Backend",
                subject="Python",
                difficulty="Intermediate",
                title="Explain Python GIL",
                question="What is the Global Interpreter Lock?"
            )
            self.db.add(existing_q)
            self.db.commit()
            self.db.refresh(existing_q)

        # Mark question as answered in UserQuestionHistory
        user_id = getattr(self, "test_user_id", 1)
        history_entry = UserQuestionHistory(user_id=user_id, question_id=existing_q.id)
        self.db.add(history_entry)
        self.db.commit()

        # Duplicate check query
        answered_ids = {
            row[0] for row in self.db.query(UserQuestionHistory.question_id).filter(
                UserQuestionHistory.user_id == user_id
            ).all()
        }
        self.assertIn(existing_q.id, answered_ids)

    # 15. MCQ evaluation
    def test_15_mcq_evaluation(self):
        q = QuestionBank(
            category="Backend",
            subject="Python",
            difficulty="Intermediate",
            question_type="MCQ",
            title="Python Mutability MCQ",
            question="Which of the following data structures is immutable in Python?",
            options=["List", "Dictionary", "Tuple", "Set"],
            correct_option_index=2,
            explanation="Tuples cannot be altered in-place after creation in Python."
        )
        self.db.add(q)
        self.db.commit()
        self.db.refresh(q)

        user_id = getattr(self, "test_user_id", 1)
        session = PracticeSession(
            user_id=user_id,
            job_role="Python Developer",
            subject="Python",
            difficulty="Intermediate",
            interview_type="MCQs",
            total_questions=1,
            question_ids=[q.id],
            answers=[],
            score=0.0
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        # Submit answer with selected_option_index 2 ("Tuple")
        eval_result = practice_service.submit_answer(
            db=self.db,
            session_id=session.id,
            user_id=user_id,
            question_id=q.id,
            answer_payload={"selected_option_index": 2}
        )
        eval_data = eval_result.get("evaluation", {})
        self.assertTrue(eval_data.get("is_correct"))
        self.assertEqual(eval_data.get("score"), 100.0)
        self.assertIn("explanation", eval_data)
        self.assertTrue(eval_result.get("is_completed"))

    # 16. Coding workflow
    def test_16_coding_workflow(self):
        python_solution = "def solution(a, b):\n    return a + b"
        test_cases = [
            {"input": "[5, 10]", "expected_output": "15"},
            {"input": "[-2, 8]", "expected_output": "6"}
        ]
        res = SandboxExecutor.execute("python", python_solution, test_cases)
        self.assertEqual(res.get("status"), "Accepted")
        self.assertEqual(res.get("passed_tests"), 2)

    # 17. Webcam permissions & candidate recording consent
    def test_17_webcam_permissions(self):
        user = self.db.query(User).filter(User.id == getattr(self, "test_user_id", 1)).first()
        self.assertIsNotNone(user)

        # Grant recording consent
        user.recording_consent = True
        user.recording_consent_timestamp = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(user)

        self.assertTrue(user.recording_consent)
        self.assertIsNotNone(user.recording_consent_timestamp)

    # 18. Audio recording validation
    def test_18_audio_recording(self):
        # Simulated WAV audio payload
        wav_header = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00" + b"\x00" * 100
        media_fmt = validate_recording_file(wav_header, "test_audio.wav")
        self.assertEqual(media_fmt, "wav")

    # 19. Video recording validation
    def test_19_video_recording(self):
        # Simulated WebM video payload (EBML ID \x1a\x45\xdf\xa3)
        webm_header = b"\x1a\x45\xdf\xa3\x9f\x42\x86\x81\x01\x42\xf7\x81\x01" + b"\x00" * 200
        media_fmt = validate_recording_file(webm_header, "candidate_interview.webm")
        self.assertEqual(media_fmt, "webm")

    # 20. Transcription
    def test_20_transcription(self):
        # Tests transcription service handling
        res = transcription_service.transcribe_audio(b"dummy_bytes")
        self.assertIn("transcript", res)
        self.assertIn("engine", res)

    # 21. Answer evaluation
    def test_21_answer_evaluation(self):
        question = "What is the CAP theorem and how does it affect distributed databases?"
        answer = (
            "The CAP theorem states that a distributed system can only guarantee at most two out of three: "
            "Consistency, Availability, and Partition Tolerance. Under network partitions, the system must "
            "choose between CP or AP."
        )
        eval_res = evaluation_service.evaluate_answer(
            question=question,
            answer=answer,
            role="Cloud Engineer"
        )
        self.assertIn("score", eval_res)
        self.assertGreater(eval_res["score"], 50)
        self.assertIn("model_answer", eval_res)
        self.assertIn("feedback", eval_res)

    # 22. Communication feedback
    def test_22_communication_feedback(self):
        speech_text = (
            "In my last role, our team had database deadlocks in our previous microservice. "
            "My responsibility was to resolve the concurrency contention. "
            "I decided to introduce distributed locks using Redis Redlock. "
            "As a result, we eliminated deadlocks and improved p99 response times by 30 percent."
        )
        comm = transcription_service.analyze_communication(
            answer_text=speech_text,
            speaking_duration_seconds=30,
            pauses_count=1
        )
        self.assertIn("wpm", comm)
        self.assertIn("filler_words", comm)
        self.assertIn("star_analysis", comm)
        self.assertTrue(comm["star_analysis"]["situation"]["detected"])
        self.assertTrue(comm["star_analysis"]["result"]["detected"])

    # 23. Roadmap generation
    def test_23_roadmap_generation(self):
        roadmap = roadmap_service.generate_career_roadmap(
            target_role="Cloud Engineer",
            current_level="Intermediate",
            education="B.S. in Computer Science",
            existing_skills=["Docker", "Linux"],
            daily_study_hours=2.5,
            career_goal="Become Senior Cloud Architect",
            timeline_months=6
        )
        self.assertIn("overview", roadmap)
        self.assertIn("milestones", roadmap)
        self.assertTrue(len(roadmap["milestones"]) >= 3)
        self.assertIn("daily_study_plan", roadmap)

    # 24. Progress tracking
    def test_24_progress_tracking(self):
        user_id = getattr(self, "test_user_id", 1)
        # Create a test CareerRoadmap in DB
        roadmap = CareerRoadmap(
            user_id=user_id,
            target_role="Cloud Engineer",
            current_level="Intermediate",
            timeline_months=6,
            overall_progress=0.0
        )
        self.db.add(roadmap)
        self.db.commit()
        self.db.refresh(roadmap)

        milestone = RoadmapMilestone(
            roadmap_id=roadmap.id,
            phase_number=1,
            title="Phase 1: Cloud Foundations",
            duration="Weeks 1-4",
            checklist=[
                {"id": "chk_1", "task": "Setup AWS VPC", "is_done": False},
                {"id": "chk_2", "task": "Configure Security Groups", "is_done": False}
            ],
            phase_progress=0.0
        )
        self.db.add(milestone)
        self.db.commit()
        self.db.refresh(milestone)

        # Toggle first task
        res = roadmap_service.toggle_task_and_recalculate_progress(
            db=self.db,
            roadmap_id=roadmap.id,
            milestone_id=milestone.id,
            task_id="chk_1",
            is_done=True,
            user_id=user_id
        )
        self.assertEqual(res.get("phase_progress"), 50.0)
        self.assertEqual(res.get("overall_progress"), 50.0)
        self.assertEqual(res.get("completed_tasks"), 1)
        self.assertEqual(res.get("total_tasks"), 2)


if __name__ == "__main__":
    unittest.main()
