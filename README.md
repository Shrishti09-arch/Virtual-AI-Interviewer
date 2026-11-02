# AI-Powered Virtual Interviewer

A web platform that helps students and early-career engineers prepare for technical interviews.
It combines resume analysis, resume building, job matching, technical practice, a webcam mock
interview, a career roadmap and a progress dashboard in one application.

**Project by:** Shrishti Vaishnav and Divyansh Pandey, MITS Gwalior
**Category:** Artificial Intelligence & Machine Learning Systems (July-Dec 2026)

## Features

| Module | What it does |
| --- | --- |
| Resume Analyzer | Reads PDF or DOCX resumes and gives an ATS score with section-wise fixes |
| Resume Builder | Creates a role-specific resume for 12 roles and exports PDF or DOCX, using only the user's own facts |
| Job Matcher | Compares a resume with a job description (TF-IDF cosine similarity) and lists missing skills |
| Technical Practice | Multiple-choice, theory and coding questions in 14 subjects, with a safe code sandbox |
| Mock Interview | Webcam and microphone interview with follow-up questions, speaking pace, filler words, pauses and STAR analysis |
| Career Roadmap | Phased study plan with tasks and daily schedule |
| Progress Dashboard | Scores, trends, skill radar and weak topics |

## How the AI works

The app tries AI providers in this order and uses the first one that responds:

1. Ollama (local)
2. LM Studio (local)
3. Hugging Face (cloud)
4. Groq (cloud)
5. Built-in rule-based engine (always available)

So every feature keeps working with no internet and no AI model installed. The header of the
app shows which engine produced the feedback.

## Tech stack

- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS, Recharts, React Router, Axios
- **Backend:** Python, FastAPI, SQLAlchemy, SQLite, Pydantic
- **Security:** Argon2, JWT, defusedxml
- **Documents and matching:** pypdf, python-docx, ReportLab, scikit-learn
- **Testing:** Pytest (47 tests)

## Run it locally

Requirements: Python 3.10+, Node.js 20+, Chrome or Edge.

**Backend** (Windows PowerShell; on Linux or macOS use `source venv/bin/activate`)

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

API documentation: http://127.0.0.1:8000/docs

**Frontend** (a second terminal)

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 and click **Instant 1-Click Demo Login**, or sign up.
Passwords need at least 8 characters, one letter and one digit.

## Optional settings

Settings are read from environment variables (not from a `.env` file). Example for a Groq key:

```powershell
$env:GROQ_API_KEY = "your-key"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

To load a file instead: `python -m uvicorn app.main:app --env-file ..\.env`.
See `.env.example` for all variables. For local models, install Ollama and run
`ollama pull llama3.1:8b`. Change `SECRET_KEY` for any real deployment.

## Tests

```powershell
cd backend
python -m pytest tests -q
```

Expected result: `47 passed`. A saved run is in `TEST_REPORT.txt`.

## Security

- Passwords hashed with Argon2; password rules enforced
- Signed JWT sessions, revoked on logout
- Every record belongs to one user and is filtered by owner
- Uploads checked by real file signature and size (resume 10 MB, recording 50 MB)
- Recording needs explicit consent; deleted files are overwritten before removal
- Submitted code is inspected before running and blocked from files, shell and system access

## Project structure

```
backend/
  app/
    routers/     API endpoints (52 in total)
    services/    business logic, code sandbox, AI provider manager
    models/      database tables (15)
    schemas/     request and response models
    core/        security functions
  tests/         47 automated tests
frontend/
  src/           pages, components, hooks, services
storage/         private uploads and recordings
requirements.txt Python dependencies
```

## Limitations

- Feedback quality depends on the AI model; the rule-based fallback is simpler.
- SQLite suits a single user or a small group.
- The ATS score is an estimate, not what every hiring system will compute.
- The system does not detect emotions or lying from the face.
- Not load-tested with many users.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `python` not recognized | Reinstall Python with "Add to PATH", or use `py` |
| PowerShell blocks `activate` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Blank page or network error | Start the backend and check http://127.0.0.1:8000/docs |
| Port already in use | Close old terminals or use `--port 8001` |
| Camera does not start | Allow camera and microphone in the browser |
