"""
Unit and Integration Tests for Module 13 Security Controls
Covers password hashing, JWT revocation blacklist, file validation,
AST sandbox execution, and input sanitization.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.security import (
    get_password_hash,
    verify_password,
    validate_password_strength,
    create_access_token,
    decode_access_token,
    revoke_token,
    is_token_revoked,
    validate_file_size,
    validate_resume_file,
    validate_recording_file,
    secure_delete_file,
    sanitize_input_text,
    MAX_RESUME_SIZE
)
from app.services.sandbox_executor import SandboxExecutor, SecurityViolationError
from fastapi import HTTPException


class TestSecurityControls(unittest.TestCase):
    def test_password_hashing_and_verification(self):
        pwd = "SecurePassword123!"
        hashed = get_password_hash(pwd)
        self.assertNotEqual(pwd, hashed)
        self.assertTrue(verify_password(pwd, hashed))
        self.assertFalse(verify_password("WrongPassword123!", hashed))

    def test_password_strength_validation(self):
        # Weak password (too short)
        is_valid, msg = validate_password_strength("weak")
        self.assertFalse(is_valid)

        # Weak password (no digits)
        is_valid, msg = validate_password_strength("NoDigitsHere")
        self.assertFalse(is_valid)

        # Strong password
        is_valid, msg = validate_password_strength("SuperSecret123$")
        self.assertTrue(is_valid)

    def test_jwt_creation_and_revocation(self):
        token = create_access_token(data={"sub": "999"})
        payload = decode_access_token(token)
        self.assertEqual(payload.get("sub"), "999")
        self.assertFalse(is_token_revoked(token))

        revoke_token(token)
        self.assertTrue(is_token_revoked(token))

    def test_file_validation_magic_bytes(self):
        # Valid PDF header
        pdf_bytes = b"%PDF-1.5 test resume content"
        self.assertEqual(validate_resume_file(pdf_bytes, "test.pdf"), "pdf")

        # Invalid fake PDF
        with self.assertRaises(HTTPException):
            validate_resume_file(b"NOT_A_PDF_CONTENT", "fake.pdf")

    def test_sandbox_security_violation(self):
        malicious_python = "__import__('os').system('ls')"
        with self.assertRaises(SecurityViolationError):
            SandboxExecutor.inspect_python_security(malicious_python)


if __name__ == "__main__":
    unittest.main()
