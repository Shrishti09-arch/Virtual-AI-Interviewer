import io
import json
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.services.ai.manager import ai_manager
from app.services.ai.schemas import InterviewAnswerEvaluation

logger = logging.getLogger(__name__)

FILLER_WORDS = [
    "um", "uh", "like", "actually", "basically", "you know", "literally",
    "sort of", "kind of", "i mean", "right", "so yeah", "honestly", "well"
]

STAR_MARKERS = {
    "situation": ["when i was", "at my previous", "in my last role", "we were facing", "the challenge was", "our team had", "the problem was", "a situation where"],
    "task": ["my responsibility was", "i was tasked with", "my goal was", "we needed to", "the objective was", "i had to", "the requirement was"],
    "action": ["i decided to", "i implemented", "i designed", "i architected", "i refactored", "i coordinated", "i developed", "we migrated", "i initiated", "i built"],
    "result": ["as a result", "consequently", "resulting in", "increased by", "reduced by", "improved", "successfully delivered", "saved", "achieved", "the outcome was", "impact was"]
}

COMPANY_PROFILES = {
    "amazon": {
        "focus": "Customer Obsession, Ownership, Bias for Action, Dive Deep, and Scalable Distributed Systems.",
        "principles": ["Customer Obsession", "Ownership", "Invent and Simplify", "Bias for Action", "Earn Trust"]
    },
    "google": {
        "focus": "Algorithmic Efficiency, System Scalability, High Concurrency, Googleyness, and Data-Driven Architecture.",
        "principles": ["Scale to Billions", "Analytical Rigor", "Open Communication", "Googleyness"]
    },
    "meta": {
        "focus": "Move Fast, High-Throughput Microservices, Real-Time Streaming, Pragmatic Trade-offs.",
        "principles": ["Move Fast", "Focus on Long-Term Impact", "Build Awesome Things"]
    },
    "microsoft": {
        "focus": "Enterprise Reliability, Growth Mindset, Cloud Architecture (Azure), Maintainable OOP.",
        "principles": ["Growth Mindset", "Customer Empathy", "One Microsoft"]
    }
}

