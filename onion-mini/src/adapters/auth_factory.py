from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from src.domain.ports import (
    GoogleIdentityProvider,
    OAuthStateStore,
    PasswordHasher,
    SessionManager,
    UserRepository,
)

from .google_oidc import GoogleOIDCProvider
from .oauth_state import InMemoryOAuthStateStore
from .password_hashing import PBKDF2PasswordHasher
from .session_tokens import SignedCookieSessionManager
from .user_store import JsonUserRepository


@dataclass(frozen=True)
class AuthDependencies:
    users: UserRepository
    hasher: PasswordHasher
    sessions: SessionManager
    state_store: OAuthStateStore
    google: GoogleIdentityProvider


def create_auth_dependencies() -> AuthDependencies:
    env = _load_env_file(Path(".env"))
    users_path = Path(_setting(env, "AUTH_USERS_PATH", "USER_STORE_PATH", "data/auth/users.json"))
    secret_key = _setting(env, "AUTH_SECRET_KEY", "SECRET_KEY", "dev-only-change-me")
    session_ttl_seconds = int(_setting(env, "AUTH_SESSION_TTL_SECONDS", default="604800"))
    pbkdf2_iterations = int(_setting(env, "AUTH_PBKDF2_ITERATIONS", default="600000"))
    oauth_state_ttl_seconds = int(_setting(env, "OAUTH_STATE_TTL_SECONDS", default="600"))
    google_timeout_seconds = float(_setting(env, "GOOGLE_OIDC_TIMEOUT_SECONDS", default="10"))

    return AuthDependencies(
        users=JsonUserRepository(users_path),
        hasher=PBKDF2PasswordHasher(iterations=pbkdf2_iterations),
        sessions=SignedCookieSessionManager(
            secret_key=secret_key,
            ttl_seconds=session_ttl_seconds,
        ),
        state_store=InMemoryOAuthStateStore(ttl_seconds=oauth_state_ttl_seconds),
        google=GoogleOIDCProvider(
            client_id=_setting(env, "GOOGLE_CLIENT_ID", default=""),
            client_secret=_setting(env, "GOOGLE_CLIENT_SECRET", default=""),
            redirect_uri=_setting(
                env,
                "GOOGLE_REDIRECT_URI",
                default="http://127.0.0.1:8501/auth/google/callback",
            ),
            timeout_seconds=google_timeout_seconds,
        ),
    )


def _setting(env: dict[str, str], *names: str, default: str = "") -> str:
    for name in names:
        value = os.getenv(name)
        if value is not None:
            return value
        if name in env:
            return env[name]
    return default


def _load_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        name, value = stripped.split("=", 1)
        values[name.strip()] = _clean_env_value(value.strip())
    return values


def _clean_env_value(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value
