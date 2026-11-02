# Virtual AI Interviewer – AI Career Coach

A production-grade, enterprise-ready full-stack AI career acceleration platform that helps students, freshers, and experienced software engineers prepare for high-stakes technical interviews, optimize resumes for ATS parsing compliance, practice technical topics with sandboxed code execution, simulate realistic mock interviews with video & audio analytics, and follow personalized dynamic career roadmaps.

---

## 🔒 Strictly Non-OpenAI AI Architecture

This platform strictly adheres to an open-source, local-first artificial intelligence hierarchy. It **does not require or use OpenAI proprietary APIs**:

```
+-------------------------------------------------------------+
| 1. Ollama (Primary Provider)                                |
|    Endpoint: http://localhost:11434/api/generate            |
|    Models: qwen2.5:7b -> llama3.1:8b -> mistral:7b          |
+------------------------------+------------------------------+
                               | (If offline or unavailable)
                               v
+-------------------------------------------------------------+
| 2. LM Studio (Secondary Local Provider)                     |
|    Endpoint: http://localhost:1234/v1                       |
+------------------------------+------------------------------+
                               | (If unconfigured or offline)
                               v
+-------------------------------------------------------------+
| 3. Hugging Face Inference API (Open Remote Router)          |
|    Open-weight model endpoints                              |
+------------------------------+------------------------------+
                               | (If unconfigured or offline)
                               v
+-------------------------------------------------------------+
| 4. Groq Ultra-Fast LPU Inference (Open Source Fallback)     |
|    Models: llama-3.3-70b-versatile, mixtral-8x7b-32768      |
+------------------------------+------------------------------+
                               | (If all network/APIs offline)
                               v
+-------------------------------------------------------------+
| 5. Deterministic Rule-Based Fallback Engine                 |
|    Zero-downtime, fully transparent heuristic grading       |
|    Explicitly labeled in UI: [Rule-Based Fallback Engine]   |
+-------------------------------------------------------------+
```

---

## 📂 Canonical Project Structure