class InterviewService:
    """
    Core engine powering AI Mock Interviews: dynamic adaptive questions,
    speech/communication analytics, multi-dimensional answer evaluation,
    and executive PDF reporting.
    """

    @classmethod
    def get_initial_questions(
        cls,
        role_title: str,
        experience_level: str,
        interview_type: str,
        difficulty: str = "Intermediate",
        technical_subjects: Optional[List[str]] = None,
        target_company: Optional[str] = None,
        total_questions: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generates initial structured question sequence starting with interviewer introduction,
        role-specific technical problem, and scenario challenge.
        """
        subjects_str = ", ".join(technical_subjects) if technical_subjects else "System Design and Algorithms"
        company_note = f" (Tailored for {target_company})" if target_company else ""

        questions = [
            # 1. Introduction & Icebreaker Question
            {
                "question_order": 1,
                "category": "Introduction & Professional Overview",
                "is_follow_up": False,
                "difficulty_level": difficulty,
                "question": f"Hello and welcome! I am your AI Technical Interviewer today. We are conducting a {difficulty} {interview_type} mock interview for the {role_title} position{company_note}. To start, please introduce yourself, highlight your core technical stack ({subjects_str}), and walk me through a major engineering project you built or led."
            },
            # 2. Core Role-Specific Technical Question
            {
                "question_order": 2,
                "category": f"Core {role_title} Engineering",
                "is_follow_up": False,
                "difficulty_level": difficulty,
                "question": cls._get_role_technical_question(role_title, subjects_str, difficulty)
            },
            # 3. System Design & Scenario Question
            {
                "question_order": 3,
                "category": "System Architecture & Scalability",
                "is_follow_up": False,
                "difficulty_level": difficulty,
                "question": cls._get_scenario_question(role_title, difficulty, target_company)
            },
            # 4. Behavioral / Leadership / STAR Question
            {
                "question_order": 4,
                "category": "Behavioral Leadership (STAR)",
                "is_follow_up": False,
                "difficulty_level": difficulty,
                "question": "Tell me about a high-stakes technical disagreement or production outage you navigated. How did you diagnose the root cause, communicate with stakeholders, and establish preventive safeguards?"
            },
            # 5. Advanced Trade-off & Synthesis Question
            {
                "question_order": 5,
                "category": "Technical Trade-offs & Engineering Synthesis",
                "is_follow_up": False,
                "difficulty_level": difficulty,
                "question": f"In your experience as a {role_title}, what is the most challenging technical tradeoff you had to make (e.g. consistency vs availability, speed vs tech debt, or build vs buy)? What was your decision framework?"
            }
        ]

        return questions[:total_questions]

    @staticmethod
    def _get_role_technical_question(role_title: str, subjects: str, difficulty: str) -> str:
        r = role_title.lower()
        if "frontend" in r or "react" in r:
            return f"Explain the critical rendering path in modern web browsers and how you optimize Web Core Vitals (LCP, INP, CLS) in a high-traffic React application. How do you mitigate unnecessary re-renders in deep component trees?"
        elif "backend" in r or "python" in r:
            return f"How do you design a high-throughput, low-latency RESTful and event-driven API service? Detail your approach to database connection pooling, asynchronous I/O execution, and distributed rate limiting."
        elif "ai" in r or "ml" in r or "data scientist" in r:
            return f"Walk me through the end-to-end architecture of a production Retrieval-Augmented Generation (RAG) system. How do you handle chunking strategies, dense vs sparse hybrid search, cross-encoder re-ranking, and hallucination reduction?"
        elif "devops" in r or "cloud" in r:
            return f"Describe your strategy for zero-downtime blue/green or canary deployments on Kubernetes with automated rollback mechanisms, distributed tracing, and infrastructure-as-code state management."
        else:
            return f"Walk me through how you architect a resilient, modular system covering {subjects}. What concurrency models, database isolation levels, and caching strategies do you apply under heavy load?"

    @staticmethod
    def _get_scenario_question(role_title: str, difficulty: str, target_company: Optional[str]) -> str:
        comp = (target_company or "").lower()
        if "amazon" in comp:
            return "Scenario: During Prime Day, your inventory checkout service experiences a 10x traffic surge and database connection timeouts begin spiking to 15%. How do you triage the incident, shed load, and prevent cascading microservice failures?"
        elif "google" in comp:
            return "Scenario: Design a globally distributed key-value storage engine supporting millions of read/write operations per second across multiple continents. How do you guarantee eventual consistency and resolve replication conflicts?"
        else:
            return f"Scenario: You are designing a real-time event streaming and analytics dashboard for 500,000 active concurrent users. How do you structure the data ingestion pipeline, WebSocket connection layer, and cache invalidation?"

    @classmethod
    def generate_follow_up_question(
        cls,
        role_title: str,
        current_question_text: str,
        candidate_answer: str,
        evaluation_score: float,
        question_order: int
    ) -> Dict[str, Any]:
        """
        Dynamically adapts question sequence based on candidate's previous response.
        If score >= 80, escalates to deep architectural edge cases.
        If score < 50, pivots to clarifying fundamental mechanisms.
        """
        if evaluation_score >= 80.0:
            diff_level = "Advanced"
            prompt = f"The candidate answered strongly ({evaluation_score}/100) to '{current_question_text}': '{candidate_answer[:250]}'. Generate an advanced technical follow-up question probing scalability limits, edge cases, failure recovery, or deeper architectural trade-offs."
            category = "Advanced Follow-up / Architectural Probe"
        else:
            diff_level = "Intermediate"
            prompt = f"The candidate answered partially ({evaluation_score}/100) to '{current_question_text}': '{candidate_answer[:250]}'. Generate a supportive follow-up question asking them to clarify foundational concepts, specific implementations, or a practical example."
            category = "Clarification & Fundamentals Follow-up"

        try:
            res_text, _, _ = ai_manager.generate_structured(
                prompt=prompt,
                system_prompt="You are an expert technical interviewer. Output ONLY the follow-up question as a single concise question string."
            )
            q_text = res_text.strip().replace('"', '')
            if len(q_text) < 20:
                raise ValueError("Too short")
        except Exception:
            if evaluation_score >= 80.0:
                q_text = f"Following up on your answer: how would your proposed solution scale when handling a 100x spike in concurrent writes, and how do you handle partial network partitions?"
            else:
                q_text = f"Could you elaborate on the practical implementation details and give a concrete example from your past projects where you applied this approach?"

        return {
            "question_order": question_order,
            "category": category,
            "is_follow_up": True,
            "difficulty_level": diff_level,
            "question": q_text
        }

    @classmethod
    def analyze_communication(
        cls,
        answer_text: str,
        time_spent_seconds: int,
        pauses_count: int = 0
    ) -> Dict[str, Any]:
        """
        Evaluates speech transcripts for pacing (WPM), filler words,
        immediate word repetitions, vocabulary richness, and STAR framework markers.
        """
        clean_text = answer_text or ""
        words = re.findall(r'\b[a-zA-Z0-9_\'-]+\b', clean_text.lower())
        word_count = len(words)
        unique_words = set(words)

        # 1. Filler Words Detection
        detected_fillers: Dict[str, int] = {}
        text_lower = clean_text.lower()
        for filler in FILLER_WORDS:
            pattern = r'\b' + re.escape(filler) + r'\b'
            cnt = len(re.findall(pattern, text_lower))
            if cnt > 0:
                detected_fillers[filler] = cnt

        total_fillers = sum(detected_fillers.values())

        # 2. Repeated Words Detection (e.g. "I I", "the the", "we we")
        repeated_words_list = []
        for match in re.finditer(r'\b(\w+)\s+\1\b', text_lower):
            repeated_words_list.append(match.group(0))

        # 3. Speaking Pace (WPM)
        duration_minutes = max(0.2, (time_spent_seconds or 60) / 60.0)
        wpm = round(word_count / duration_minutes, 1)

        if wpm < 100:
            pace_rating = "Deliberate / Slow Pace (aim for 120-150 WPM for maximum engagement)"
        elif 110 <= wpm <= 165:
            pace_rating = "Optimal Conversational Pace (120-165 WPM)"
        else:
            pace_rating = "Rapid Pace (pause deliberately between points to allow interviewer digestion)"

        # 4. Vocabulary Richness (Type-Token Ratio)
        vocab_score = round((len(unique_words) / max(word_count, 1)) * 100.0, 1) if word_count > 0 else 0.0

        # 5. Clarity Rating
        if total_fillers <= 2 and 110 <= wpm <= 165 and len(repeated_words_list) == 0:
            clarity_rating = "Exceptional Clarity"
        elif total_fillers <= 5 and 90 <= wpm <= 180:
            clarity_rating = "Clear & Professional"
        elif total_fillers <= 9:
            clarity_rating = "Moderate Fillers Detected"
        else:
            clarity_rating = "High Filler Count — Practice Pausing"

        # 6. STAR Method Markers
        star_analysis: Dict[str, Any] = {}
        for phase, markers in STAR_MARKERS.items():
            detected = any(m in text_lower for m in markers)
            star_analysis[phase] = {
                "detected": detected,
                "label": phase.capitalize()
            }

        return {
            "word_count": word_count,
            "wpm": wpm,
            "pace_rating": pace_rating,
            "filler_words": detected_fillers,
            "total_fillers": total_fillers,
            "repeated_words": repeated_words_list,
            "pauses_count": pauses_count,
            "vocabulary_score": vocab_score,
            "clarity_rating": clarity_rating,
            "star_analysis": star_analysis
        }

    @classmethod
    def evaluate_answer(
        cls,
        question_text: str,
        category: str,
        candidate_answer: str,
        time_spent_seconds: int,
        pauses_count: int = 0,
        user_llm_provider: Optional[str] = None,
        api_key: Optional[str] = None,
        ollama_endpoint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Conducts semantic, multi-dimensional evaluation of technical answer:
        Technical correctness, conceptual understanding, relevance, completeness,
        problem-solving, and practical examples. Assigns score out of 10 and 100.
        """
        comm_stats = cls.analyze_communication(candidate_answer, time_spent_seconds, pauses_count)
        word_count = comm_stats["word_count"]

        prompt = f"""Evaluate this mock interview candidate's response with senior engineering rigor:
Question: {question_text}
Category: {category}
Candidate Answer: {candidate_answer}
Word Count: {word_count}

Output a strictly valid JSON object matching this schema:
{{
  "score": (float 0 to 100),
  "technical_accuracy": (float 0 to 100),
  "completeness": (float 0 to 100),
  "problem_solving_rating": (float 0 to 100),
  "feedback": "2-3 constructive sentences coaching technical depth and clarity",
  "correct_points": ["Strong technical point 1", "Strong technical point 2"],
  "incorrect_points": ["Misconception or inaccurate statement if any"],
  "missing_concepts": ["Crucial concept omitted that would elevate answer"],
  "model_answer": "Concise, gold-standard answer demonstrating deep technical expertise",
  "improvement_suggestions": "Concrete guidance on how to structure a higher-impact answer"
}}
"""
        user_cfg = {}
        if api_key:
            user_cfg["groq_api_key"] = api_key
        if ollama_endpoint:
            user_cfg["ollama_endpoint"] = ollama_endpoint

        llm_output = ai_manager.generate_structured(
            prompt=prompt,
            system_prompt="You are a principal engineer conducting a technical interview. Accept alternative correct wording and practical variations. Output JSON only.",
            schema_cls=InterviewAnswerEvaluation,
            preferred_provider=user_llm_provider,
            user_config=user_cfg
        )

        eval_data = llm_output.structured_data or {}
        score_100 = float(eval_data.get("score", 70.0))
        score_10 = round(score_100 / 10.0, 1)

        eval_data["score"] = score_100
        eval_data["score_out_of_10"] = score_10
        eval_data["technical_accuracy"] = float(eval_data.get("technical_accuracy", score_100))
        eval_data["completeness"] = float(eval_data.get("completeness", score_100))
        eval_data["problem_solving_rating"] = float(eval_data.get("problem_solving_rating", score_100))

        if not eval_data.get("correct_points"):
            eval_data["correct_points"] = ["Articulated general engineering concepts clearly."]
        if not eval_data.get("missing_concepts"):
            eval_data["missing_concepts"] = ["Concrete performance benchmarks or edge-case failure modes."]
        if not eval_data.get("incorrect_points"):
            eval_data["incorrect_points"] = []
        if not eval_data.get("improvement_suggestions"):
            eval_data["improvement_suggestions"] = "Structure explanations with the Problem -> Architecture -> Trade-offs pattern."

        eval_data["is_fallback"] = llm_output.is_fallback
        eval_data["provider_used"] = llm_output.provider_used
        eval_data["model_used"] = llm_output.model_used
        eval_data["ideal_answer"] = eval_data.get("model_answer", "")

        # Communication analysis metrics attached
        eval_data["filler_words"] = comm_stats["filler_words"]
        eval_data["total_fillers"] = comm_stats["total_fillers"]
        eval_data["repeated_words"] = comm_stats["repeated_words"]
        eval_data["pauses_count"] = comm_stats["pauses_count"]
        eval_data["wpm"] = comm_stats["wpm"]
        eval_data["vocabulary_score"] = comm_stats["vocabulary_score"]
        eval_data["clarity_rating"] = comm_stats["clarity_rating"]
        eval_data["star_analysis"] = comm_stats["star_analysis"]

        return eval_data

    @classmethod
    def generate_interview_summary(
        cls,
        questions_evaluations: List[Dict[str, Any]],
        role_title: str = "Software Development Engineer"
    ) -> Dict[str, Any]:
        """
        Aggregates session scores across technical accuracy, communication,
        answer quality, and problem solving; drafts actionable improvement plan.
        """
        if not questions_evaluations:
            return {
                "overall_score": 0.0,
                "technical_score": 0.0,
                "communication_score": 0.0,
                "behavioral_score": 0.0,
                "answer_quality_score": 0.0,
                "problem_solving_score": 0.0,
                "verdict": "Needs Improvement",
                "overall_summary": "Session concluded with no answers recorded.",
                "key_strengths": [],
                "areas_to_improve": ["Complete a full practice session."],
                "recommended_topics": ["Core technical interview fundamentals."],
                "improvement_plan": [],
                "total_filler_words": 0,
                "average_wpm": 0.0,
                "clarity_rating": "Incomplete",
                "full_transcript": ""
            }

        scores = [q.get("score", 0.0) for q in questions_evaluations]
        tech_scores = [q.get("technical_accuracy", 0.0) for q in questions_evaluations]
        prob_scores = [q.get("problem_solving_rating", 0.0) for q in questions_evaluations]
        fillers = [q.get("total_fillers", 0) for q in questions_evaluations]
        wpms = [q.get("wpm", 0.0) for q in questions_evaluations if q.get("wpm", 0.0) > 0]

        avg_score = round(sum(scores) / len(scores), 1)
        avg_tech = round(sum(tech_scores) / len(tech_scores), 1)
        avg_prob = round(sum(prob_scores) / len(prob_scores), 1)
        total_fillers = sum(fillers)
        avg_wpm = round(sum(wpms) / max(len(wpms), 1), 1)

        # Communication score calculation
        filler_penalty = min(25.0, total_fillers * 2.0)
        pace_penalty = 0.0 if (110 <= avg_wpm <= 165) else 10.0
        comm_score = round(max(30.0, 100.0 - filler_penalty - pace_penalty), 1)

        # Answer Quality Score (completeness & structure)
        completeness_list = [q.get("completeness", 70.0) for q in questions_evaluations]
        avg_quality = round(sum(completeness_list) / len(completeness_list), 1)

        # Hiring Verdict
        if avg_score >= 85.0 and comm_score >= 80.0:
            verdict = "Strong Hire"
        elif avg_score >= 72.0:
            verdict = "Hire"
        elif avg_score >= 58.0:
            verdict = "Lean Hire"
        else:
            verdict = "Needs Improvement"

        # Strengths & Weaknesses
        strengths = []
        weaknesses = []
        for q in questions_evaluations:
            for s in q.get("correct_points", []):
                if s not in strengths and len(strengths) < 4:
                    strengths.append(s)
            for m in q.get("missing_concepts", []):
                if m not in weaknesses and len(weaknesses) < 4:
                    weaknesses.append(m)

        if not strengths:
            strengths = ["Communicated clearly with consistent professional engagement."]
        if not weaknesses:
            weaknesses = ["Incorporate concrete scale metrics (e.g. latency, QPS, data volume)."]

        # Actionable 4-Step Improvement Plan
        improvement_plan = [
            f"Step 1 (Fundamentals): Review core architecture patterns relevant to {role_title}.",
            "Step 2 (Pacing & Fillers): Practice 2-second silent pauses instead of verbal fillers ('um', 'like').",
            "Step 3 (STAR Formatting): Explicitly structure answers: Situation -> Architectural Task -> Action -> Quantified Result.",
            "Step 4 (Trade-off Articulation): For every design choice, state at least one alternative and why you rejected it."
        ]

        # Recommended Topics
        recommended_topics = [
            f"Advanced {role_title} System Architecture",
            "Distributed Caching, Invalidation & CAP Theorem",
            "STAR-format Behavioral Articulation",
            "High-Throughput Concurrency & Async I/O"
        ]

        # Assemble Full Transcript
        transcript_lines = []
        for idx, q in enumerate(questions_evaluations, 1):
            q_text = q.get("question_text") or f"Question {idx}"
            ans_text = q.get("candidate_answer") or "[No response provided]"
            transcript_lines.append(f"Q{idx}: {q_text}\nCandidate: {ans_text}\nScore: {q.get('score', 0)}/100 (Score: {round(q.get('score', 0)/10.0, 1)}/10)\n")

        full_transcript = "\n".join(transcript_lines)

        clarity = "Exceptional" if total_fillers < 4 and 110 <= avg_wpm <= 165 else ("Good" if total_fillers < 10 else "Needs Practice")

        return {
            "overall_score": avg_score,
            "technical_score": avg_tech,
            "communication_score": comm_score,
            "behavioral_score": round((avg_score + comm_score) / 2.0, 1),
            "answer_quality_score": avg_quality,
            "problem_solving_score": avg_prob,
            "verdict": verdict,
            "overall_summary": f"Candidate demonstrated {verdict} readiness for {role_title}. Technical correctness averaged {avg_tech}%, with communication pacing at {avg_wpm} WPM.",
            "key_strengths": strengths,
            "areas_to_improve": weaknesses,
            "recommended_topics": recommended_topics,
            "improvement_plan": improvement_plan,
            "total_filler_words": total_fillers,
            "average_wpm": avg_wpm,
            "clarity_rating": clarity,
            "full_transcript": full_transcript
        }

    @classmethod
    def generate_pdf_report(cls, session: Any) -> bytes:
        """
        Generates an executive, styled PDF report of the mock interview session
        using ReportLab, including score summaries, question-wise breakdown,
        communication metrics, and assessment limitations disclaimer.
        """
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        primary_color = colors.HexColor("#0f172a") # Slate-900
        accent_color = colors.HexColor("#0284c7")  # Cyan-600
        text_color = colors.HexColor("#334155")

        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            textColor=primary_color
        )

        subtitle_style = ParagraphStyle(
            'SubTitleStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=accent_color
        )

        heading_style = ParagraphStyle(
            'HeadingStyle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=17,
            textColor=primary_color,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13.5,
            textColor=text_color
        )

        bold_body = ParagraphStyle(
            'BoldBody',
            parent=body_style,
            fontName='Helvetica-Bold'
        )

        disclaimer_style = ParagraphStyle(
            'DisclaimerStyle',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#64748b")
        )

        elements = []

        # 1. Header Banner
        elements.append(Paragraph("VIRTUAL AI MOCK INTERVIEW — PERFORMANCE REPORT", title_style))
        elements.append(Spacer(1, 4))
        date_str = session.completed_at.strftime('%B %d, %Y') if session.completed_at else datetime.utcnow().strftime('%B %d, %Y')
        elements.append(Paragraph(f"Candidate: {session.role_title} Candidate • Track: {session.interview_type} • Date: {date_str}", subtitle_style))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=accent_color, spaceAfter=14))

        # 2. Executive Scorecard Table
        verdict = session.verdict or "Hire"
        score_data = [
            [
                Paragraph("<b>Overall Score</b>", bold_body),
                Paragraph("<b>Technical Score</b>", bold_body),
                Paragraph("<b>Communication</b>", bold_body),
                Paragraph("<b>Problem Solving</b>", bold_body),
                Paragraph("<b>Hiring Verdict</b>", bold_body)
            ],
            [
                Paragraph(f"<font size='14' color='#0284c7'><b>{session.overall_score}%</b></font><br/>({round(session.overall_score/10.0, 1)}/10)", body_style),
                Paragraph(f"<font size='14'><b>{session.technical_score}%</b></font>", body_style),
                Paragraph(f"<font size='14'><b>{session.communication_score}%</b></font>", body_style),
                Paragraph(f"<font size='14'><b>{session.problem_solving_score or session.overall_score}%</b></font>", body_style),
                Paragraph(f"<font size='12' color='#16a34a'><b>{verdict}</b></font>", body_style),
            ]
        ]
        score_table = Table(score_data, colWidths=[108, 108, 108, 108, 108])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(score_table)
        elements.append(Spacer(1, 16))

        # 3. Speech & Communication Insights
        elements.append(Paragraph("Speech & Communication Indicators", heading_style))
        comm_text = f"• Average Speaking Pace: <b>{session.average_wpm} WPM</b> (Optimal: 120-165 WPM)<br/>" \
                    f"• Total Filler Words ('um', 'like', etc.): <b>{session.total_filler_words}</b><br/>" \
                    f"• Clarity Assessment: <b>{session.clarity_rating}</b>"
        elements.append(Paragraph(comm_text, body_style))
        elements.append(Spacer(1, 14))

        # 4. Strengths & Growth Areas
        elements.append(Paragraph("Key Strengths & Growth Opportunities", heading_style))
        strengths_p = "<b>Demonstrated Strengths:</b><br/>" + "<br/>".join([f"✓ {s}" for s in (session.key_strengths or [])])
        areas_p = "<br/><b>Areas for Technical Refinement:</b><br/>" + "<br/>".join([f"• {a}" for a in (session.areas_to_improve or [])])
        elements.append(Paragraph(strengths_p + "<br/>" + areas_p, body_style))
        elements.append(Spacer(1, 14))

        # 5. Question-by-Question Evaluation Summary
        elements.append(Paragraph("Question-by-Question Evaluation", heading_style))
        for q in session.questions:
            q_header = f"<b>Q{q.question_order} ({q.category}):</b> {q.question_text}"
            score_line = f"<b>Score:</b> {q.score}/100 ({q.score_out_of_10 or round(q.score/10.0, 1)}/10) | <b>Pacing:</b> {q.wpm} WPM"
            feedback_line = f"<b>Coaching Feedback:</b> {q.feedback or 'Good explanation.'}"
            elements.append(Paragraph(q_header, body_style))
            elements.append(Spacer(1, 2))
            elements.append(Paragraph(score_line, body_style))
            elements.append(Spacer(1, 2))
            elements.append(Paragraph(feedback_line, body_style))
            if q.ideal_answer:
                ideal_p = f"<b>Model Answer:</b> {q.ideal_answer[:300]}..."
                elements.append(Paragraph(ideal_p, disclaimer_style))
            elements.append(Spacer(1, 8))

        # 6. Actionable Improvement Plan
        if session.improvement_plan:
            elements.append(Paragraph("Personalized 4-Step Improvement Plan", heading_style))
            plan_str = "<br/>".join([f"{p}" for p in session.improvement_plan])
            elements.append(Paragraph(plan_str, body_style))
            elements.append(Spacer(1, 14))

        # 7. Ethical AI Limitations Disclaimer
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94a3b8"), spaceAfter=8))
        disclaimer_text = session.assessment_disclaimer or "Notice: Audio, video, and speech analyses are heuristic coaching estimates. Antigravity AI does not claim to detect personality, honesty, or cognitive suitability from facial appearance."
        elements.append(Paragraph(disclaimer_text, disclaimer_style))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

interview_service = InterviewService()
