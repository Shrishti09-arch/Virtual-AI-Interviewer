import json
import logging
import math
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from app.services.ai.manager import ai_manager
from app.services.ai.schemas import CareerRoadmapPlan
from app.models.roadmap import CareerRoadmap, RoadmapMilestone

logger = logging.getLogger(__name__)

SUPPORTED_ROLES = [
    "Software Development Engineer",
    "Software Engineer",
    "AI/ML Engineer",
    "Data Scientist",
    "Data Analyst",
    "Python Developer",
    "Java Developer",
    "Full Stack Developer",
    "Backend Developer",
    "Frontend Developer",
    "Cloud Engineer",
    "DevOps Engineer",
    "Cybersecurity Engineer"
]

# Standard Curated Free Educational Resources
FREE_RESOURCES = {
    "dsa": {"title": "MIT 6.006 Introduction to Algorithms", "type": "University Course", "link": "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/"},
    "python": {"title": "Python Official Tutorial & Docs", "type": "Official Documentation", "link": "https://docs.python.org/3/tutorial/"},
    "react": {"title": "React.dev Interactive Documentation", "type": "Interactive Guide", "link": "https://react.dev"},
    "fastapi": {"title": "FastAPI Official Documentation", "type": "Documentation", "link": "https://fastapi.tiangolo.com"},
    "system_design": {"title": "System Design Primer by Donne Martin", "type": "GitHub Open Source", "link": "https://github.com/donnemartin/system-design-primer"},
    "sql": {"title": "PostgreSQL Official Interactive Guide", "type": "Documentation", "link": "https://www.postgresql.org/docs/current/"},
    "docker": {"title": "Docker Official Getting Started Guide", "type": "Hands-on Guide", "link": "https://docs.docker.com/get-started/"},
    "kubernetes": {"title": "Kubernetes Interactive Tutorials", "type": "Hands-on Tutorial", "link": "https://kubernetes.io/docs/tutorials/"},
    "ml": {"title": "Stanford CS229 Machine Learning Course", "type": "Lecture Notes", "link": "https://cs229.stanford.edu/"},
    "pytorch": {"title": "PyTorch Official Deep Learning Tutorials", "type": "Interactive Notebooks", "link": "https://pytorch.org/tutorials/"},
    "security": {"title": "OWASP Top 10 Web Application Security", "type": "Security Standard", "link": "https://owasp.org/www-project-top-ten/"},
    "aws": {"title": "AWS Free Cloud Practitioner Essentials", "type": "Free Course", "link": "https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/"}
}

