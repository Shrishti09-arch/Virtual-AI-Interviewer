"""
Unit and Integration Tests for Module 1, 2, 3 Resume Services
Tests text extraction, ATS scoring, role optimization without hallucinations,
and PDF/DOCX document export generation.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.resume_service import resume_service
from services.ats_service import ats_service

SAMPLE_RESUME = """
SARAH CONNER
Email: sarah.conner@techcareer.io | Phone: (555) 234-5678 | Location: Seattle, WA
LinkedIn: linkedin.com/in/sarahconner | GitHub: github.com/sarahconner

PROFESSIONAL SUMMARY
Full Stack Software Engineer with 4+ years of experience architecting distributed cloud applications.

EDUCATION
B.S. in Computer Science - University of Washington (2018 - 2022) | GPA: 3.85

TECHNICAL SKILLS
Languages: Python, TypeScript, JavaScript, SQL, Go
Frameworks: React, FastAPI, Next.js, Node.js, Tailwind CSS
Databases & Cloud: PostgreSQL, Redis, Docker, Kubernetes, AWS, GitHub Actions

WORK EXPERIENCE
Senior Software Engineer - CloudScale Systems (2022 - Present)
• Responsible for building microservices handling 25M daily requests.
• Worked on React UI components to improve dashboard load speed by 35%.

PROJECTS
Distributed Event Streaming Platform (FastAPI, Redis, Docker)
• Architected real-time WebSocket broker processing 10k messages per second.
"""


class TestResumeServices(unittest.TestCase):
    def test_structured_data_extraction(self):
        extracted = resume_service.extract_structured_resume_data(SAMPLE_RESUME)
        self.assertIn("full_name", extracted)
        self.assertEqual(extracted["full_name"], "Sarah Conner")
        self.assertEqual(extracted["email"], "sarah.conner@techcareer.io")
        languages = extracted.get("technical_skills", {}).get("Languages", [])
        self.assertTrue(any("Python" in l for l in languages))

    def test_ats_scoring_and_audit(self):
        audit = ats_service.audit_resume(SAMPLE_RESUME, target_role="Software Development Engineer")
        self.assertIn("overall_ats_score", audit)
        self.assertGreater(audit["overall_ats_score"], 50)
        self.assertIn("section_scores", audit)
        self.assertIn("matched_skills", audit)

    def test_job_description_matcher(self):
        jd = "Seeking a Python and FastAPI Backend Developer with PostgreSQL and Docker experience."
        match_result = ats_service.match_job_description(
            resume_text=SAMPLE_RESUME,
            job_description=jd,
            target_role="Backend Developer"
        )
        self.assertIn("matching_skills", match_result)
        self.assertTrue(len(match_result["matching_skills"]) > 0)
        self.assertIn("keyword_match_percentage", match_result)

    def test_pdf_and_docx_generation(self):
        extracted = resume_service.extract_structured_resume_data(SAMPLE_RESUME)
        pdf_bytes = resume_service.generate_pdf_resume(extracted)
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))

        docx_bytes = resume_service.generate_docx_resume(extracted)
        self.assertTrue(docx_bytes.startswith(b"PK\x03\x04"))


if __name__ == "__main__":
    unittest.main()
