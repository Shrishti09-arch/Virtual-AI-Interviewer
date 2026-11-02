from app.database import SessionLocal
from app.models.user import User
from app.services.resume_service import resume_service
from app.routers import resumes
from app.schemas.resume import JobMatchRequest

def test_module3_matcher():
    db = SessionLocal()
    try:
        print("=== 1. Testing Job Description Matcher Engine ===", flush=True)

        sample_resume = """
        ALEX MORGAN - SENIOR FULL STACK ENGINEER
        Email: alex.morgan@careercoach.ai | Phone: (555) 019-2834
        LinkedIn: linkedin.com/in/alexmorgan | GitHub: github.com/alexmorgan

        PROFESSIONAL SUMMARY
        Innovative Full Stack Software Engineer with 5+ years building distributed applications using React, TypeScript, FastAPI, PostgreSQL, and Docker.

        PROFESSIONAL EXPERIENCE
        Senior Software Engineer - Apex Cloud (2022 - Present)
        • Architected microservices platform handling 50M requests daily, reducing latency by 45%.
        • Spearheaded migration to React 19 and Tailwind CSS, increasing page load speed by 30%.
        • Optimized PostgreSQL indexing and query execution, cutting database CPU utilization by 40%.
        • Engineered automated CI/CD deployment pipelines using Docker and GitHub Actions.

        KEY PROJECTS
        High-Throughput Rate Limiter (FastAPI, Redis, Docker)
        • Designed token-bucket rate limiter middleware enforcing tenant API quotas with sub-millisecond overhead.

        TECHNICAL SKILLS
        Languages: Python, TypeScript, JavaScript, SQL, Go
        Frameworks: React, FastAPI, Next.js, Node.js, Tailwind CSS
        Databases & Cloud: PostgreSQL, Redis, Docker, AWS, GitHub Actions

        EDUCATION
        B.S. in Computer Science - UC Berkeley (2018 - 2022)
        """

        sample_job_description = """
        We are seeking a Senior Backend / Distributed Systems Engineer to scale our core event streaming and cloud architecture.

        Key Responsibilities:
        • Architect, build, and maintain high-throughput microservices using Python, FastAPI, and Kubernetes.
        • Design scalable data pipelines and distributed caching layers utilizing Redis and Kafka.
        • Collaborate cross-functionally to deploy cloud native services on AWS with Terraform and CI/CD automation.
        • Ensure 99.99% high availability, system design reliability, and perform unit testing with PyTest.

        Qualifications:
        • 4+ years of professional software engineering experience.
        • Strong proficiency in Python, RESTful API architecture, PostgreSQL, and Docker.
        • Hands-on experience with Kafka, Kubernetes, and AWS is strongly preferred.
        • Passion for clean code, concurrency, and automated test coverage.
        """

        user = db.query(User).first()
        assert user is not None

        req = JobMatchRequest(
            resume_text=sample_resume,
            job_description=sample_job_description,
            target_role="Senior Backend Engineer"
        )

        match_res = resumes.match_job_description_endpoint(req, current_user=user, db=db)

        # 1. Matching skills
        assert len(match_res.matching_skills) > 0
        assert "Python" in match_res.matching_skills
        assert "Fastapi" in match_res.matching_skills or "FastAPI" in match_res.matching_skills
        assert "Docker" in match_res.matching_skills
        assert "Postgresql" in match_res.matching_skills or "PostgreSQL" in match_res.matching_skills
        print(f"[PASS] Matching skills ({len(match_res.matching_skills)}): {match_res.matching_skills}", flush=True)

        # 2. Missing skills
        assert len(match_res.missing_skills) > 0
        print(f"[PASS] Missing skills ({len(match_res.missing_skills)}): {match_res.missing_skills}", flush=True)

        # 3. Keyword match percentage
        assert 0 <= match_res.keyword_match_percentage <= 100
        assert 0 <= match_res.overall_fit_score <= 100
        print(f"[PASS] Keyword Match Percentage: {match_res.keyword_match_percentage}% (Overall Fit: {match_res.overall_fit_score}%)", flush=True)

        # 4. Relevant experience mapping
        assert len(match_res.relevant_experience) > 0
        first_exp = match_res.relevant_experience[0]
        assert "resume_snippet" in first_exp.dict()
        assert "matched_jd_requirement" in first_exp.dict()
        assert first_exp.relevance_score > 0
        print(f"[PASS] Relevant Experience Snippet ({len(match_res.relevant_experience)} mapped):", flush=True)
        print(f"       Resume Bullet: '{first_exp.resume_snippet}'", flush=True)
        print(f"       JD Requirement: '{first_exp.matched_jd_requirement}'", flush=True)
        print(f"       Relevance Score: {first_exp.relevance_score}%", flush=True)

        # 5. Technical skill gaps
        assert len(match_res.technical_skill_gaps) > 0
        first_gap = match_res.technical_skill_gaps[0]
        assert first_gap.category is not None
        assert len(first_gap.missing_skills) > 0
        assert first_gap.impact in ["Critical", "Important", "Nice-to-Have"]
        print(f"[PASS] Technical Skill Gaps ({len(match_res.technical_skill_gaps)} categories):", flush=True)
        for gap in match_res.technical_skill_gaps:
            print(f"       [{gap.impact}] {gap.category}: {gap.missing_skills}", flush=True)

        # 6. Strategic Recommendations
        assert len(match_res.recommendations) >= 3
        print(f"[PASS] Recommendations ({len(match_res.recommendations)}):", flush=True)
        for rec in match_res.recommendations:
            print(f"       - {rec}", flush=True)

        # 7. Summary Verdict & Report Header
        assert len(match_res.summary_verdict) > 0
        assert len(match_res.candidate_strengths) > 0
        print(f"[PASS] Summary Verdict: '{match_res.summary_verdict}'", flush=True)
        print(f"[PASS] Candidate Strengths: {match_res.candidate_strengths}", flush=True)

        print("\n=======================================================", flush=True)
        print("ALL MODULE 3 JOB DESCRIPTION MATCHER TESTS PASSED 100%!", flush=True)
        print("=======================================================", flush=True)

    finally:
        db.close()

if __name__ == "__main__":
    test_module3_matcher()