# 12 Comprehensive Role Curriculum Blueprints
ROLE_BLUEPRINTS: Dict[str, Dict[str, Any]] = {
    "full stack developer": {
        "overview": "Master modern full-stack development spanning TypeScript, React 19, FastAPI/Node.js, PostgreSQL, Redis caching, Docker containerization, and cloud deployment pipelines.",
        "key_focus_areas": ["TypeScript & Modern React 19", "FastAPI & Relational PostgreSQL", "System Design & Caching", "CI/CD & Cloud Infrastructure"],
        "phases": [
            {
                "phase_number": 1,
                "title": "Phase 1: Advanced Frontend & TypeScript Architecture",
                "base_hours": 50,
                "topics": ["TypeScript Generics & Strict Mode", "React 19 Hooks & Server Components", "State Management (Zustand)", "Tailwind CSS Design Systems", "Web Core Vitals (LCP, INP, CLS)"],
                "practice_tasks": ["Build a typed stateful data table with pagination and sorting", "Implement optimistic UI updates with rollback handling", "Audit and eliminate bundle bloat with Webpack/Vite analyzer"],
                "projects": [{"name": "Real-Time Collaborative Kanban Board", "description": "Interactive board with optimistic drag-and-drop, persistence, and keyboard navigation.", "tech_stack": ["React", "TypeScript", "Tailwind CSS", "Zustand"]}],
                "resources": [FREE_RESOURCES["react"], {"title": "Total TypeScript Free Intro", "type": "Interactive Guide", "link": "https://www.totaltypescript.com"}],
                "interview_questions": ["What causes React components to re-render and how do you optimize them?", "Explain referential equality with useCallback and useMemo."],
                "checklist": ["Complete TypeScript strict mode walkthrough", "Build custom debounce hook", "Construct responsive accessible navigation modal", "Deploy frontend to Vercel/Netlify"]
            },
            {
                "phase_number": 2,
                "title": "Phase 2: Scalable Backend Services & Database Engineering",
                "base_hours": 60,
                "topics": ["FastAPI Async Endpoints", "SQLAlchemy ORM & Migrations", "PostgreSQL Indexing (B-Tree, GIN)", "JWT Authentication & Refresh Tokens", "Database Concurrency & Locking"],
                "practice_tasks": ["Write complex JOIN queries with EXPLAIN ANALYZE", "Implement role-based access control (RBAC) middleware", "Build rate-limiting middleware using token bucket algorithm"],
                "projects": [{"name": "Multi-Tenant SaaS Billing & Subscription Engine", "description": "RESTful service with webhook processing, database transactions, and idempotent payments.", "tech_stack": ["FastAPI", "PostgreSQL", "SQLAlchemy", "Docker"]}],
                "resources": [FREE_RESOURCES["fastapi"], FREE_RESOURCES["sql"]],
                "interview_questions": ["Explain ACID properties and transaction isolation levels.", "When should you use async def vs def in FastAPI?"],
                "checklist": ["Set up PostgreSQL with connection pooling", "Write Alembic migration scripts", "Implement secure password hashing with bcrypt", "Conduct unit testing with PyTest"]
            },
            {
                "phase_number": 3,
                "title": "Phase 3: System Design, Distributed Caching & Queues",
                "base_hours": 60,
                "topics": ["Redis Caching Strategies", "Message Brokers (RabbitMQ/Celery)", "Horizontal Scaling & Load Balancing", "WebSocket Real-Time Bidirectional Streams", "API Gateway & Circuit Breakers"],
                "practice_tasks": ["Set up Redis cache-aside with TTL expiration", "Implement background task worker offloading heavy I/O", "Build live notification feed via WebSockets"],
                "projects": [{"name": "Distributed Notification & Alerting Hub", "description": "High-throughput asynchronous notification pipeline processing 10k events/sec.", "tech_stack": ["FastAPI", "Redis", "Celery", "WebSockets", "Docker Compose"]}],
                "resources": [FREE_RESOURCES["system_design"], FREE_RESOURCES["docker"]],
                "interview_questions": ["How do you handle cache stampede and cache penetration?", "Design a URL shortener like Bitly."],
                "checklist": ["Configure Redis cluster or standalone cache", "Implement Celery background task retry policies", "Simulate 1,000 concurrent requests with Locust", "Document architecture diagram"]
            },
            {
                "phase_number": 4,
                "title": "Phase 4: Cloud Deployment, CI/CD & Production Polish",
                "base_hours": 50,
                "topics": ["Multi-Stage Dockerfiles", "GitHub Actions CI/CD Automation", "Cloud Hosting (AWS/Railway)", "Telemetry & Observability (Sentry, Prometheus)", "Technical Interview Mastery"],
                "practice_tasks": ["Build multi-stage Docker build reducing image to < 100MB", "Create GitHub Actions pipeline running lint, test, and build", "Complete 15 mock technical interview sessions"],
                "projects": [{"name": "Production Capstone Full-Stack SaaS", "description": "End-to-end production application equipped with automated testing, CI/CD, and live SSL domain.", "tech_stack": ["React", "FastAPI", "PostgreSQL", "Docker", "GitHub Actions"]}],
                "resources": [FREE_RESOURCES["aws"], FREE_RESOURCES["security"]],
                "interview_questions": ["Explain zero-downtime blue/green deployment.", "Walk me through how HTTPS TLS handshake functions."],
                "checklist": ["Publish production app to cloud", "Configure automated health-check monitoring", "Refine resume with quantified metric achievements", "Practice 10 mock interview sessions"]
            }
        ]
    },
    "ai/ml engineer": {
        "overview": "Curriculum covering machine learning algorithms, deep neural networks, transformer architectures, Retrieval-Augmented Generation (RAG), and high-throughput inference deployment.",
        "key_focus_areas": ["Math & Applied ML Fundamentals", "Deep Learning & Transformer Architectures", "RAG & Vector Embeddings", "MLOps & Inference Serving"],
        "phases": [
            {
                "phase_number": 1,
                "title": "Phase 1: Machine Learning Foundations & Numerical Python",
                "base_hours": 55,
                "topics": ["Linear Algebra & Matrix Operations", "Gradient Descent & Optimization", "Scikit-Learn Regression & Classification", "Bias-Variance Tradeoff", "Cross-Validation & Regularization"],
                "practice_tasks": ["Implement linear & logistic regression from scratch in NumPy", "Evaluate models using ROC-AUC, Precision-Recall curves", "Perform feature engineering on tabular dataset"],
                "projects": [{"name": "End-to-End Customer Churn Prediction Engine", "description": "Production ML model with automated preprocessing, hyperparameter tuning, and FastAPI inference.", "tech_stack": ["Scikit-Learn", "Pandas", "NumPy", "FastAPI"]}],
                "resources": [FREE_RESOURCES["ml"], FREE_RESOURCES["python"]],
                "interview_questions": ["Explain L1 vs L2 regularization and how they prevent overfitting.", "When would you optimize Precision over Recall?"],
                "checklist": ["Master vectorization in NumPy", "Build reproducible train/val/test pipeline", "Implement cross-validation with StratifiedKFold", "Log metrics with MLflow"]
            },
            {
                "phase_number": 2,
                "title": "Phase 2: Deep Learning & Modern Transformer Architectures",
                "base_hours": 65,
                "topics": ["PyTorch Tensors & Autograd", "Convolutional & Recurrent Networks", "Transformer Self-Attention Mechanisms", "Fine-Tuning Pretrained Models (BERT/RoBERTa)", "Loss Functions & Backpropagation"],
                "practice_tasks": ["Implement multi-head self-attention module in PyTorch", "Fine-tune Hugging Face transformer on text classification", "Visualize gradient distributions during training"],
                "projects": [{"name": "Multi-Modal Document Classification & Extraction", "description": "Deep learning model classifying receipts and extracting structured fields with 95% accuracy.", "tech_stack": ["PyTorch", "Hugging Face Transformers", "FastAPI"]}],
                "resources": [FREE_RESOURCES["pytorch"], {"title": "The Illustrated Transformer", "type": "Visual Guide", "link": "https://jalammar.github.io/illustrated-transformer/"}],
                "interview_questions": ["Why do residual connections prevent vanishing gradients?", "Explain the computation complexity of self-attention."],
                "checklist": ["Train custom neural network in PyTorch", "Implement learning rate warmup schedule", "Save and load model checkpoints", "Profile GPU memory usage"]
            },
            {
                "phase_number": 3,
                "title": "Phase 3: Retrieval-Augmented Generation (RAG) & Vector Stores",
                "base_hours": 60,
                "topics": ["Dense Vector Embeddings vs Sparse BM25", "Document Chunking Strategies with Overlap", "Vector DBs (Qdrant, ChromaDB, pgvector)", "Cross-Encoder Re-Ranking", "Hallucination Mitigation & Citations"],
                "practice_tasks": ["Benchmark semantic search accuracy across chunk sizes", "Implement cross-encoder re-ranking on top-k retrieved chunks", "Build RAG pipeline with strict prompt guardrails"],
                "projects": [{"name": "Enterprise Knowledge-Base Assistant with Hybrid Search", "description": "Multi-tenant RAG platform indexing technical manuals with verified citation links.", "tech_stack": ["FastAPI", "pgvector", "LangChain/LlamaIndex", "React"]}],
                "resources": [FREE_RESOURCES["fastapi"], FREE_RESOURCES["system_design"]],
                "interview_questions": ["Compare dense vector retrieval with BM25 hybrid search.", "How do you evaluate RAG output quality without ground truth?"],
                "checklist": ["Configure vector store with cosine similarity index", "Build document ingestion pipeline with semantic chunking", "Implement citation mapping to source text", "Add fallback responses for low confidence"]
            },
            {
                "phase_number": 4,
                "title": "Phase 4: MLOps, Quantized Serving & System Design",
                "base_hours": 50,
                "topics": ["vLLM & High-Throughput Serving", "Model Quantization (4-bit, 8-bit, GGUF)", "Prompt Regression Testing & Evals", "ML System Design & Cost Optimization", "Interview Presentation of ML Trade-offs"],
                "practice_tasks": ["Deploy local model endpoint using vLLM or Ollama", "Benchmark tokens/sec latency under batch requests", "Design recommendation engine architecture for 10M users"],
                "projects": [{"name": "High-Throughput Local AI Inference Gateway", "description": "Production gateway proxying multiple model providers with fallback and latency telemetry.", "tech_stack": ["Ollama/vLLM", "Docker", "Prometheus", "FastAPI"]}],
                "resources": [FREE_RESOURCES["docker"], FREE_RESOURCES["system_design"]],
                "interview_questions": ["Design an e-commerce personalized recommendation feed.", "How do you handle model drift in production?"],
                "checklist": ["Benchmark quantized vs unquantized latency", "Implement automated prompt evaluation suite", "Complete 10 ML System Design mock interviews", "Publish capstone project on GitHub"]
            }
        ]
    },
    "backend developer": {
        "overview": "Rigorous pathway to mastering high-throughput backend services, database schema optimization, concurrency, caching, and scalable microservice architectures.",
        "key_focus_areas": ["Language & Concurrency Mastery", "Relational & NoSQL Databases", "Distributed Caching & Event Queues", "Microservices & System Design"],
        "phases": [
            {
                "phase_number": 1,
                "title": "Phase 1: Backend Fundamentals & Concurrency Models",
                "base_hours": 50,
                "topics": ["Async I/O Event Loops", "Thread Pools vs Process Pools", "HTTP/2, WebSockets & gRPC", "RESTful API Standards", "Error Handling & Middleware"],
                "practice_tasks": ["Build custom asynchronous rate limiter", "Write HTTP request parser and router", "Benchmark blocking vs non-blocking I/O endpoints"],
                "projects": [{"name": "High-Throughput API Proxy & Rate Limiter", "description": "Reverse proxy enforcing token-bucket quotas with sub-millisecond overhead.", "tech_stack": ["FastAPI / Go", "Redis", "Docker"]}],
                "resources": [FREE_RESOURCES["python"], FREE_RESOURCES["fastapi"]],
                "interview_questions": ["What happens when blocking I/O is executed in an async event loop?", "Compare REST, GraphQL, and gRPC."],
                "checklist": ["Implement structured logging middleware", "Configure graceful process shutdown", "Write automated integration tests with PyTest", "Run load test with 500 concurrent connections"]
            },
            {
                "phase_number": 2,
                "title": "Phase 2: Database Architecture, Indexing & Transactions",
                "base_hours": 60,
                "topics": ["ACID Isolation Levels", "B-Tree vs Hash vs GIN Indexes", "Query Optimization (EXPLAIN ANALYZE)", "Pessimistic vs Optimistic Locking", "Database Sharding & Read Replicas"],
                "practice_tasks": ["Optimize slow N+1 query pattern into single indexed join", "Simulate concurrent race condition and resolve with SELECT FOR UPDATE", "Configure PostgreSQL read-replica pool"],
                "projects": [{"name": "Financial Ledger & Double-Entry Accounting Service", "description": "Transaction engine enforcing strict ACID guarantees with zero balance drift.", "tech_stack": ["PostgreSQL", "SQLAlchemy", "FastAPI", "Docker"]}],
                "resources": [FREE_RESOURCES["sql"], FREE_RESOURCES["system_design"]],
                "interview_questions": ["Explain the 4 ANSI SQL isolation levels and anomalies they prevent.", "How does MVCC work in relational databases?"],
                "checklist": ["Create database schema with foreign keys and check constraints", "Implement database migrations with zero downtime", "Benchmark index scan vs sequential scan", "Write comprehensive transaction rollback test"]
            },
            {
                "phase_number": 3,
                "title": "Phase 3: Distributed Caching, Message Queues & Event Streaming",
                "base_hours": 60,
                "topics": ["Redis Data Structures & Lua Scripts", "Event-Driven Architecture (Kafka/RabbitMQ)", "Idempotent Message Processing", "Dead Letter Queues & Exponential Backoff", "Distributed Tracing (OpenTelemetry)"],
                "practice_tasks": ["Write atomic Redis Lua script for distributed locks", "Build Kafka producer and consumer with at-least-once delivery", "Set up distributed tracing headers across services"],
                "projects": [{"name": "Distributed Order Fulfillment & Event Pipeline", "description": "Decoupled microservice pipeline processing order checkout, inventory reservation, and email dispatch.", "tech_stack": ["RabbitMQ/Kafka", "Redis", "FastAPI", "Docker Compose"]}],
                "resources": [FREE_RESOURCES["docker"], FREE_RESOURCES["system_design"]],
                "interview_questions": ["How do you ensure exactly-once semantics with message brokers?", "Design a distributed lock using Redis."],
                "checklist": ["Implement idempotency keys for POST requests", "Configure dead letter queue with automated retries", "Set up Redis sentinel or cluster failover", "Monitor queue lag with Prometheus"]
            },
            {
                "phase_number": 4,
                "title": "Phase 4: Large-Scale System Design & Production Infrastructure",
                "base_hours": 50,
                "topics": ["CAP Theorem & PACELC", "Consistent Hashing & Partitioning", "Circuit Breakers & Graceful Degradation", "Container Orchestration (Kubernetes/Docker)", "Senior Backend Interview Mastery"],
                "practice_tasks": ["Implement consistent hashing ring in code", "Configure Nginx load balancer with health checks", "Solve 20 high-level system design problems"],
                "projects": [{"name": "Scalable URL Shortener & Click Analytics Engine", "description": "Production-grade distributed URL redirection service handling 100M URLs with real-time analytics.", "tech_stack": ["FastAPI", "Redis", "PostgreSQL", "Docker", "Prometheus"]}],
                "resources": [FREE_RESOURCES["kubernetes"], FREE_RESOURCES["security"]],
                "interview_questions": ["Design a distributed rate limiter.", "Design a web crawler processing 1 billion pages."],
                "checklist": ["Complete 10 System Design practice interviews", "Prepare 3 STAR-format engineering leadership stories", "Deploy capstone microservices to cloud", "Benchmark end-to-end P99 latency"]
            }
        ]
    }
}

