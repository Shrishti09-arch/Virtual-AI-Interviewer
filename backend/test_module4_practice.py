import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.database import SessionLocal
from app.models.user import User
from app.models.practice import QuestionBank, PracticeSession, UserQuestionHistory
from app.services.seed_service import seed_question_bank
from app.routers import practice
from app.schemas.practice import (
    StartPracticeSessionRequest,
    PracticeAnswerSubmitRequest,
    ExecuteCodeRequest
)

def test_module4_all():
    print("\n==========================================")
    print("RUNNING COMPLETE MODULE 4 TECHNICAL PRACTICE TEST SUITE")
    print("==========================================")

    db = SessionLocal()
    seed_question_bank(db)

    # Setup test user
    user = db.query(User).filter(User.email == "module4_user@test.com").first()
    if not user:
        user = User(
            email="module4_user@test.com",
            hashed_password="hashed_pw_test",
            full_name="Module 4 Candidate",
            role_target="Software Development Engineer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 1. Test Metadata Endpoint
    print("\n--- 1. Testing GET /api/v1/practice/metadata ---")
    meta = practice.get_practice_metadata()
    subjects = meta["subjects"] if isinstance(meta, dict) else meta.subjects
    difficulties = meta["difficulties"] if isinstance(meta, dict) else meta.difficulties
    types = meta["interview_types"] if isinstance(meta, dict) else meta.interview_types
    assert len(subjects) == 14, f"Expected 14 subjects, got {len(subjects)}"
    assert "Data Structures and Algorithms" in subjects
    assert "Operating Systems" in subjects
    assert "System Design" in subjects
    assert "SQL" in subjects
    assert "Deep Learning" in subjects
    assert len(difficulties) == 4
    print(f"Metadata verified: {len(subjects)} subjects, {len(difficulties)} difficulties, {len(types)} interview types.")

    # 2. Test Question Bank Filtering & Legit Sources
    print("\n--- 2. Testing Question Bank Retrieval & Source Verification ---")
    dsa_qs = practice.get_questions(subject="Data Structures and Algorithms", db=db)
    assert len(dsa_qs) >= 2, f"Expected at least 2 DSA questions, got {len(dsa_qs)}"
    for q in dsa_qs:
        assert q.source_type in ["curated_educational", "ai_generated"]
        if q.source_type == "curated_educational":
            assert q.source_url and q.source_url.startswith("http")
            print(f"Verified Curated Source: [{q.title}] -> {q.source_name} ({q.source_url})")

    # 3. Test Safe Subprocess Code Execution Sandbox
    print("\n--- 3. Testing Safe Subprocess Code Execution Sandbox ---")
    # 3a. Normal Python execution
    code_sol = """def solution(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        if target - n in seen:
            return [seen[target - n], i]
        seen[n] = i
    return []
"""
    exec_req = ExecuteCodeRequest(
        language="python",
        code=code_sol,
        test_cases=[
            {"input": "[[2, 7, 11, 15], 9]", "expected_output": "[0, 1]"},
            {"input": "[[3, 2, 4], 6]", "expected_output": "[1, 2]"}
        ]
    )
    res_data = practice.run_code_in_sandbox(payload=exec_req, current_user=user)
    assert res_data["passed"] is True, f"Expected passed=True, got {res_data}"
    assert res_data["passed_tests"] == 2
    assert res_data["status"] == "Accepted"
    print("Isolated Python execution PASSED all test cases.")

    # 3b. Security violation check (AST forbids os/sys/eval/exec/open)
    malicious_code = """import os
print(os.listdir('.'))
"""
    sec_req = ExecuteCodeRequest(language="python", code=malicious_code, test_cases=[])
    sec_data = practice.run_code_in_sandbox(payload=sec_req, current_user=user)
    assert sec_data["status"] == "Security Violation"
    assert "prohibited in the execution sandbox" in sec_data["error"]
    print("Static AST Security check correctly BLOCKED malicious module import.")

    # 3c. SQL sandbox execution
    sql_query = "SELECT MAX(salary) FROM Employee WHERE salary < (SELECT MAX(salary) FROM Employee);"
    sql_req = ExecuteCodeRequest(
        language="sql",
        code=sql_query,
        test_cases=[
            {
                "input": "test dataset",
                "setup_sql": "CREATE TABLE Employee (id INT, salary INT); INSERT INTO Employee VALUES (1, 100), (2, 200), (3, 300);",
                "expected_output": "[[200]]"
            }
        ]
    )
    sql_data = practice.run_code_in_sandbox(payload=sql_req, current_user=user)
    assert sql_data["passed"] is True, f"SQL sandbox test failed: {sql_data}"
    print("In-memory SQLite sandbox query execution PASSED.")

    # 4. Interactive Practice Session Lifecycle
    print("\n--- 4. Testing Interactive Practice Session Lifecycle ---")
    start_req = StartPracticeSessionRequest(
        job_role="Software Development Engineer",
        subject="Data Structures and Algorithms",
        programming_language="Python",
        difficulty="Intermediate",
        total_questions=2,
        interview_type="Comprehensive Mixed"
    )
    session_data = practice.start_practice_session(payload=start_req, current_user=user, db=db)
    if isinstance(session_data, dict):
        session_id = session_data["session_id"]
        total_questions = session_data["total_questions"]
        current_index = session_data["current_index"]
        is_completed = session_data["is_completed"]
        q1 = session_data["active_question"]
    else:
        session_id = session_data.session_id
        total_questions = session_data.total_questions
        current_index = session_data.current_index
        is_completed = session_data.is_completed
        q1 = session_data.active_question

    assert total_questions == 2
    assert current_index == 0
    assert is_completed is False
    assert q1 is not None
    print(f"Practice Session #{session_id} created. Question 1/2: [{q1['title']}] ({q1['question_type']})")

    # 4a. Answer Question 1
    if q1["question_type"] == "MCQ":
        ans_payload = PracticeAnswerSubmitRequest(
            question_id=q1["id"],
            answer_type="mcq",
            selected_option_index=1
        )
    elif q1["question_type"] == "Coding":
        ans_payload = PracticeAnswerSubmitRequest(
            question_id=q1["id"],
            answer_type="coding",
            code=code_sol,
            language="python"
        )
    else:
        ans_payload = PracticeAnswerSubmitRequest(
            question_id=q1["id"],
            answer_type="theory",
            user_answer="Binary search has logarithmic time complexity O(log n) because the search space is divided in half at each step."
        )

    q1_result = practice.submit_session_answer(
        session_id=session_id,
        payload=ans_payload,
        current_user=user,
        db=db
    )
    q1_idx = q1_result["current_index"] if isinstance(q1_result, dict) else q1_result.current_index
    q1_done = q1_result["is_completed"] if isinstance(q1_result, dict) else q1_result.is_completed
    q2 = q1_result["next_question"] if isinstance(q1_result, dict) else q1_result.next_question
    q1_eval = q1_result["evaluation"] if isinstance(q1_result, dict) else q1_result.evaluation

    assert q1_idx == 1
    assert q1_done is False
    assert q2 is not None
    print(f"Question 1 evaluated with score: {q1_eval['score']}. Advanced to Question 2.")

    # 4b. Answer Question 2 (Completing session)
    if q2["question_type"] == "MCQ":
        ans2_payload = PracticeAnswerSubmitRequest(
            question_id=q2["id"],
            answer_type="mcq",
            selected_option_index=1
        )
    elif q2["question_type"] == "Coding":
        ans2_payload = PracticeAnswerSubmitRequest(
            question_id=q2["id"],
            answer_type="coding",
            code=code_sol,
            language="python"
        )
    else:
        ans2_payload = PracticeAnswerSubmitRequest(
            question_id=q2["id"],
            answer_type="theory",
            user_answer="Dijkstra algorithm uses a priority queue with non-negative edge weights, whereas Bellman-Ford can handle negative weights and detect negative cycles in O(V * E) time."
        )

    q2_result = practice.submit_session_answer(
        session_id=session_id,
        payload=ans2_payload,
        current_user=user,
        db=db
    )
    q2_done = q2_result["is_completed"] if isinstance(q2_result, dict) else q2_result.is_completed
    report = q2_result["final_report"] if isinstance(q2_result, dict) else q2_result.final_report

    assert q2_done is True
    assert report is not None

    print("\n--- 5. Verifying Final Executive Report ---")
    assert report["total_questions"] == 2
    assert "accuracy" in report
    assert "topic_performance" in report
    assert "weak_areas" in report
    assert "recommended_topics" in report
    print(f"Final Report: Accuracy = {report['accuracy']}%, Correct = {report['correct_count']}/{report['total_questions']}")
    print(f"Topic Performance: {report['topic_performance']}")
    print(f"Recommended Next Topics: {report['recommended_topics']}")

    # 6. Verify User History Tracking (Duplicate Prevention)
    print("\n--- 6. Verifying User Question History Uniqueness ---")
    history_count = db.query(UserQuestionHistory).filter(UserQuestionHistory.user_id == user.id).count()
    assert history_count >= 2, f"Expected at least 2 questions in user history, got {history_count}"
    print(f"Successfully recorded {history_count} questions in UserQuestionHistory to avoid repetition.")

    db.close()
    print("\n==========================================")
    print("ALL MODULE 4 TECHNICAL PRACTICE TESTS PASSED (100%)!")
    print("==========================================")

if __name__ == "__main__":
    test_module4_all()
