import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Any

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-for-production")
ALGORITHM = "HS256"
TOKEN_TTL_SECONDS = 60 * 60 * 12


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _unb64(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    iterations = 210_000
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations)
    return f"pbkdf2_sha256${iterations}${salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        scheme, iterations, salt, stored = password_hash.split("$", 3)
        if scheme != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), int(iterations))
        return hmac.compare_digest(digest.hex(), stored)
    except Exception:
        return False


def create_access_token(payload: dict[str, Any]) -> str:
    header = {"alg": ALGORITHM, "typ": "JWT"}
    body = dict(payload)
    body["exp"] = int(time.time()) + TOKEN_TTL_SECONDS
    signing_input = f"{_b64(json.dumps(header, separators=(',', ':')).encode())}.{_b64(json.dumps(body, separators=(',', ':')).encode())}"
    signature = hmac.new(SECRET_KEY.encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256).digest()
    return f"{signing_input}.{_b64(signature)}"


def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        header_b64, body_b64, sig_b64 = token.split(".", 2)
        signing_input = f"{header_b64}.{body_b64}"
        expected = hmac.new(SECRET_KEY.encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256).digest()
        if not hmac.compare_digest(_b64(expected), sig_b64):
            return None
        body = json.loads(_unb64(body_b64))
        if int(body.get("exp", 0)) < int(time.time()):
            return None
        return body
    except Exception:
        return None
