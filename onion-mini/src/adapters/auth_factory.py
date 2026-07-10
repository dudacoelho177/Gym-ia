from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from src.domain.ports import OAuthStateStore, PasswordHasher, SessionManager, UserRepository

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


def create_auth_dependencies() -> AuthDependencies:
    users_path = Path(os.getenv("AUTH_USERS_PATH", "data/auth/users.json"))
    secret_key = os.getenv("AUTH_SECRET_KEY", "dev-only-change-me")
    session_ttl_seconds = int(os.getenv("AUTH_SESSION_TTL_SECONDS", "604800"))
    pbkdf2_iterations = int(os.getenv("AUTH_PBKDF2_ITERATIONS", "600000"))
    oauth_state_ttl_seconds = int(os.getenv("OAUTH_STATE_TTL_SECONDS", "600"))

    return AuthDependencies(
        users=JsonUserRepository(users_path),
        hasher=PBKDF2PasswordHasher(iterations=pbkdf2_iterations),
        sessions=SignedCookieSessionManager(
            secret_key=secret_key,
            ttl_seconds=session_ttl_seconds,
        ),
        state_store=InMemoryOAuthStateStore(ttl_seconds=oauth_state_ttl_seconds),
    )
