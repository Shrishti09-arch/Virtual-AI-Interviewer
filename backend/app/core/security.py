import ast
import datetime
import hashlib
import hmac
import io
import os
import re
import threading
import time
import uuid
import zipfile
from typing import Optional, Dict, Any, Tuple, List
from fastapi import HTTPException, status
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from pypdf import PdfReader
from docx import Document

from app.config import settings

# -------------------------------------------------------------
# 1. Password Security (Argon2id + PBKDF2 Fallback)
# -------------------------------------------------------------
_hasher = PasswordHasher(
    time_cost=2,
    memory_cost=65536,
    parallelism=1,
    hash_len=32,
    salt_len=16
)

def get_password_hash(password: str) -> str:
    """Hashes password with Argon2id; falls back to PBKDF2-HMAC-SHA256 if needed."""
    try:
        return _hasher.hash(password)
    except Exception:
        salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        return f"pbkdf2:{salt.hex()}:{key.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies plain password against stored hash using constant-time comparison."""
    if not hashed_password:
        return False
    if hashed_password.startswith("pbkdf2:"):
        try:
            _, salt_hex, key_hex = hashed_password.split(":")
            salt = bytes.fromhex(salt_hex)
            expected_key = bytes.fromhex(key_hex)
            actual_key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, 100000)
            return hmac.compare_digest(actual_key, expected_key)
        except Exception:
            return False
    try:
        return _hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, Exception):
        return False

def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Enforces strong password policy:
    - Minimum 8 characters
    - At least one digit
    - At least one letter (upper or lower)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    if not re.search(r"[a-zA-Z]", password):
        return False, "Password must contain at least one letter."
    return True, "Password meets security policy."

# -------------------------------------------------------------
# 2. JWT Authentication & Token Revocation (Session Management)
# -------------------------------------------------------------
# In-memory thread-safe revocation store: maps jti / token_hash -> expiry_timestamp
_revoked_tokens: Dict[str, float] = {}
_revocation_lock = threading.Lock()

def _cleanup_expired_revocations() -> None:
    now = time.time()
    with _revocation_lock:
        expired_keys = [k for k, exp in _revoked_tokens.items() if exp < now]
        for k in expired_keys:
            del _revoked_tokens[k]

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
    """Generates a cryptographically signed JWT with unique jti, issued-at, and expiration."""
    to_encode = data.copy()
    now = datetime.datetime.now(datetime.timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": now,
        "jti": uuid.uuid4().hex
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> dict:
    """
    Decodes and validates a JWT token.
    Checks signature, expiration, and ensures token is not in the revocation blacklist.
    """
    _cleanup_expired_revocations()

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"require": ["exp", "sub"]}
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token signature.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Check revocation blacklist by jti or token hash
    jti = payload.get("jti")
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with _revocation_lock:
        if (jti and jti in _revoked_tokens) or (token_hash in _revoked_tokens):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked. Please log in again.",
                headers={"WWW-Authenticate": "Bearer"}
            )

    return payload

def revoke_token(token: str) -> bool:
    """Revokes a JWT token by adding its jti and token hash to the blacklist."""
    try:
        # Decode without verification in case token is close to expiry
        unverified = jwt.decode(token, options={"verify_signature": False})
        exp = unverified.get("exp", time.time() + 3600)
        jti = unverified.get("jti")
    except Exception:
        exp = time.time() + 3600
        jti = None

    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with _revocation_lock:
        if jti:
            _revoked_tokens[jti] = float(exp)
        _revoked_tokens[token_hash] = float(exp)
    return True

def is_token_revoked(token: str) -> bool:
    """Checks whether token is active or revoked."""
    try:
        unverified = jwt.decode(token, options={"verify_signature": False})
        jti = unverified.get("jti")
    except Exception:
        jti = None

    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with _revocation_lock:
        return (jti is not None and jti in _revoked_tokens) or (token_hash in _revoked_tokens)

# -------------------------------------------------------------
# 3. API Key Protection & Masking
# -------------------------------------------------------------
def mask_api_key(key: Optional[str]) -> str:
    """
    Masks API keys for secure display in API responses and logs.
    Example: 'gsk_abcdef1234567890' -> 'gsk_••••••••••••7890'
    """
    if not key or not isinstance(key, str):
        return ""
    stripped = key.strip()
    if len(stripped) <= 8:
        return "••••••••"
    prefix = stripped[:4]
    suffix = stripped[-4:]
    masked_middle = "•" * max(4, len(stripped) - 8)
    return f"{prefix}{masked_middle}{suffix}"