```
virtual-ai-interviewer/
│
├── frontend/                          # React 19 + TypeScript + Vite + Tailwind CSS
│   ├── src/
│   │   ├── components/                # Modular UI components (Navbar, Sidebar, Charts, Cards)
│   │   ├── pages/                     # 10 full-featured SaaS view pages
│   │   │   ├── Dashboard.tsx          # Real-time metrics, radar chart, progression
│   │   │   ├── ResumeAnalyzer.tsx     # ATS scoring, keyword match, section audits
│   │   │   ├── ResumeBuilder.tsx      # Role-based AI resume generator (12 roles)
│   │   │   ├── JobMatcher.tsx         # Job description gap analysis & match report
│   │   │   ├── TechnicalPractice.tsx  # 14 CS subjects, MCQs, theory, sandboxed code
│   │   │   ├── MockInterview.tsx      # Webcam/mic recording, TTS, Whisper speech analytics
│   │   │   ├── CareerRoadmap.tsx      # Dynamic phase blueprints, checklists, daily plans
│   │   │   ├── MyProgress.tsx         # Comprehensive historical learning analytics
│   │   │   ├── InterviewHistory.tsx   # Past session transcripts and audio playback
│   │   │   ├── Settings.tsx           # AI engine preference & account settings
│   │   │   ├── Login.tsx              # Secure JWT authentication
│   │   │   └── Register.tsx           # User account registration
│   │   ├── layouts/                   # MainLayout, Sidebar navigation, Header
│   │   ├── hooks/                     # Custom hooks (useAuth, useTheme, useToast, useMediaRecorder)
│   │   ├── services/                  # Frontend API services (auth, resume, interview, practice, roadmap)
│   │   ├── types/                     # TypeScript schema declarations
│   │   ├── utils/                     # Formatting, validation, and styling helpers
│   │   ├── App.tsx                    # Route definitions and authenticated providers
│   │   └── main.tsx                   # React DOM entry point
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
│
├── backend/                           # FastAPI + SQLAlchemy + SQLite
│   ├── main.py                        # Top-level ASGI entry point
│   ├── config.py                      # Global configuration & environment settings
│   ├── database/
│   │   ├── db.py                      # SQLite database engine & sessionmaker factory
│   │   └── models.py                  # All 8 Section 11 SQLAlchemy models
│   ├── schemas/                       # Pydantic schemas for request/response validation
│   ├── routers/                       # Modular FastAPI API route controllers
│   │   ├── auth.py                    # User registration, login, logout, profile
│   │   ├── dashboard.py               # Aggregated metrics, charts, weak skills
│   │   ├── resume.py                  # Resume parsing, ATS scoring, role builder, exports
│   │   ├── interview.py               # Mock interviews, webcam recordings, question flow
│   │   ├── roadmap.py                 # Dynamic roadmaps, study plans, task tracking
│   │   └── progress.py                # Historical trends, score averages, radar data
│   ├── services/                      # Enterprise domain logic services
│   │   ├── ai_service.py              # Modular AI orchestrator with priority chain
│   │   ├── ollama_service.py          # Local Ollama REST client & auto-model selector
│   │   ├── lmstudio_service.py        # LM Studio local client
│   │   ├── huggingface_service.py     # Hugging Face inference provider
│   │   ├── groq_service.py            # Groq LPU inference provider
│   │   ├── ats_service.py             # Dedicated ATS audit and JD match engine
│   │   ├── resume_service.py          # Resume parsing, role optimizer, PDF/DOCX generator
│   │   ├── question_service.py        # Question bank retrieval, uniqueness, safe code sandbox
│   │   ├── evaluation_service.py      # Multi-dimensional interview answer scoring
│   │   ├── transcription_service.py   # Whisper STT & speech communication metrics
│   │   └── roadmap_service.py         # Career roadmaps & progress recalculator
│   └── tests/                         # Automated unit & integration test suites
│       ├── test_ai_hierarchy.py       # AI provider priority & fallback tests
│       ├── test_security.py           # Password hashing, token revocation, magic bytes, sandbox
│       ├── test_database.py           # 8 models schema & user data isolation tests
│       ├── test_resume.py             # ATS scoring, structured parsing, PDF/DOCX exports
│       ├── test_practice.py           # Metadata, question bank, Python code sandbox
│       ├── test_interview.py          # Communication metrics (WPM, fillers, STAR), scoring
│       ├── test_roadmap.py            # Dynamic roadmaps & daily study plan generation
│       └── test_all.py                # Consolidated test discovery runner
│
├── storage/                           # Private isolated file storage
│   ├── resumes/                       # Uploaded candidate resumes (PDF/DOCX)
│   ├── recordings/                    # Webcam video/audio recordings (user-isolated)
│   ├── reports/                       # Generated interview & evaluation PDF reports
│   └── generated_resumes/             # Exported role-tailored PDF & DOCX resumes
│
├── README.md                          # Comprehensive project documentation
├── .env.example                       # Documented environment template
└── requirements.txt                   # Complete Python backend dependencies
```

---

## 🚀 Key Modules & Capabilities

### 1. Module 1: Resume Analyzer & ATS Audit
- **Multi-Format Ingestion**: Authenticates and parses PDF and DOCX files.
- **ATS Scoring Engine**: Evaluates keyword density, section completeness, readability metrics, and quantifiable impact bullets.
- **1-Click Corrections**: AI-generated and heuristic suggestions for replacing passive language with action verbs.

### 2. Module 2: Role-Based AI Resume Builder
- **12 Supported Target Roles**: Software Development Engineer, AI/ML Engineer, Data Scientist, Data Analyst, Python Developer, Java Developer, Full Stack Developer, Backend Developer, Frontend Developer, Cybersecurity Engineer, Cloud Engineer, DevOps Engineer.
- **Truth Preservation Guarantee**: Strictly forbids hallucination or fabrication of credentials.
- **Dual Formats**: Generates downloadable machine-parseable PDF (ReportLab) and DOCX (python-docx).

### 3. Module 3: Job Description Matcher
- **Deep Alignment Engine**: Compares resumes against job postings using TF-IDF cosine similarity and skill taxonomies.
- **Gap Categorization**: Identifies missing skills categorized into *Languages*, *Frameworks*, *Databases*, and *DevOps/Cloud* with priority indicators.

