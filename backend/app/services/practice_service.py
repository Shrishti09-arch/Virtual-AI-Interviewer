import json
import logging
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.practice import QuestionBank, PracticeSession, UserQuestionHistory
from app.services.ai.manager import ai_manager
from app.services.sandbox_executor import sandbox_executor

logger = logging.getLogger(__name__)

SUPPORTED_SUBJECTS = [
    "Data Structures and Algorithms",
    "Java",
    "Python",
    "C++",
    "Operating Systems",
    "DBMS",
    "Computer Networks",
    "Artificial Intelligence",
    "Machine Learning",
    "Deep Learning",
    "SQL",
    "System Design",
    "OOP",
    "Computer Science Fundamentals"
]

SUPPORTED_DIFFICULTIES = ["Beginner", "Intermediate", "Advanced", "Expert"]

SUPPORTED_INTERVIEW_TYPES = [
    "Comprehensive Mixed",
    "MCQs",
    "Coding questions",
    "Theoretical questions",
    "Scenario-based questions",
    "Problem-solving questions",
    "Company-level questions",
    "Real-world technical questions"
]

class PracticeService:
    """
    Intelligent question selection, AI generation, duplicate detection,
    interactive session management, and performance analytics.
    """

    def get_supported_metadata(self) -> Dict[str, Any]:
        return {
            "subjects": SUPPORTED_SUBJECTS,
            "difficulties": SUPPORTED_DIFFICULTIES,
            "interview_types": SUPPORTED_INTERVIEW_TYPES,
            "languages": ["Python", "Java", "C++", "SQL", "JavaScript", "Go"]
        }

    def start_session(
        self,
        db: Session,
        user_id: int,
        job_role: str,
        subject: str,
        programming_language: str,
        difficulty: str,
        total_questions: int,
        interview_type: str,
        user_llm_provider: Optional[str] = None,
        api_key: Optional[str] = None,
        ollama_endpoint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Starts an interactive practice session with unique, non-repeating questions
        selected or dynamically generated for the user.
        """
        # Fetch question IDs already attempted by this user
        attempted_qids = {
            row[0] for row in db.query(UserQuestionHistory.question_id).filter(
                UserQuestionHistory.user_id == user_id
            ).all()
        }

        # Query eligible questions matching subject
        query = db.query(QuestionBank)
        if subject and subject != "All":
            query = query.filter(QuestionBank.subject == subject)

        # Filter by interview type if specific
        type_mapping = {
            "MCQs": "MCQ",
            "Coding questions": "Coding",
            "Theoretical questions": "Theory",
            "Scenario-based questions": "Scenario",
            "Problem-solving questions": "Problem-Solving",
            "Company-level questions": "Company-Level",
            "Real-world technical questions": "Real-World"
        }
        target_type = type_mapping.get(interview_type)
        if target_type:
            query = query.filter(QuestionBank.question_type == target_type)

        all_candidates = query.all()

        # Prioritize unattempted questions
        unattempted = [q for q in all_candidates if q.id not in attempted_qids]
        selected_questions = unattempted[:total_questions]

        # If not enough unattempted questions, try generating fresh ones with AI if available
        needed = total_questions - len(selected_questions)
        if needed > 0:
            ai_questions = self._try_generate_ai_questions(
                db=db,
                needed_count=needed,
                job_role=job_role,
                subject=subject,
                programming_language=programming_language,
                difficulty=difficulty,
                interview_type=interview_type,
                user_llm_provider=user_llm_provider,
                api_key=api_key,
                ollama_endpoint=ollama_endpoint
            )
            selected_questions.extend(ai_questions)

        # If still needed, fill from candidate questions (least recent)
        if len(selected_questions) < total_questions and all_candidates:
            for q in all_candidates:
                if q not in selected_questions:
                    selected_questions.append(q)
                if len(selected_questions) >= total_questions:
                    break

        # Fallback to any general questions in database if subject was empty
        if not selected_questions:
            selected_questions = db.query(QuestionBank).limit(total_questions).all()

        question_ids = [q.id for q in selected_questions]

        # Record in history to track uniqueness
        for qid in question_ids:
            hist_entry = UserQuestionHistory(user_id=user_id, question_id=qid)
            db.add(hist_entry)

        # Create session record
        session = PracticeSession(
            user_id=user_id,
            job_role=job_role,
            subject=subject,
            programming_language=programming_language,
            difficulty=difficulty,
            interview_type=interview_type,
            total_questions=len(question_ids),
            current_index=0,
            is_completed=False,
            question_ids=question_ids,
            answers=[]
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        first_q = self.format_active_question(selected_questions[0], 0, len(question_ids)) if selected_questions else None

        return {
            "session_id": session.id,
            "job_role": session.job_role,
            "subject": session.subject,
            "programming_language": session.programming_language,
            "difficulty": session.difficulty,
            "interview_type": session.interview_type,
            "total_questions": session.total_questions,
            "current_index": 0,
            "is_completed": False,
            "active_question": first_q
        }

    def _try_generate_ai_questions(
        self,
        db: Session,
        needed_count: int,
        job_role: str,
        subject: str,
        programming_language: str,
        difficulty: str,
        interview_type: str,
        user_llm_provider: Optional[str],
        api_key: Optional[str],
        ollama_endpoint: Optional[str]
    ) -> List[QuestionBank]:
        """
        Dynamically generates structured, non-duplicate technical questions using
        active AI provider (Ollama / Groq / etc.) with fallback protection.
        """
        generated = []
        q_type = "MCQ" if "MCQ" in interview_type else ("Coding" if "Coding" in interview_type else "Theory")

        prompt = f"""Generate {needed_count} distinct, high-quality technical interview questions for:
Role: {job_role}
Subject: {subject}
Language: {programming_language}
Difficulty: {difficulty}
Question Type: {q_type}

Return ONLY a JSON array with objects formatted as:
[
  {{
    "title": "Clear concise question title",
    "question_text": "Detailed technical problem statement or question",
    "question_type": "{q_type}",
    "options": ["Option A", "Option B", "Option C", "Option D"] (empty if not MCQ),
    "correct_option_index": 0 (0-3 for MCQ, null otherwise),
    "explanation": "Detailed explanation of correct answer and underlying principles",
    "sample_answer": "Complete ideal solution or architectural explanation",
    "expected_keywords": ["keyword1", "keyword2", "keyword3"],
    "hints": ["Hint 1", "Hint 2"],
    "code_template": "Starter code stub if coding, else empty string",
    "test_cases": []
  }}
]
"""
        output = ai_manager.generate_structured(
            prompt=prompt,
            system_prompt="You are an expert technical interviewer and computer science examiner. Output valid JSON only.",
            preferred_provider=user_llm_provider,
            user_config={"groq_api_key": api_key, "ollama_endpoint": ollama_endpoint}
        )
        response_text = output.raw_text or ""
        provider = output.provider_used
        model = output.model_used

        try:
            # Parse JSON from AI response
            cleaned = response_text.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()

            items = json.loads(cleaned)
            if isinstance(items, list):
                for item in items:
                    title = item.get("title", "").strip()
                    if not title:
                        continue

                    # Duplicate detection: check if title or semantic content is already in DB
                    existing = db.query(QuestionBank).filter(QuestionBank.title == title).first()
                    if existing:
                        continue

                    new_q = QuestionBank(
                        category="DSA" if subject in ["Data Structures and Algorithms", "Computer Science Fundamentals"] else "Backend",
                        subject=subject,
                        difficulty=difficulty,
                        role_track=job_role,
                        programming_language=programming_language,
                        question_type=item.get("question_type", q_type),
                        title=title,
                        question_text=item.get("question_text", ""),
                        expected_keywords=item.get("expected_keywords", []),
                        sample_answer=item.get("sample_answer", ""),
                        hints=item.get("hints", []),
                        options=item.get("options", []),
                        correct_option_index=item.get("correct_option_index"),
                        explanation=item.get("explanation", ""),
                        code_template=item.get("code_template", ""),
                        test_cases=item.get("test_cases", []),
                        source_type="ai_generated",
                        source_name=f"Ollama ({model or 'local'})",
                        source_url=None
                    )
                    db.add(new_q)
                    db.commit()
                    db.refresh(new_q)
                    generated.append(new_q)
        except Exception as e:
            logger.warning(f"AI question generation parsing failed: {e}. Utilizing curated standard questions.")

        return generated

    def format_active_question(self, q: QuestionBank, index: int, total: int) -> Dict[str, Any]:
        """
        Formats question for user display, masking correct answers and hidden test cases.
        """
        masked_test_cases = []
        for tc in (q.test_cases or []):
            if tc.get("hidden", False):
                masked_test_cases.append({
                    "input": "[Hidden Test Case]",
                    "expected_output": "[Hidden]",
                    "hidden": True
                })
            else:
                masked_test_cases.append(tc)

        return {
            "id": q.id,
            "index": index + 1,
            "total": total,
            "title": q.title,
            "question_text": q.question_text,
            "subject": q.subject,
            "difficulty": q.difficulty,
            "programming_language": q.programming_language,
            "question_type": q.question_type,
            "options": q.options or [],
            "code_template": q.code_template or "",
            "hints": q.hints or [],
            "test_cases": masked_test_cases,
            "source_type": q.source_type,
            "source_name": q.source_name,
            "source_url": q.source_url
        }

    def submit_answer(
        self,
        db: Session,
        session_id: int,
        user_id: int,
        question_id: int,
        answer_payload: Dict[str, Any],
        user_llm_provider: Optional[str] = None,
        api_key: Optional[str] = None,
        ollama_endpoint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluates candidate answer (MCQ, Coding, or Theory), records progress,
        and returns next question or final performance report.
        """
        session = db.query(PracticeSession).filter(
            PracticeSession.id == session_id,
            PracticeSession.user_id == user_id
        ).first()

        if not session:
            raise ValueError("Practice session not found.")

        question = db.query(QuestionBank).filter(QuestionBank.id == question_id).first()
        if not question:
            raise ValueError("Question not found.")

        q_type = question.question_type or "Theory"
        evaluation: Dict[str, Any] = {}

        if q_type == "MCQ":
            selected_idx = answer_payload.get("selected_option_index")
            correct_idx = question.correct_option_index
            is_correct = (selected_idx is not None and selected_idx == correct_idx)
            score = 100.0 if is_correct else 0.0

            evaluation = {
                "question_id": question.id,
                "question_type": "MCQ",
                "title": question.title,
                "subject": question.subject,
                "is_correct": is_correct,
                "score": score,
                "selected_option_index": selected_idx,
                "correct_option_index": correct_idx,
                "explanation": question.explanation or "Correct option chosen.",
                "sample_answer": question.sample_answer
            }

        elif q_type == "Coding":
            code = answer_payload.get("code", "")
            language = answer_payload.get("language") or question.programming_language or "python"
            sandbox_res = sandbox_executor.execute(language, code, question.test_cases or [])
            passed_tests = sandbox_res.get("passed_tests", 0)
            total_tests = sandbox_res.get("total_tests", 1) or 1
            score = round((passed_tests / total_tests) * 100.0, 1)

            evaluation = {
                "question_id": question.id,
                "question_type": "Coding",
                "title": question.title,
                "subject": question.subject,
                "score": score,
                "is_correct": (score == 100.0),
                "status": sandbox_res.get("status", "Evaluated"),
                "passed_tests": passed_tests,
                "total_tests": total_tests,
                "test_results": sandbox_res.get("test_results", []),
                "error": sandbox_res.get("error"),
                "sample_answer": question.sample_answer,
                "code_submitted": code
            }

        else: # Theory, Scenario, Problem-Solving, Company-Level, Real-World
            user_text = answer_payload.get("user_answer", "").strip()
            eval_res = self._evaluate_theory_answer(
                question=question,
                user_answer=user_text,
                user_llm_provider=user_llm_provider,
                api_key=api_key,
                ollama_endpoint=ollama_endpoint
            )
            evaluation = {
                "question_id": question.id,
                "question_type": q_type,
                "title": question.title,
                "subject": question.subject,
                "score": eval_res["score"],
                "is_correct": (eval_res["score"] >= 70.0),
                "feedback": eval_res["feedback"],
                "strengths": eval_res.get("strengths", []),
                "missing_concepts": eval_res.get("missing_concepts", []),
                "ideal_answer": question.sample_answer,
                "improvement_suggestions": eval_res.get("improvement_suggestions", "Review core fundamentals.")
            }

        # Update session answers
        current_answers = list(session.answers or [])
        current_answers.append(evaluation)
        session.answers = current_answers
        session.current_index += 1

        is_finished = session.current_index >= session.total_questions
        next_question = None
        final_report = None

        if is_finished:
            session.is_completed = True
            final_report = self._compute_final_report(session)
            session.correct_count = final_report["correct_count"]
            session.incorrect_count = final_report["incorrect_count"]
            session.accuracy = final_report["accuracy"]
            session.topic_performance = final_report["topic_performance"]
            session.weak_areas = final_report["weak_areas"]
            session.recommended_topics = final_report["recommended_topics"]
        else:
            next_qid = session.question_ids[session.current_index]
            next_q_model = db.query(QuestionBank).filter(QuestionBank.id == next_qid).first()
            if next_q_model:
                next_question = self.format_active_question(next_q_model, session.current_index, session.total_questions)

        db.commit()
        db.refresh(session)

        return {
            "evaluation": evaluation,
            "current_index": session.current_index,
            "total_questions": session.total_questions,
            "is_completed": is_finished,
            "next_question": next_question,
            "final_report": final_report
        }

    def _evaluate_theory_answer(
        self,
        question: QuestionBank,
        user_answer: str,
        user_llm_provider: Optional[str],
        api_key: Optional[str],
        ollama_endpoint: Optional[str]
    ) -> Dict[str, Any]:
        """Evaluates free-form theoretical answers using AI or rule-based fallback."""
        if not user_answer:
            return {
                "score": 0.0,
                "feedback": "No answer provided.",
                "strengths": [],
                "missing_concepts": question.expected_keywords or ["Core principles"],
                "improvement_suggestions": "Provide an explanation covering key concepts."
            }

        prompt = f"""Evaluate this candidate's technical interview answer:
Question: {question.question_text}
Expected Keywords / Concepts: {', '.join(question.expected_keywords or [])}
Model Answer: {question.sample_answer}
Candidate's Answer: {user_answer}

Return ONLY a JSON object:
{{
  "score": (float between 0 and 100),
  "feedback": "Constructive evaluation of the answer",
  "strengths": ["Strong point 1", "Strong point 2"],
  "missing_concepts": ["Missing concept 1", "Missing concept 2"],
  "improvement_suggestions": "Actionable guidance to improve answer depth"
}}
"""
        output = ai_manager.generate_structured(
            prompt=prompt,
            system_prompt="You are a strict, objective senior technical interviewer. Return JSON only.",
            preferred_provider=user_llm_provider,
            user_config={"groq_api_key": api_key, "ollama_endpoint": ollama_endpoint}
        )
        if output.structured_data and isinstance(output.structured_data, dict) and "score" in output.structured_data:
            eval_data = output.structured_data
            eval_data["is_fallback"] = output.is_fallback
            eval_data["provider_used"] = output.provider_used
            eval_data["model_used"] = output.model_used
            return eval_data

        response_text = output.raw_text or ""

        try:
            cleaned = response_text.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()
            return json.loads(cleaned)
        except Exception:
            # Rule-based fallback calculation
            keywords = question.expected_keywords or []
            matched = [kw for kw in keywords if kw.lower() in user_answer.lower()]
            missing = [kw for kw in keywords if kw.lower() not in user_answer.lower()]
            length_bonus = min(20.0, len(user_answer.split()) * 0.3)
            base_score = (len(matched) / max(len(keywords), 1)) * 80.0
            score = round(min(100.0, base_score + length_bonus), 1)

            return {
                "score": score,
                "feedback": f"Candidate covered {len(matched)} of {len(keywords)} key concepts: {', '.join(matched) if matched else 'None'}.",
                "strengths": [f"Addressed {kw}" for kw in matched] if matched else ["Attempted answer"],
                "missing_concepts": missing or ["Deep architectural nuances"],
                "improvement_suggestions": f"Incorporate missing foundational concepts: {', '.join(missing[:3])}."
            }

    def _compute_final_report(self, session: PracticeSession) -> Dict[str, Any]:
        """Calculates final performance metrics, topic breakdown, and recommendations."""
        answers = session.answers or []
        total = len(answers)
        correct_count = sum(1 for a in answers if a.get("score", 0) >= 70.0)
        incorrect_count = total - correct_count
        accuracy = round((correct_count / total * 100.0), 1) if total > 0 else 0.0

        # Topic breakdown
        topic_map: Dict[str, Dict[str, Any]] = {}
        weak_areas = []

        for a in answers:
            subject = a.get("subject") or session.subject or "Computer Science"
            if subject not in topic_map:
                topic_map[subject] = {"total": 0, "correct": 0, "scores": []}
            topic_map[subject]["total"] += 1
            topic_map[subject]["scores"].append(a.get("score", 0))
            if a.get("score", 0) >= 70.0:
                topic_map[subject]["correct"] += 1
            else:
                title = a.get("title", "")
                if title and title not in weak_areas:
                    weak_areas.append(f"{subject}: {title}")

        topic_performance = {}
        for subj, data in topic_map.items():
            avg_score = round(sum(data["scores"]) / max(len(data["scores"]), 1), 1)
            topic_performance[subj] = {
                "total": data["total"],
                "correct": data["correct"],
                "average_score": avg_score
            }

        # Recommendations
        recommended = []
        if accuracy < 60.0:
            recommended.append("Revisit core data structures, time complexity analysis, and problem-solving patterns.")
        if any("SQL" in str(w) for w in weak_areas):
            recommended.append("Practice advanced SQL grouping, window functions (ROW_NUMBER, DENSE_RANK), and query optimization.")
        if any("System Design" in str(w) for w in weak_areas):
            recommended.append("Study distributed systems patterns: caching, message queues, horizontal scaling, and sharding.")
        if any("Operating Systems" in str(w) for w in weak_areas):
            recommended.append("Review virtual memory paging, process scheduling, concurrency locks, and Coffman deadlock conditions.")
        if not recommended:
            recommended.append(f"Advance to Expert-level mock interview challenges in {session.subject}.")

        return {
            "session_id": session.id,
            "job_role": session.job_role,
            "subject": session.subject,
            "programming_language": session.programming_language,
            "difficulty": session.difficulty,
            "total_questions": total,
            "correct_count": correct_count,
            "incorrect_count": incorrect_count,
            "accuracy": accuracy,
            "topic_performance": topic_performance,
            "weak_areas": weak_areas,
            "recommended_topics": recommended,
            "answers_review": answers
        }

    def get_session_report(self, db: Session, session_id: int, user_id: int) -> Dict[str, Any]:
        """Fetches final performance report for a practice session."""
        session = db.query(PracticeSession).filter(
            PracticeSession.id == session_id,
            PracticeSession.user_id == user_id
        ).first()

        if not session:
            raise ValueError("Practice session not found.")

        return self._compute_final_report(session)

practice_service = PracticeService()