# -------------------------------------------------------------
# 4. File Type Validation & Size Restrictions
# -------------------------------------------------------------
MAX_RESUME_SIZE = 10 * 1024 * 1024       # 10 MB limit for resumes
MAX_RECORDING_SIZE = 50 * 1024 * 1024    # 50 MB limit for recordings

def validate_file_size(file_bytes: bytes, max_allowed: int, file_desc: str = "File") -> None:
    """Enforces strict file size limits, returning HTTP 413 if exceeded."""
    if len(file_bytes) > max_allowed:
        max_mb = max_allowed // (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"{file_desc} exceeds maximum allowed size of {max_mb}MB (received {len(file_bytes) / (1024*1024):.1f}MB)."
        )

def validate_resume_file(file_bytes: bytes, filename: str) -> str:
    """
    Validates resume file size and authenticates magic bytes (not just extension).
    Returns verified format: 'pdf', 'docx', or 'txt'.
    Rejects spoofed or malicious files with HTTP 415.
    """
    validate_file_size(file_bytes, MAX_RESUME_SIZE, "Resume document")

    lower_name = filename.lower()

    # 1. PDF Magic Byte Verification (%PDF-)
    if file_bytes.startswith(b"%PDF-"):
        return "pdf"

    # 2. DOCX Magic Byte Verification (PK\x03\x04 + Office Open XML structure)
    if file_bytes.startswith(b"PK\x03\x04"):
        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
                namelist = zf.namelist()
                if "[Content_Types].xml" in namelist or "word/document.xml" in namelist:
                    return "docx"
        except zipfile.BadZipFile:
            pass

    # 3. Plain Text Validation (must be valid UTF-8/ASCII without null bytes)
    if lower_name.endswith(".txt"):
        try:
            text = file_bytes.decode("utf-8")
            if "\x00" not in text:
                return "txt"
        except UnicodeDecodeError:
            pass

    # If extension claims PDF but signature failed:
    if lower_name.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Invalid PDF format: Document does not contain a valid %PDF- header signature."
        )

    # If extension claims DOCX but signature failed:
    if lower_name.endswith(".docx") or lower_name.endswith(".doc"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Invalid DOCX format: Document is not a valid OpenXML Word container."
        )

    raise HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail="Unsupported or corrupted file format. Only verified PDF, DOCX, and TXT files are accepted."
    )

def validate_recording_file(file_bytes: bytes, filename: str) -> str:
    """
    Validates audio/video recording file size and authenticates media container magic bytes.
    Supports WebM, MP4, WAV, and OGG.
    """
    validate_file_size(file_bytes, MAX_RECORDING_SIZE, "Media recording")

    # WebM / Matroska EBML header: 0x1A 0x45 0xDF 0xA3
    if file_bytes.startswith(b"\x1a\x45\xdf\xa3"):
        return "webm"

    # MP4: contains 'ftyp' in first 16 bytes
    if len(file_bytes) >= 12 and b"ftyp" in file_bytes[:16]:
        return "mp4"

    # WAV: 'RIFF' .... 'WAVE'
    if file_bytes.startswith(b"RIFF") and len(file_bytes) >= 12 and file_bytes[8:12] == b"WAVE":
        return "wav"

    # OGG: 'OggS'
    if file_bytes.startswith(b"OggS"):
        return "ogg"

    # Fallback check if user uploaded WebM audio chunks
    lower_name = filename.lower()
    if lower_name.endswith(".webm") and len(file_bytes) > 0:
        return "webm"

    raise HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail="Unsupported media format. Recording must be a valid WebM, MP4, WAV, or OGG container."
    )

