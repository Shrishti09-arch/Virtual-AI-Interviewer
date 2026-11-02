"""
Unit and Integration Tests for Module 5 Virtual AI Mock Interview
Tests speech communication analysis, multi-dimensional answer evaluation,
and interview question orchestration.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.evaluation_service import evaluation_service
from services.transcription_service import transcription_service
from app.services.interview_service import InterviewService


class TestMockInterview(unittest.TestCase):
    def test_communication_analysis(self):
        answer_text = (
            "Well, basically when I was at my previous company, our team had a huge latency bottleneck. "
            "My responsibility was to refactor the distributed caching layer. "
            "I decided to implement Redis with cache-aside pattern. "
            "Consequently, we improved our p99 query latency by 45 percent."
        )
        comm = transcription_service.analyze_communication(
            answer_text=answer_text,
            speaking_duration_seconds=30,
            pauses_count=1
        )
        self.assertIn("wpm", comm)
        self.assertIn("filler_words", comm)
        self.assertIn("star_analysis", comm)
        self.assertTrue(comm["star_analysis"]["situation"]["detected"])
        self.assertTrue(comm["star_analysis"]["result"]["detected"])
        self.assertIn("ethical_disclaimer", comm)

    def test_answer_evaluation(self):
        question = "How does consistent hashing minimize remapping in distributed caches?"
        answer = (
            "Consistent hashing maps both servers and keys to a circular ring hash space. "
            "When a node is added or removed, only k/n keys need to be remapped on average."
        )
        eval_res = evaluation_service.evaluate_answer(
            question=question,
            answer=answer,
            role="Software Engineer"
        )
        self.assertIn("score", eval_res)
        self.assertGreater(eval_res["score"], 40)
        self.assertIn("model_answer", eval_res)

    def test_initial_questions_generation(self):
        questions = InterviewService.get_initial_questions(
            role_title="Backend Developer",
            experience_level="Mid-Level",
            interview_type="Technical",
            difficulty="Intermediate",
            total_questions=3
        )
        self.assertEqual(len(questions), 3)
        self.assertIn("question", questions[0])


if __name__ == "__main__":
    unittest.main()
