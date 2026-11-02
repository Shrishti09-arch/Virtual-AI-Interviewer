from app.database import SessionLocal
from app.models.user import User
from app.services.resume_service import resume_service, SUPPORTED_ROLES
from app.routers import resumes
from app.schemas.resume import (
    RoleOptimizeRequest,
    ResumeGenerateRequest,
    ResumeWorkExperience,
    ResumeEducation,
    ResumeProject
)

def test_module2_resume_builder():
    db = SessionLocal()
    try:
        print("=== 1. Testing 12 Supported Roles Taxonomy ===", flush=True)
        assert len(SUPPORTED_ROLES) == 12
        expected_roles = [
            "Software Development Engineer",
            "AI/ML Engineer",
            "Data Scientist",
            "Data Analyst",
            "Python Developer",
            "Java Developer",
            "Full Stack Developer",
            "Backend Developer",
            "Frontend Developer",
            "Cybersecurity Engineer",
            "Cloud Engineer",
            "DevOps Engineer"
        ]
        for r in expected_roles:
            assert r in SUPPORTED_ROLES, f"Missing role: {r}"
        print(f"[PASS] All 12 required roles are supported and verified.", flush=True)

        user = db.query(User).first()
        assert user is not None

        print("\n=== 2. Testing Role-Based AI Optimization Engine ===", flush=True)
        # Test Cybersecurity Engineer
        opt_req = RoleOptimizeRequest(
            target_role="Cybersecurity Engineer",
            experience_level="Senior (5+ yrs)",
            full_name="Marcus Vance",
            professional_summary="Experienced security specialist building defensive infrastructure.",
            skills={"Languages": ["Python", "Bash"], "Security": ["Splunk", "Wireshark"]},
            experience=[
                ResumeWorkExperience(
                    company="Fortress Cyber",
                    role="Security Analyst",
                    duration="2021 - Present",
                    highlights=[
                        "Responsible for monitoring SIEM alerts across 5,000 corporate endpoints.",
                        "Helped with annual SOC2 compliance audits."
                    ]
                )
            ],
            education=[
                ResumeEducation(
                    institution="Carnegie Mellon University",
                    degree="B.S. in Information Security",
                    year="2017 - 2021"
                )
            ],
            projects=[
                ResumeProject(
                    name="Automated Vulnerability Scanner",
                    technologies=["Python", "Nmap", "Docker"],
                    description="Worked on scanning network subnet ranges for outdated SSL certs."
                )
            ],
            certifications=["CISSP", "CompTIA Security+"],
            achievements=["DefCon CTF Finalist 2023"]
        )

        opt_res = resumes.optimize_resume_for_role(opt_req, current_user=user)
        assert opt_res.target_role == "Cybersecurity Engineer"
        assert "Senior" in opt_res.optimized_summary or "5+" in opt_res.optimized_summary
        assert len(opt_res.missing_keywords) > 0
        assert len(opt_res.matched_keywords) > 0
        assert "certifications" in opt_res.recommended_section_order
        assert opt_res.estimated_ats_score >= 60.0
        print(f"[PASS] Cybersecurity optimization: Score {opt_res.estimated_ats_score}%.", flush=True)
        print(f"       Summary: {opt_res.optimized_summary[:85]}...", flush=True)
        print(f"       Section Order: {opt_res.recommended_section_order}", flush=True)
        print(f"       Matched Keywords: {opt_res.matched_keywords}", flush=True)

        # Test Student / Intern ordering on AI/ML Engineer
        opt_req_student = RoleOptimizeRequest(
            target_role="AI/ML Engineer",
            experience_level="Student / Intern",
            full_name="Elena Rostova",
            skills={"Languages": ["Python"], "Frameworks": ["PyTorch"]},
            education=[
                ResumeEducation(
                    institution="Stanford University",
                    degree="B.S. in AI",
                    year="2022 - 2026"
                )
            ],
            projects=[
                ResumeProject(
                    name="Transformer RAG Pipeline",
                    technologies=["PyTorch", "Hugging Face", "ChromaDB"],
                    description="Built vector search question-answering system."
                )
            ]
        )
        opt_res_student = resumes.optimize_resume_for_role(opt_req_student, current_user=user)
        # Student order must prioritize education and projects
        assert opt_res_student.recommended_section_order[1] in ["education", "skills", "projects"]
        print(f"[PASS] Student AI/ML optimization: Section Order: {opt_res_student.recommended_section_order}", flush=True)

        print("\n=== 3. Testing ATS-Friendly PDF Generation (ReportLab) ===", flush=True)
        gen_req = ResumeGenerateRequest(
            full_name="Marcus Vance",
            email="marcus.vance@cybersec.io",
            phone="+1 (555) 777-9999",
            location="Washington, DC",
            linkedin="linkedin.com/in/marcusvance",
            github="github.com/marcusvance",
            target_role="Cybersecurity Engineer",
            experience_level="Senior (5+ yrs)",
            professional_summary=opt_res.optimized_summary,
            skills=opt_res.recommended_skills,
            experience=opt_res.optimized_experience,
            education=[
                ResumeEducation(
                    institution="Carnegie Mellon University",
                    degree="B.S. in Information Security",
                    year="2017 - 2021"
                )
            ],
            projects=opt_res.optimized_projects,
            certifications=["CISSP", "CompTIA Security+"],
            achievements=["DefCon CTF Finalist 2023"],
            section_order=opt_res.recommended_section_order
        )

        pdf_resp = resumes.generate_ats_pdf(gen_req, current_user=user)
        assert pdf_resp.media_type == "application/pdf"
        assert len(pdf_resp.body) > 1500
        print(f"[PASS] ATS-friendly PDF successfully generated ({len(pdf_resp.body)} bytes).", flush=True)

        print("\n=== 4. Testing ATS-Friendly DOCX Generation (python-docx) ===", flush=True)
        docx_resp = resumes.generate_ats_docx(gen_req, current_user=user)
        assert docx_resp.media_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert len(docx_resp.body) > 2000
        # Check ZIP / Office Open XML header magic bytes (PK..)
        assert docx_resp.body[:2] == b"PK", "Invalid DOCX magic bytes"
        print(f"[PASS] ATS-friendly DOCX successfully generated ({len(docx_resp.body)} bytes, valid PK ZIP container).", flush=True)

        print("\n=======================================================", flush=True)
        print("ALL MODULE 2 RESUME BUILDER BACKEND TESTS PASSED 100%!", flush=True)
        print("=======================================================", flush=True)

    finally:
        db.close()

if __name__ == "__main__":
    test_module2_resume_builder()
