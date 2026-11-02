"""
Unit and Integration Tests for Module 4 AI Technical Interview Practice
Tests metadata retrieval, question bank operations, and sandboxed code execution.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.question_service import question_service, SandboxExecutor, SecurityViolationError


class TestTechnicalPractice(unittest.TestCase):
    def test_metadata_retrieval(self):
        metadata = question_service.get_supported_metadata()
        self.assertIn("subjects", metadata)
        self.assertIn("difficulties", metadata)
        self.assertIn("interview_types", metadata)
        self.assertIn("languages", metadata)
        self.assertIn("Data Structures and Algorithms", metadata["subjects"])

    def test_sandbox_python_success(self):
        code = "def two_sum(nums, target):\n    return [0, 1]"
        test_cases = [
            {"input": "[[2, 7, 11, 15], 9]", "expected_output": "[0, 1]"}
        ]
        result = SandboxExecutor.execute("python", code, test_cases)
        self.assertEqual(result.get("status"), "Accepted")
        self.assertEqual(result.get("passed_tests"), 1)

    def test_sandbox_security_rejection(self):
        malicious = "import os\nos.system('dir')"
        with self.assertRaises(SecurityViolationError):
            SandboxExecutor.inspect_python_security(malicious)


if __name__ == "__main__":
    unittest.main()