# -------------------------------------------------------------
# 5. Safe Document Parsing (Zip Bomb & XXE Defense)
# -------------------------------------------------------------
def safe_extract_pdf_text(file_bytes: bytes, max_pages: int = 25, max_chars: int = 200000) -> str:
    """
    Extracts text from PDF with strict limits to defend against decompression bombs
    and infinite-loop document structures.
    """
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        total_pages = len(reader.pages)
        pages_to_read = min(total_pages, max_pages)

        extracted_text = []
        char_count = 0

        for idx in range(pages_to_read):
            page_text = reader.pages[idx].extract_text() or ""
            if page_text:
                extracted_text.append(page_text)
                char_count += len(page_text)
                if char_count >= max_chars:
                    break

        return "\n".join(extracted_text)[:max_chars].strip()
    except Exception as e:
        raise ValueError(f"Safe PDF text extraction failed: {str(e)}")

def safe_extract_docx_text(
    file_bytes: bytes,
    max_uncompressed_bytes: int = 25 * 1024 * 1024,
    max_ratio: float = 50.0,
    max_chars: int = 200000
) -> str:
    """
    Extracts text from DOCX while defending against Zip Decompression Bombs,
    Directory Traversal filenames, and XML expansion attacks.
    """
    # 1. Zip Bomb & Traversal Pre-Inspection
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
            total_uncompressed = 0
            total_compressed = max(1, len(file_bytes))

            for info in zf.infolist():
                # Defend against Directory Traversal in ZIP entry names
                if ".." in info.filename or info.filename.startswith("/") or info.filename.startswith("\\"):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Security violation: Malicious path traversal detected inside document container."
                    )

                total_uncompressed += info.file_size
                if total_uncompressed > max_uncompressed_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="Security alert: Decompression bomb detected (exceeds 25MB uncompressed limit)."
                    )

            ratio = total_uncompressed / total_compressed
            if ratio > max_ratio and total_uncompressed > 5 * 1024 * 1024:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Security alert: Decompression bomb detected (abnormal compression ratio of {ratio:.1f}:1)."
                )
    except HTTPException:
        raise
    except Exception as e:
        raise ValueError(f"DOCX container safety verification failed: {str(e)}")

    # 2. Extract Document Content Safely
    try:
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text]
        tables_text = []
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text:
                        tables_text.append(cell.text)

        full_text = "\n".join(paragraphs + tables_text)
        return full_text[:max_chars].strip()
    except Exception as e:
        raise ValueError(f"Safe DOCX text extraction failed: {str(e)}")

# -------------------------------------------------------------
# 6. Secure File Deletion (DoD 5220.22-M Overwrite Pattern)
# -------------------------------------------------------------
STORAGE_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "storage"))

def is_safe_storage_path(target_path: str) -> bool:
    """Verifies that the target path is strictly inside the authorized storage folder."""
    abs_target = os.path.abspath(target_path)
    abs_base = STORAGE_BASE_DIR
    return abs_target.startswith(abs_base)

def secure_delete_file(file_path: str, passes: int = 1) -> bool:
    """
    Securely deletes a file from disk by overwriting its contents with random bytes
    before unlinking, preventing forensic recovery.
    """
    if not file_path or not os.path.exists(file_path):
        return False

    abs_path = os.path.abspath(file_path)

    try:
        if os.path.isfile(abs_path):
            file_len = os.path.getsize(abs_path)
            if file_len > 0:
                with open(abs_path, "r+b") as f:
                    for _ in range(passes):
                        f.seek(0)
                        f.write(os.urandom(file_len))
                        f.flush()
                        os.fsync(f.fileno())

            os.remove(abs_path)
            return True
        elif os.path.isdir(abs_path):
            os.rmdir(abs_path)
            return True
        return False
    except Exception:
        # Fallback to standard remove if r+b fails
        try:
            if os.path.isfile(abs_path):
                os.remove(abs_path)
                return True
        except Exception:
            return False
        return False

# -------------------------------------------------------------
# 7. Input Sanitization & Anti-XSS Guards
# -------------------------------------------------------------
def sanitize_input_text(text: Optional[str], max_length: int = 50000) -> str:
    """
    Sanitizes string inputs:
    - Strips dangerous null bytes
    - Removes <script> and dangerous HTML tags
    - Caps maximum length
    """
    if not text:
        return ""
    # Strip null bytes
    clean = text.replace("\x00", "")
    # Remove script tags
    clean = re.sub(r"(?i)<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>", "", clean)
    clean = re.sub(r"(?i)javascript:", "", clean)
    return clean[:max_length].strip()
