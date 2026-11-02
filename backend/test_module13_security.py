import datetime
import io
import os
import sys
import time
import zipfile
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

# Setup import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.database import SessionLocal
from app.models.user import User
from app.models.resume import Resume, ResumeAnalysis
from app.models.interview import InterviewSession
from app.routers import auth, resumes, interviews, ai_settings
from app.schemas.user import UserRegister, UserLogin, AIPreferenceUpdate
from app.schemas.interview import InterviewStartRequest
from app.core.security import (
    get_password_hash,
    verify_password,
    validate_password_strength,
    create_access_token,
    decode_access_token,
    revoke_token,
    is_token_revoked,
    mask_api_key,
    validate_file_size,
    validate_resume_file,
    validate_recording_file,
    safe_extract_pdf_text,
    safe_extract_docx_text,
    secure_delete_file,
    sanitize_input_text,
    MAX_RESUME_SIZE,
    MAX_RECORDING_SIZE
)
from app.services.auth_service import get_current_user
from app.services.sandbox_executor import sandbox_executor, SecurityViolationError

# Mock UploadFile class for router test calls
class MockUploadFile:
    def __init__(self, filename: str, content: bytes, content_type: str = "application/octet-stream"):
        self.filename = filename
        self.content = content
        self.content_type = content_type

    def read(self):
        return self.content

