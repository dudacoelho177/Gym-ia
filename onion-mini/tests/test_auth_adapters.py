from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.adapters import (
    InMemoryOAuthStateStore,
    JsonUserRepository,
    PBKDF2PasswordHasher,
    SignedCookieSessionManager,
    create_auth_dependencies,
)
from src.domain import AuthProvider, EmailAddress, User, UserId


class AuthAdapterTests(unittest.TestCase):
    def test_json_user_repository_persists_and_loads_user(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "auth" / "users.json"
            repository = JsonUserRepository(path)
            user = User(
                id=UserId("user-1"),
                email=EmailAddress("user@example.com"),
                display_name="User",
                password_hash="hashed-password",
                auth_providers={AuthProvider.LOCAL},
            )

            repository.save(user)
            reloaded = JsonUserRepository(path)

            self.assertEqual(reloaded.find_by_id(UserId("user-1")), user)
            self.assertEqual(reloaded.find_by_email(EmailAddress("USER@example.com")), user)
            self.assertTrue(path.exists())

    def test_json_user_repository_finds_by_google_subject(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = JsonUserRepository(Path(directory) / "users.json")
            user = User(
                id=UserId("user-1"),
                email=EmailAddress("user@example.com"),
                auth_providers={AuthProvider.GOOGLE},
                google_subject="google-subject",
            )

            repository.save(user)

            self.assertEqual(repository.find_by_google_subject("google-subject"), user)

    def test_pbkdf2_password_hasher_hashes_and_verifies_passwords(self) -> None:
        hasher = PBKDF2PasswordHasher(iterations=1_000)

        password_hash = hasher.hash("password123")

        self.assertNotEqual(password_hash, "password123")
        self.assertTrue(password_hash.startswith("pbkdf2_sha256$1000$"))
        self.assertTrue(hasher.verify("password123", password_hash))
        self.assertFalse(hasher.verify("wrong-password", password_hash))

    def test_pbkdf2_password_hasher_uses_unique_salts(self) -> None:
        hasher = PBKDF2PasswordHasher(iterations=1_000)

        first_hash = hasher.hash("password123")
        second_hash = hasher.hash("password123")

        self.assertNotEqual(first_hash, second_hash)
        self.assertTrue(hasher.verify("password123", first_hash))
        self.assertTrue(hasher.verify("password123", second_hash))

    def test_signed_cookie_session_manager_round_trips_valid_token(self) -> None:
        manager = SignedCookieSessionManager(secret_key="secret", ttl_seconds=60)

        session = manager.create_session(UserId("user-1"))
        verified = manager.verify_session(session.token)

        self.assertIsNotNone(verified)
        self.assertEqual(verified.user_id, UserId("user-1"))
        self.assertEqual(verified.token, session.token)

    def test_signed_cookie_session_manager_rejects_tampered_token(self) -> None:
        manager = SignedCookieSessionManager(secret_key="secret", ttl_seconds=60)
        session = manager.create_session(UserId("user-1"))
        payload, signature = session.token.split(".", 1)
        tampered = f"{payload}.{signature[:-1]}x"

        self.assertIsNone(manager.verify_session(tampered))

    def test_signed_cookie_session_manager_rejects_expired_token(self) -> None:
        manager = SignedCookieSessionManager(secret_key="secret", ttl_seconds=-1)

        session = manager.create_session(UserId("user-1"))

        self.assertIsNone(manager.verify_session(session.token))

    def test_oauth_state_store_consumes_state_once(self) -> None:
        state_store = InMemoryOAuthStateStore(ttl_seconds=60)

        state, nonce = state_store.create_state()

        self.assertEqual(state_store.consume_state(state), nonce)
        self.assertIsNone(state_store.consume_state(state))

    def test_oauth_state_store_rejects_expired_state(self) -> None:
        state_store = InMemoryOAuthStateStore(ttl_seconds=-1)

        state, _ = state_store.create_state()

        self.assertIsNone(state_store.consume_state(state))

    def test_auth_factory_reads_environment(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "users.json"
            with patch.dict(
                "os.environ",
                {
                    "AUTH_USERS_PATH": str(path),
                    "AUTH_SECRET_KEY": "factory-secret",
                    "AUTH_SESSION_TTL_SECONDS": "120",
                    "AUTH_PBKDF2_ITERATIONS": "1000",
                    "OAUTH_STATE_TTL_SECONDS": "30",
                },
                clear=True,
            ):
                deps = create_auth_dependencies()

            self.assertIsInstance(deps.users, JsonUserRepository)
            self.assertIsInstance(deps.hasher, PBKDF2PasswordHasher)
            self.assertIsInstance(deps.sessions, SignedCookieSessionManager)
            self.assertIsInstance(deps.state_store, InMemoryOAuthStateStore)


if __name__ == "__main__":
    unittest.main()