### 4. Module 4: AI Technical Interview Practice
- **14 CS Subjects**: Data Structures & Algorithms, Java, Python, C++, Operating Systems, DBMS, Computer Networks, Artificial Intelligence, Machine Learning, Deep Learning, SQL, System Design, OOP, Computer Science Fundamentals.
- **Interactive Practice Modes**: MCQs, Theoretical questions, and Coding questions.
- **Isolated Code Sandbox**: Subprocess execution sandbox with AST security inspection, blocking filesystem access, shell escapes, and infinite loops.

### 5. Module 5: Virtual AI Mock Interview
- **Webcam & Audio Interface**: Candidate media recording via `getUserMedia()` and `MediaRecorder` API with private local storage.
- **Adaptive AI Interviewer**: Follow-up question generation based on prior answers and dynamic difficulty scaling.
- **Speech Analytics**: Words per minute (WPM), filler word distribution, repetition detection, pauses count, and STAR structure detection.
- **Ethical Safeguard**: Explicitly refrains from claiming facial deception or emotional detection.

### 6. Module 6: Dynamic Career Roadmap
- **Customized Learning Plans**: Multi-phase trajectories tailored to target roles, daily study hours, and current skill levels.
- **Actionable Tracking**: Daily schedules, weekly targets, monthly milestones, and interactive checklist progress calculation.

### 7. Module 7: Analytics & My Progress
- **Historical Tracking**: Radar competency graphs, score trends, ATS gains, and topic-wise breakdown.

---

## 🛡️ Enterprise Security Implementations (Section 13)

1. **Password Hashing**: Argon2id primary encryption with PBKDF2 fallback and policy enforcement ($\ge 8$ chars, $\ge 1$ digit, $\ge 1$ letter). Plaintext passwords are never stored.
2. **JWT Authentication & Revocation**: Signed bearer tokens with in-memory revocation blacklist on logout.
3. **Strict User Data Isolation**: Database queries enforce `user_id == current_user.id`. Cross-user access returns HTTP 404.
4. **Magic Byte Verification**: Authenticates PDF (`%PDF-`), DOCX (`PK\x03\x04`), and media formats (WebM, MP4, WAV, OGG).
5. **File Size Enforcement**: 10 MB ceiling for resumes, 50 MB ceiling for media recordings.
6. **Defensive Document Parsing**: Defends against zip bombs (uncompressed ratio $>50:1$) and path traversal (`..`).
7. **Recording Consent Requirement**: Explicit user consent verified before recording upload (`HTTP 403` when denied).
8. **Secure Forensic File Deletion**: DoD-compliant random-byte overwrite before file unlinking.
9. **AST Code Execution Sandbox**: Blocks `eval`, `exec`, `os`, `subprocess`, `sys`, and dunder attribute introspection.

---

## ⚡ Quick Start Guide

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher & npm

### 1. Backend Setup
```powershell
# Navigate to backend directory
cd backend

# Create and activate virtual environment (optional but recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r ..\requirements.txt

# Run database migrations and seed question bank
python -c "import sys; sys.path.insert(0, '.'); from app.database import engine, Base; from app.services.seed_service import seed_initial_data; Base.metadata.create_all(bind=engine); from app.database import SessionLocal; db = SessionLocal(); seed_initial_data(db); db.close()"

# Start FastAPI server
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive API Documentation will be available at: `http://127.0.0.1:8000/docs`.

### 2. Frontend Setup
```powershell
# Navigate to frontend directory
cd frontend

# Install npm dependencies
npm install

# Start Vite development server
npm run dev
```
Open your browser at `http://localhost:5173`.

### 3. (Optional) Run Ollama Locally
```powershell
# Install Ollama on Windows
winget install Ollama.Ollama

# Pull preferred open-source model
ollama run llama3.1:8b
```
*(If Ollama is not running, the application seamlessly operates via LM Studio, Hugging Face, Groq, or the built-in deterministic heuristic fallback engine).*

---

## 🧪 Automated Test Verification

Run all unit and integration tests across all modules:

```powershell
# Run consolidated master test suite
python backend/tests/test_all.py
```

Expected output:
```
Total Tests Run: 23
Errors: 0
Failures: 0
Success: True
```

Run specific module security audit:
```powershell
python backend/test_module13_security.py
```
Expected output:
```
ALL 14 SECTION 13 SECURITY AUDIT CHECKS PASSED 100%!
```

Run frontend production build verification:
```powershell
npm --prefix frontend run build
```
Expected output:
```
✓ built in ~1.5s
```
