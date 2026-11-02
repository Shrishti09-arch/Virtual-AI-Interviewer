"""
Unit and Integration Tests for Module 6 AI Career Roadmap
Tests dynamic multi-phase roadmap generation, daily study plans,
and structured milestone task progression.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.roadmap_service import roadmap_service


class TestCareerRoadmap(unittest.TestCase):
    def test_dynamic_roadmap_generation(self):
        plan = roadmap_service.generate_career_roadmap(
            target_role="AI/ML Engineer",
            current_level="Beginner",
            education="B.S. in Computer Science",
            existing_skills=["Python", "Calculus"],
            daily_study_hours=3.0,
            career_goal="Become Junior ML Engineer",
            timeline_months=6
        )
        self.assertIn("overview", plan)
        self.assertIn("daily_study_plan", plan)
        self.assertIn("milestones", plan)
        self.assertTrue(len(plan["milestones"]) >= 3)

        # Check first milestone structure
        m1 = plan["milestones"][0]
        self.assertIn("title", m1)
        self.assertIn("duration", m1)
        self.assertIn("topics", m1)
        self.assertIn("practice_tasks", m1)
        self.assertIn("checklist", m1)
        self.assertIn("recommended_projects", m1)
        self.assertIn("learning_resources", m1)
        self.assertIn("interview_questions", m1)

    def test_daily_study_plan_generation(self):
        study_plan = roadmap_service._generate_daily_study_plan(daily_hours=2.5)
        self.assertIn("total_daily_minutes", study_plan)
        self.assertEqual(study_plan["total_daily_minutes"], 150)
        self.assertIn("routine", study_plan)
        self.assertTrue(len(study_plan["routine"]) >= 3)


if __name__ == "__main__":
    unittest.main()
