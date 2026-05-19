import hashlib
import hmac
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import HTTPException


def verify_github_signature(secret: str, payload_body: bytes, signature_header: str) -> bool:
    if not secret or not signature_header:
        return False
    signature_parts = signature_header.split("=")
    if len(signature_parts) != 2 or signature_parts[0] != "sha256":
        return False
    expected = hmac.new(secret.encode(), payload_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_parts[1])


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def safe_json_parse(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"text": text}
