import io
from app.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.resume import Resume, ResumeAnalysis
from app.services.resume_service import resume_service
from app.routers import resumes
from app.schemas.resume import (
    ResumeExtractedDataUpdate,
    ExtractedResumeData,
    ResumeCorrectionActionRequest
)

def test_module1_resume():
    db = SessionLocal()
    try:
        print("=== 1. Testing Resume Extraction & Parsing ===", flush=True)
        sample_resume_text = """
        SARAH CONNER
        Email: sarah.conner@techcareer.io | Phone: (555) 234-5678 | Location: Seattle, WA
        LinkedIn: linkedin.com/in/sarahconner | GitHub: github.com/sarahconner

        PROFESSIONAL SUMMARY
        Full Stack Software Engineer with 4+ years of experience architecting distributed cloud applications, scalable APIs, and reactive web applications.

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
        • Assisted in database query optimization reducing p99 latency by 40ms.

        INTERNSHIPS
        Software Engineering Intern - NextGen Devs (Summer 2021)
        • Helped with developing automated CI/CD pipelines using GitHub Actions.
        • Implemented unit test coverage with Jest and PyTest across 12 services.

        PROJECTS
        Distributed Event Streaming Platform (FastAPI, Redis, Docker)
        • Architected real-time WebSocket broker processing 10k messages per second.
        • Deployed containerized clusters on AWS ECS with zero-downtime rolling updates.

        CERTIFICATIONS
        • AWS Certified Solutions Architect - Associate
        • Certified Kubernetes Administrator (CKA)

        ACHIEVEMENTS
        • 1st Place Winner - Pacific Northwest Cloud Hackathon 2022
        • Published research paper on high-throughput distributed state management
        """

        # 1. Test extraction of all 10 fields
        extracted = resume_service.extract_structured_resume_data(sample_resume_text)
        assert extracted["full_name"] == "Sarah Conner", f"Expected Sarah Conner, got {extracted['full_name']}"
        assert extracted["email"] == "sarah.conner@techcareer.io"
        assert extracted["phone"] == "(555) 234-5678"
        assert len(extracted["education"]) > 0
        assert len(extracted["technical_skills"]) > 0
        assert len(extracted["work_experience"]) > 0
        assert len(extracted["internships"]) > 0
        assert len(extracted["projects"]) > 0
        assert len(extracted["certifications"]) > 0
        assert len(extracted["achievements"]) > 0
        print("[PASS] All 10 structured sections extracted accurately:", flush=True)
        print(f"       - Full Name: {extracted['full_name']}", flush=True)
        print(f"       - Email: {extracted['email']}, Phone: {extracted['phone']}", flush=True)
        print(f"       - Education entries: {len(extracted['education'])}", flush=True)
        print(f"       - Skill categories: {list(extracted['technical_skills'].keys())}", flush=True)
        print(f"       - Work experience: {len(extracted['work_experience'])} jobs", flush=True)
        print(f"       - Internships: {len(extracted['internships'])} entries", flush=True)
        print(f"       - Projects: {len(extracted['projects'])} projects", flush=True)
        print(f"       - Certifications: {len(extracted['certifications'])} items", flush=True)
        print(f"       - Achievements: {len(extracted['achievements'])} items", flush=True)

        print("\n=== 2. Testing ATS Analysis & Section-Wise Scores ===", flush=True)
        user = db.query(User).first()
        assert user is not None

        analysis = resumes.analyze_resume_text(
            target_role="Full Stack Software Engineer",
            resume_text=sample_resume_text,
            job_description="Seeking a Full Stack Engineer with React, FastAPI, PostgreSQL, and Docker.",
            current_user=user,
            db=db
        )

        assert 0 <= analysis.overall_ats_score <= 100
        assert len(analysis.section_scores) >= 10
        assert "formatting" in analysis.section_scores
        assert "structure" in analysis.section_scores
        assert "keywords" in analysis.section_scores
        assert "technical_skills" in analysis.section_scores
        assert "experience" in analysis.section_scores
        assert "grammar" in analysis.section_scores
        assert "readability" in analysis.section_scores
        assert len(analysis.weak_sentences) > 0
        assert "not guaranteed" in analysis.disclaimer.lower()
        print(f"[PASS] Overall ATS score: {analysis.overall_ats_score}/100", flush=True)
        print(f"[PASS] Section-wise scores: {list(analysis.section_scores.keys())}", flush=True)
        print(f"[PASS] Readability score: {analysis.readability_score}/100 (Grade level: {analysis.readability_metrics.get('estimated_grade_level')})", flush=True)
        print(f"[PASS] Disclaimer verified: '{analysis.disclaimer[:65]}...'", flush=True)

        print("\n=== 3. Testing AI Resume Corrections (Before & After) ===", flush=True)
        assert len(analysis.corrections) > 0
        first_correction = analysis.corrections[0]
        assert "original" in first_correction
        assert "corrected" in first_correction
        assert "explanation" in first_correction
        assert first_correction["status"] == "pending"
        print(f"[PASS] Generated {len(analysis.corrections)} factual corrections.", flush=True)
        print(f"       [Original]  : {first_correction['original']}", flush=True)
        print(f"       [Corrected] : {first_correction['corrected']}", flush=True)
        print(f"       [Category]  : {first_correction['category']}", flush=True)

        print("\n=== 4. Testing User Accept / Reject Correction Action ===", flush=True)
        cid = first_correction["id"]
        res_action = resumes.handle_correction_action(
            analysis_id=analysis.id,
            correction_id=cid,
            payload=ResumeCorrectionActionRequest(action="accept"),
            current_user=user,
            db=db
        )
        assert res_action["status"] == "success"
        matched = [c for c in res_action["corrections"] if c["id"] == cid]
        assert matched[0]["status"] == "accepted"
        print(f"[PASS] Correction {cid} accepted and updated in database.", flush=True)

        print("\n=== 5. Testing Review & Edit Extracted Data ===", flush=True)
        # Fetch current extracted
        curr_ext = resumes.get_extracted_resume_data(analysis.resume_id, current_user=user, db=db)
        assert curr_ext["resume_id"] == analysis.resume_id
        
        # User edits their phone and adds an extra skill
        edited_data = ExtractedResumeData(**curr_ext["extracted_data"])
        edited_data.phone = "+1 (555) 999-8888"
        edited_data.technical_skills.setdefault("Languages", []).append("Rust")

        update_res = resumes.update_extracted_resume_data(
            resume_id=analysis.resume_id,
            update_data=ResumeExtractedDataUpdate(extracted_data=edited_data),
            current_user=user,
            db=db
        )
        assert update_res.overall_ats_score > 0
        assert update_res.extracted_data["phone"] == "+1 (555) 999-8888"
        assert "Rust" in update_res.extracted_data["technical_skills"]["Languages"]
        print("[PASS] User successfully reviewed and edited extracted resume data. Fresh ATS score computed.", flush=True)

        print("\n=======================================================", flush=True)
        print("ALL MODULE 1 BACKEND TESTS PASSED 100%!", flush=True)
        print("=======================================================", flush=True)

    finally:
        db.close()

if __name__ == "__main__":
    test_module1_resume()
