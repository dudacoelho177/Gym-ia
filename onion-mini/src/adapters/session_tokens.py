from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from typing import Any

from src.domain import AuthSession, UserId


class SignedCookieSessionManager:
    def __init__(self, secret_key: str, ttl_seconds: int = 604_800) -> None:
        if not secret_key:
            raise ValueError("secret_key is required.")
        self.secret_key = secret_key.encode("utf-8")
        self.ttl_seconds = ttl_seconds

    def create_session(self, user_id: UserId) -> AuthSession:
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=self.ttl_seconds)
        payload = {
            "sub": user_id.value,
            "exp": int(expires_at.timestamp()),
        }
        payload_value = _b64encode_json(payload)
        signature = self._sign(payload_value)
        token = f"{payload_value}.{signature}"
        return AuthSession(token=token, user_id=user_id, expires_at=expires_at)

    def verify_session(self, token: str) -> AuthSession | None:
        try:
            payload_value, signature = token.split(".", 1)
        except ValueError:
            return None

        expected_signature = self._sign(payload_value)
        if not hmac.compare_digest(signature, expected_signature):
            return None

        try:
            payload = _b64decode_json(payload_value)
            user_id = UserId(str(payload["sub"]))
            expires_at = datetime.fromtimestamp(int(payload["exp"]), tz=timezone.utc)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            return None

        if expires_at <= datetime.now(timezone.utc):
            return None
        return AuthSession(token=token, user_id=user_id, expires_at=expires_at)

    def revoke_session(self, token: str) -> None:
        return None

    def _sign(self, payload_value: str) -> str:
        digest = hmac.new(
            self.secret_key,
            payload_value.encode("ascii"),
            hashlib.sha256,
        ).digest()
        return _b64encode_bytes(digest)


def _b64encode_json(payload: dict[str, Any]) -> str:
    data = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return _b64encode_bytes(data)


def _b64decode_json(value: str) -> dict[str, Any]:
    return json.loads(_b64decode_bytes(value).decode("utf-8"))


def _b64encode_bytes(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64decode_bytes(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)
