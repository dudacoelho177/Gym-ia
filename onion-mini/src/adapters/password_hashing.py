from __future__ import annotations

import base64
import hashlib
import hmac
import secrets


class PBKDF2PasswordHasher:
    algorithm = "pbkdf2_sha256"

    def __init__(self, iterations: int = 600_000, salt_bytes: int = 16) -> None:
        self.iterations = iterations
        self.salt_bytes = salt_bytes

    def hash(self, password: str) -> str:
        salt = secrets.token_bytes(self.salt_bytes)
        digest = self._digest(password, salt, self.iterations)
        return "$".join(
            [
                self.algorithm,
                str(self.iterations),
                _b64encode(salt),
                _b64encode(digest),
            ]
        )

    def verify(self, password: str, password_hash: str) -> bool:
        try:
            algorithm, iterations_value, salt_value, digest_value = password_hash.split("$")
            if algorithm != self.algorithm:
                return False
            iterations = int(iterations_value)
            salt = _b64decode(salt_value)
            expected_digest = _b64decode(digest_value)
        except (ValueError, TypeError):
            return False

        actual_digest = self._digest(password, salt, iterations)
        return hmac.compare_digest(actual_digest, expected_digest)

    def _digest(self, password: str, salt: bytes, iterations: int) -> bytes:
        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
        )


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)