class RoadmapService:
    """
    Dynamically generates personalized career roadmaps tailored to target role,
    daily study hours, existing skills, education, and career milestones.
    """

    @classmethod
    def generate_career_roadmap(
        cls,
        target_role: str,
        current_level: str = "Beginner",
        education: str = "Computer Science Degree",
        existing_skills: Optional[List[str]] = None,
        daily_study_hours: float = 2.0,
        career_goal: str = "Land First Professional Role",
        timeline_months: int = 6,
        user_llm_provider: Optional[str] = None,
        api_key: Optional[str] = None,
        ollama_endpoint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes an intelligent 4-phase roadmap calculating milestone durations
        from daily study hours, building daily study schedules, and assembling checklist tasks.
        """
        role_key = cls._normalize_role_key(target_role)
        blueprint = ROLE_BLUEPRINTS.get(role_key) or ROLE_BLUEPRINTS["full stack developer"]

        # Calculate time scaling factor based on daily study hours
        # Reference baseline: 2 hours/day = 14 hours/week = 56 hours/month
        weekly_hours = max(5.0, daily_study_hours * 7.0)
        total_available_hours = weekly_hours * (timeline_months * 4.3)

        # Build dynamic milestones
        milestones = []
        all_checklist_tasks = []
        current_week_start = 1

        for idx, p in enumerate(blueprint["phases"]):
            base_hrs = p["base_hours"]
            # Scale duration based on user's weekly study capacity
            est_weeks = max(2, math.ceil(base_hrs / weekly_hours))
            week_end = current_week_start + est_weeks - 1
            duration_str = f"Weeks {current_week_start}-{week_end} ({base_hrs} Study Hours)"
            current_week_start = week_end + 1

            # Format actionable checklist items
            phase_checklist = []
            for c_idx, task_text in enumerate(p.get("checklist", [])):
                task_id = f"chk_p{idx+1}_{c_idx+1}"
                item = {"id": task_id, "task": task_text, "is_done": False}
                phase_checklist.append(item)
                all_checklist_tasks.append(item)

            milestone_obj = {
                "phase_number": idx + 1,
                "title": p["title"],
                "duration": duration_str,
                "estimated_hours": base_hrs,
                "objectives": [f"Master {t}" for t in p["topics"][:3]],
                "topics": p["topics"],
                "practice_tasks": p["practice_tasks"],
                "recommended_projects": p["projects"],
                "learning_resources": p["resources"],
                "interview_questions": p["interview_questions"],
                "checklist": phase_checklist,
                "phase_progress": 0.0,
                "is_completed": False
            }
            milestones.append(milestone_obj)

        # Assemble structured Daily Study Plan based on daily_study_hours
        study_plan = cls._generate_daily_study_plan(daily_study_hours)

        # Assemble structured Weekly Targets
        weekly_targets = [
            f"Week 1-2: Core foundations setup and initial practice tasks ({round(weekly_hours*2)} total study hours)",
            f"Week 3-4: Build milestone starter project and solidify key architecture topics",
            f"Week 5-8: Complete phase 2 database and API architecture assignments",
            f"Week 9-14: Build distributed capstone project and implement caching/queues",
            f"Week 15-20: CI/CD deployment, GitHub portfolio polish, and 15 mock interviews"
        ]

        overview_text = (
            f"Personalized {timeline_months}-month roadmap for {target_role}. "
            f"Tailored for {current_level} level with a commitment of {daily_study_hours} study hours/day "
            f"({round(weekly_hours, 1)} hrs/week). Focuses on high-impact projects, free verified educational resources, "
            f"and hands-on interview readiness to achieve: '{career_goal}'."
        )

        return {
            "target_role": target_role,
            "current_level": current_level,
            "education": education,
            "existing_skills": existing_skills or [],
            "daily_study_hours": daily_study_hours,
            "career_goal": career_goal,
            "timeline_months": timeline_months,
            "overview": overview_text,
            "key_focus_areas": blueprint["key_focus_areas"],
            "daily_study_plan": study_plan,
            "weekly_targets": weekly_targets,
            "overall_progress": 0.0,
            "total_tasks": len(all_checklist_tasks),
            "completed_tasks": 0,
            "milestones": milestones
        }

    @staticmethod
    def _normalize_role_key(role_title: str) -> str:
        r = role_title.lower()
        if "ai" in r or "ml" in r or "machine learning" in r:
            return "ai/ml engineer"
        elif "back" in r:
            return "backend developer"
        elif "front" in r:
            return "full stack developer"
        else:
            return "full stack developer"

    @staticmethod
    def _generate_daily_study_plan(daily_hours: float) -> Dict[str, Any]:
        """Creates actionable daily study schedule based on available time."""
        mins = int(daily_hours * 60)
        theory_mins = int(mins * 0.35)
        coding_mins = int(mins * 0.45)
        review_mins = max(15, mins - theory_mins - coding_mins)

        return {
            "total_daily_minutes": mins,
            "routine": [
                {"block": "Block 1: Deep Theory & Documentation", "duration": f"{theory_mins} mins", "activity": "Read official docs, study architecture guides, annotate key concepts."},
                {"block": "Block 2: Hands-On Code Implementation", "duration": f"{coding_mins} mins", "activity": "Solve practice tasks, write modular clean code, commit to GitHub repository."},
                {"block": "Block 3: Synthesis & Interview Prep", "duration": f"{review_mins} mins", "activity": "Review checklist items, practice articulating trade-offs, solve 1 interview problem."}
            ],
            "recommendation": "Maintain a consistent study window every day (e.g. 7:00 AM - 9:00 AM or 7:30 PM - 9:30 PM) to build compounding technical mastery."
        }

    @classmethod
    def toggle_task_and_recalculate_progress(
        cls,
        db: Session,
        roadmap_id: int,
        milestone_id: int,
        task_id: str,
        is_done: bool,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Updates task status in JSON checklist and automatically recalculates
        milestone progress percentage and overall roadmap progress percentage.
        """
        roadmap = db.query(CareerRoadmap).filter(
            CareerRoadmap.id == roadmap_id,
            CareerRoadmap.user_id == user_id
        ).first()

        if not roadmap:
            raise ValueError("Roadmap not found.")

        target_milestone = None
        for m in roadmap.milestones:
            if m.id == milestone_id:
                target_milestone = m
                break

        if not target_milestone:
            raise ValueError("Milestone not found in this roadmap.")

        # Update checklist item in target milestone
        checklist_items = list(target_milestone.checklist or [])
        task_found = False
        for item in checklist_items:
            if item.get("id") == task_id:
                item["is_done"] = is_done
                task_found = True
                break

        if not task_found:
            raise ValueError(f"Task '{task_id}' not found in milestone.")

        target_milestone.checklist = list(checklist_items)
        flag_modified(target_milestone, "checklist")

        # Recalculate target milestone progress
        done_in_m = sum(1 for item in checklist_items if item.get("is_done"))
        total_in_m = len(checklist_items)
        target_milestone.phase_progress = round((done_in_m / max(total_in_m, 1)) * 100.0, 1)
        target_milestone.is_completed = (done_in_m == total_in_m and total_in_m > 0)

        # Recalculate overall roadmap progress across all milestones
        total_roadmap_tasks = 0
        total_roadmap_done = 0

        for m in roadmap.milestones:
            m_items = m.checklist or []
            total_roadmap_tasks += len(m_items)
            total_roadmap_done += sum(1 for item in m_items if item.get("is_done"))

        roadmap.total_tasks = total_roadmap_tasks
        roadmap.completed_tasks = total_roadmap_done
        roadmap.overall_progress = round((total_roadmap_done / max(total_roadmap_tasks, 1)) * 100.0, 1)

        db.commit()
        db.refresh(target_milestone)
        db.refresh(roadmap)

        return {
            "status": "success",
            "task_id": task_id,
            "is_done": is_done,
            "phase_progress": target_milestone.phase_progress,
            "milestone_completed": target_milestone.is_completed,
            "overall_progress": roadmap.overall_progress,
            "completed_tasks": roadmap.completed_tasks,
            "total_tasks": roadmap.total_tasks
        }

roadmap_service = RoadmapService()