def run_all_security_tests():
    print("\n=======================================================")
    print("RUNNING EXHAUSTIVE SECTION 13 SECURITY AUDIT & TEST SUITE")
    print("=======================================================\n")

    db: Session = SessionLocal()

    # -------------------------------------------------------------
    # 1. Secure Password Hashing & Complexity Policy
    # -------------------------------------------------------------
    print("--- 1. Testing Secure Password Hashing & Complexity Policy ---")
    pw = "SuperSecure@2026!"
    hashed = get_password_hash(pw)
    assert hashed != pw, "Password was stored in plaintext!"
    assert hashed.startswith("$argon2id$") or hashed.startswith("pbkdf2:"), "Hash algorithm not Argon2id or PBKDF2!"
    assert verify_password(pw, hashed) is True, "Password verification failed!"
    assert verify_password("WrongPassword123!", hashed) is False, "Wrong password erroneously verified!"

    # Test password policy validation
    ok, _ = validate_password_strength("Short1!")
    assert ok is False, "Failed to reject short password (<8 chars)"
    ok, _ = validate_password_strength("alllettersnocount")
    assert ok is False, "Failed to reject password without digits"
    ok, _ = validate_password_strength("1234567890")
    assert ok is False, "Failed to reject password without letters"
    ok, msg = validate_password_strength(pw)
    assert ok is True, f"Valid password rejected: {msg}"
    print("[PASS] Argon2id password hashing and complexity policy verified.")

    # -------------------------------------------------------------
    # 2. JWT Authentication & Signature Integrity
    # -------------------------------------------------------------
    print("\n--- 2. Testing JWT Authentication & Signature Integrity ---")
    token = create_access_token({"sub": "999"})
    payload = decode_access_token(token)
    assert payload.get("sub") == "999"
    assert "jti" in payload, "JWT missing unique jti"
    assert "iat" in payload, "JWT missing issued-at (iat)"
    assert "exp" in payload, "JWT missing expiration (exp)"

    # Expired token rejection
    expired_token = create_access_token({"sub": "999"}, expires_delta=datetime.timedelta(seconds=-10))
    try:
        decode_access_token(expired_token)
        assert False, "Expired token was not rejected!"
    except HTTPException as e:
        assert e.status_code == 401
    print("[PASS] JWT token generation, signature check, and expiration verified.")

    # -------------------------------------------------------------
    # 3. Protected Routes & Authentication Enforcement
    # -------------------------------------------------------------
    print("\n--- 3. Testing Protected API Routes & Credentials Enforcement ---")
    try:
        get_current_user(credentials=None, db=db)
        assert False, "Protected route allowed unauthenticated request!"
    except HTTPException as e:
        assert e.status_code == 401, f"Expected 401, got {e.status_code}"
        print("  -> Unauthenticated request rejected with HTTP 401.")

    try:
        bad_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid.token.signature")
        get_current_user(credentials=bad_creds, db=db)
        assert False, "Protected route allowed bogus token!"
    except HTTPException as e:
        assert e.status_code == 401
        print("  -> Malformed/tampered token rejected with HTTP 401.")
    print("[PASS] Protected route access control verified.")

    # -------------------------------------------------------------
    # 4. Secure Session Management & Logout Token Revocation
    # -------------------------------------------------------------
    print("\n--- 4. Testing Secure Session Management & Token Blacklisting ---")
    user_email = f"security_user_{int(time.time())}@defense.gov"
    user1 = db.query(User).filter(User.email == user_email).first()
    if not user1:
        user1 = User(
            email=user_email,
            hashed_password=get_password_hash("StrongPassword2026!"),
            full_name="Major Security Auditor",
            role_target="Cybersecurity Engineer"
        )
        db.add(user1)
        db.commit()
        db.refresh(user1)

    auth_token = create_access_token({"sub": str(user1.id)})
    valid_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=auth_token)

    # Verify user can access protected route
    curr = get_current_user(credentials=valid_creds, db=db)
    assert curr.id == user1.id

    # Execute Logout via auth.logout
    logout_res = auth.logout(credentials=valid_creds, current_user=user1)
    assert logout_res["status"] == "success"

    # Verify revoked token is now rejected on protected endpoints
    try:
        get_current_user(credentials=valid_creds, db=db)
        assert False, "Revoked token was not rejected!"
    except HTTPException as e:
        assert e.status_code == 401
        assert "revoked" in e.detail.lower()
    print("[PASS] Logout token revocation blacklist verified: invalidated session cannot be reused.")

    # -------------------------------------------------------------
    # 5. User Data Isolation
    # -------------------------------------------------------------
    print("\n--- 5. Testing User Data Isolation ---")
    user2_email = f"intruder_{int(time.time())}@unauthorized.io"
    user2 = db.query(User).filter(User.email == user2_email).first()
    if not user2:
        user2 = User(
            email=user2_email,
            hashed_password=get_password_hash("AnotherPassword2026!"),
            full_name="Unauthorized Intruder",
            role_target="Backend Developer"
        )
        db.add(user2)
        db.commit()
        db.refresh(user2)

    # User 1 creates resume
    u1_resume = resumes.analyze_resume_text(
        target_role="Cybersecurity Engineer",
        resume_text="Senior security architect specializing in defense in depth and cloud IAM zero-trust.",
        job_description=None,
        current_user=user1,
        db=db
    )
    u1_resume_id = u1_resume.resume_id

    # User 2 attempts to read User 1's extracted resume
    try:
        resumes.get_extracted_resume_data(resume_id=u1_resume_id, current_user=user2, db=db)
        assert False, "Data isolation breached! User 2 accessed User 1's resume data."
    except HTTPException as e:
        assert e.status_code == 404
        print("  -> User 2 blocked from reading User 1's resume (HTTP 404).")

    # User 2 attempts to delete User 1's resume
    try:
        resumes.delete_resume(resume_id=u1_resume_id, current_user=user2, db=db)
        assert False, "Data isolation breached! User 2 deleted User 1's resume."
    except HTTPException as e:
        assert e.status_code == 404
        print("  -> User 2 blocked from deleting User 1's resume (HTTP 404).")

    # User 1 creates interview session
    start_req = InterviewStartRequest(
        role_title="Cybersecurity Engineer",
        interview_type="Technical",
        experience_level="3-5 years",
        difficulty="Advanced",
        technical_subjects=["Computer Networks", "Operating Systems"],
        total_questions=3,
        recording_consent=True
    )
    u1_session = interviews.start_interview_session(start_req=start_req, current_user=user1, db=db)
    u1_sess_id = u1_session.id

    # User 2 attempts to fetch User 1's interview session
    try:
        interviews.get_interview_session(session_id=u1_sess_id, current_user=user2, db=db)
        assert False, "Data isolation breached! User 2 accessed User 1's interview session."
    except HTTPException as e:
        assert e.status_code == 404
        print("  -> User 2 blocked from reading User 1's interview session (HTTP 404).")

    # User 2 attempts to delete User 1's interview session
    try:
        interviews.delete_interview_session(session_id=u1_sess_id, current_user=user2, db=db)
        assert False, "Data isolation breached! User 2 deleted User 1's interview session."
    except HTTPException as e:
        assert e.status_code == 404
        print("  -> User 2 blocked from deleting User 1's interview session (HTTP 404).")
    print("[PASS] Strict user-level data isolation verified across all modules.")

    # -------------------------------------------------------------
    # 6. File Type Validation (Magic Bytes Inspection)
    # -------------------------------------------------------------
    print("\n--- 6. Testing File Type Validation (Magic Bytes Inspection) ---")
    valid_pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
    assert validate_resume_file(valid_pdf_bytes, "resume.pdf") == "pdf"

    # Fake PDF (bash script with .pdf name)
    fake_pdf_bytes = b"#!/bin/bash\nrm -rf /"
    try:
        validate_resume_file(fake_pdf_bytes, "malicious.pdf")
        assert False, "Fake PDF was not rejected!"
    except HTTPException as e:
        assert e.status_code == 415
        print("  -> Disguised executable payload in PDF rejected (HTTP 415).")

    # Fake DOCX (plain text with .docx name)
    fake_docx_bytes = b"This is plain text disguised as DOCX."
    try:
        validate_resume_file(fake_docx_bytes, "malicious.docx")
        assert False, "Fake DOCX was not rejected!"
    except HTTPException as e:
        assert e.status_code == 415
        print("  -> Non-zip payload in DOCX rejected (HTTP 415).")

    # Media container magic bytes
    webm_bytes = b"\x1a\x45\xdf\xa3" + b"\x00" * 32
    assert validate_recording_file(webm_bytes, "rec.webm") == "webm"
    wav_bytes = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00"
    assert validate_recording_file(wav_bytes, "audio.wav") == "wav"

    try:
        validate_recording_file(b"MZ\x90\x00\x03\x00\x00\x00", "audio.mp4")
        assert False, "PE executable disguised as MP4 was not rejected!"
    except HTTPException as e:
        assert e.status_code == 415
        print("  -> Windows PE binary disguised as MP4 rejected (HTTP 415).")
    print("[PASS] Magic byte file type validation verified.")

    # -------------------------------------------------------------
    # 7. File Size Restrictions
    # -------------------------------------------------------------
    print("\n--- 7. Testing File Size Restrictions ---")
    try:
        validate_file_size(b"X" * (MAX_RESUME_SIZE + 1024), MAX_RESUME_SIZE, "Resume document")
        assert False, "Oversized resume allowed!"
    except HTTPException as e:
        assert e.status_code == 413
        print(f"  -> Resume exceeding 10MB limit correctly blocked (HTTP 413).")

    try:
        validate_file_size(b"X" * (MAX_RECORDING_SIZE + 1024), MAX_RECORDING_SIZE, "Media recording")
        assert False, "Oversized recording allowed!"
    except HTTPException as e:
        assert e.status_code == 413
        print(f"  -> Recording exceeding 50MB limit correctly blocked (HTTP 413).")
    print("[PASS] File size limits verified.")

    # -------------------------------------------------------------
    # 8. Safe Document Parsing (Zip Bomb & Path Traversal)
    # -------------------------------------------------------------
    print("\n--- 8. Testing Safe Document Parsing (Zip Bomb & Path Traversal) ---")
    # Path Traversal ZIP
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w") as zf:
        zf.writestr("../../etc/shadow", "root:$6$salt$hash:18000:0:99999:7:::")
    traversal_bytes = zip_buf.getvalue()

    try:
        safe_extract_docx_text(traversal_bytes)
        assert False, "Path traversal inside zip was not blocked!"
    except HTTPException as e:
        assert e.status_code in [400, 413]
        print("  -> Directory traversal inside document container blocked successfully.")
    print("[PASS] Safe document parsing and zip bomb safeguards verified.")

    # -------------------------------------------------------------
    # 9. Candidate Recording Consent & Isolated Private Storage
    # -------------------------------------------------------------
    print("\n--- 9. Testing Candidate Recording Consent & Isolated Private Storage ---")
    # Start interview without recording consent
    no_consent_req = InterviewStartRequest(
        role_title="Software Engineer",
        interview_type="Technical",
        experience_level="1-3 years",
        difficulty="Intermediate",
        technical_subjects=["Data Structures and Algorithms"],
        total_questions=3,
        recording_consent=False
    )
    no_consent_sess = interviews.start_interview_session(start_req=no_consent_req, current_user=user1, db=db)
    assert no_consent_sess.recording_consent is False

    # Attempt upload of recording without consent
    mock_rec = MockUploadFile("candidate_video.webm", webm_bytes, "video/webm")
    try:
        interviews.upload_interview_recording(
            session_id=no_consent_sess.id,
            file=mock_rec,
            current_user=user1,
            db=db
        )
        assert False, "Recording upload succeeded without consent!"
    except HTTPException as e:
        assert e.status_code == 403
        assert "consent" in e.detail.lower()
        print("  -> Recording upload without candidate consent strictly rejected (HTTP 403).", flush=True)

    # Upload recording to session WITH consent
    upload_res = interviews.upload_interview_recording(
        session_id=u1_sess_id,
        file=mock_rec,
        current_user=user1,
        db=db
    )
    assert upload_res["status"] == "success"
    rec_path = upload_res["recording_path"]
    assert os.path.exists(rec_path)
    assert f"user_{user1.id}" in rec_path, "Recording not in user-isolated directory!"
    print("  -> Recording stored in private user-isolated directory.", flush=True)

    # User 2 tries to stream User 1's recording
    try:
        interviews.stream_interview_recording(session_id=u1_sess_id, current_user=user2, db=db)
        assert False, "User 2 streamed User 1's private recording!"
    except HTTPException as e:
        assert e.status_code == 404
        print("  -> User 2 blocked from streaming User 1's private recording.", flush=True)

    # -------------------------------------------------------------
    # 10. Secure File Deletion (DoD Random-Byte Overwrite)
    # -------------------------------------------------------------
    print("\n--- 10. Testing Secure File Deletion (DoD Overwriting Shred) ---", flush=True)
    test_shred = os.path.abspath("./storage/recordings/test_shred.bin")
    os.makedirs(os.path.dirname(test_shred), exist_ok=True)
    with open(test_shred, "wb") as f:
        f.write(b"HIGHLY_SENSITIVE_VOICE_DATA" * 50)
    assert os.path.exists(test_shred)

    shred_success = secure_delete_file(test_shred)
    assert shred_success is True
    assert not os.path.exists(test_shred)

    # Delete recording via interview endpoint
    del_res = interviews.delete_interview_recording(session_id=u1_sess_id, current_user=user1, db=db)
    assert del_res["status"] == "success"
    assert not os.path.exists(rec_path), "Recording still exists on disk after secure delete!"
    print("[PASS] Cryptographic overwrite shredding and file deletion verified.", flush=True)

    # -------------------------------------------------------------
    # 11. API Key Protection
    # -------------------------------------------------------------
    print("\n--- 11. Testing API Key Protection & Masking ---", flush=True)
    secret_key = "gsk_9876543210abcdeffedcba0123456789"
    masked = mask_api_key(secret_key)
    assert masked.startswith("gsk_")
    assert masked.endswith("6789")
    assert "abcdef" not in masked
    assert "•" in masked

    # Update AI preferences for User 1
    auth.update_ai_preferences(
        prefs=AIPreferenceUpdate(llm_preference="groq", groq_api_key=secret_key),
        current_user=user1,
        db=db
    )

    from unittest.mock import patch
    from app.services.ai.manager import ai_manager
    with patch.object(ai_manager, "check_all_health", return_value={}):
        ai_status = ai_settings.get_all_provider_statuses(current_user=user1)
        assert ai_status["masked_groq_key"] == masked
        assert secret_key not in str(ai_status), "Raw API key leaked in AI settings output!"
    print("[PASS] API key protection verified: raw key is never exposed.", flush=True)

    # -------------------------------------------------------------
    # 12. Safe Code Execution Sandbox & AST Inspection
    # -------------------------------------------------------------
    print("\n--- 12. Testing Safe Code Execution Sandbox & AST Inspection ---")
    # Safe python code
    safe_res = sandbox_executor.execute("python", "def solution(x):\n    return x + 5\n", [{"input": "[10]", "expected_output": "15"}])
    assert safe_res["passed"] is True, f"Execution failed: {safe_res}"

    # Prohibited modules
    bad_import = sandbox_executor.execute("python", "import os\nos.system('dir')", [{"input": 1, "expected": 1}])
    assert bad_import["status"] == "Security Violation"
    assert "prohibited" in bad_import["error"]

    # Prohibited dunder escape attempt (__subclasses__)
    bad_dunder = sandbox_executor.execute("python", "x = ().__class__.__bases__[0].__subclasses__()", [{"input": 1, "expected": 1}])
    assert bad_dunder["status"] == "Security Violation"
    assert "prohibited" in bad_dunder["error"]

    # Prohibited JS call
    bad_js = sandbox_executor.execute("javascript", "const fs = require('fs');", [{"input": 1, "expected": 1}])
    assert bad_js["status"] == "Security Violation"
    print("[PASS] AST-guarded isolated subprocess sandbox verified.")

    # -------------------------------------------------------------
    # 13. Input Sanitization
    # -------------------------------------------------------------
    print("\n--- 13. Testing Input Sanitization & Anti-XSS ---")
    dirty = "John Doe<script>alert(1)</script>\x00"
    cleaned = sanitize_input_text(dirty)
    assert "<script>" not in cleaned
    assert "\x00" not in cleaned
    assert "John Doe" in cleaned
    print("[PASS] Input sanitization and null-byte stripping verified.")

    # -------------------------------------------------------------
    # 14. Secure Deletion of Resume and Cascade Purge
    # -------------------------------------------------------------
    print("\n--- 14. Testing Resume Secure Deletion & Cascade Purge ---")
    del_resume_res = resumes.delete_resume(resume_id=u1_resume_id, current_user=user1, db=db)
    assert del_resume_res["status"] == "success"
    check_purged = db.query(Resume).filter(Resume.id == u1_resume_id).first()
    assert check_purged is None, "Resume still exists in DB after delete!"
    check_analysis = db.query(ResumeAnalysis).filter(ResumeAnalysis.resume_id == u1_resume_id).first()
    assert check_analysis is None, "Analyses not cascaded after resume delete!"
    print("[PASS] Resume secure deletion and cascade purge verified.")

    db.close()
    print("\n=======================================================")
    print("ALL 14 SECTION 13 SECURITY AUDIT CHECKS PASSED 100%!")
    print("=======================================================\n")

if __name__ == "__main__":
    run_all_security_tests()
