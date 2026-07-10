from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from src.domain import (
    AuthProvider,
    AuthSession,
    EmailAddress,
    GoogleIdentity,
    User,
    UserId,
)
from src.services.auth_service import (
    EmailAlreadyRegistered,
    InvalidCredentials,
    InvalidOAuthState,
    UnverifiedOAuthEmail,
    WeakPassword,
    current_user,
    finish_google_login,
    login_with_password,
    register_user,
    start_google_login,
)


class InMemoryUserRepository:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}
        self.next_value = 1

    def next_id(self) -> UserId:
        user_id = UserId(f"user-{self.next_value}")
        self.next_value += 1
        return user_id

    def find_by_id(self, user_id: UserId) -> User | None:
        return self.users.get(user_id.value)

    def find_by_email(self, email: EmailAddress) -> User | None:
        normalized = email.normalized()
        for user in self.users.values():
            if user.email.normalized() == normalized:
                return user
        return None

    def find_by_google_subject(self, subject: str) -> User | None:
        for user in self.users.values():
            if user.google_subject == subject:
                return user
        return None

    def save(self, user: User) -> None:
        self.users[user.id.value] = user


class FakePasswordHasher:
    def hash(self, password: str) -> str:
        return f"hashed:{password}"

    def verify(self, password: str, password_hash: str) -> bool:
        return password_hash == self.hash(password)


class FakeSessionManager:
    def __init__(self) -> None:
        self.sessions: dict[str, AuthSession] = {}
        self.next_value = 1

    def create_session(self, user_id: UserId) -> AuthSession:
        token = f"token-{self.next_value}"
        self.next_value += 1
        session = AuthSession(
            token=token,
            user_id=user_id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        self.sessions[token] = session
        return session

    def verify_session(self, token: str) -> AuthSession | None:
        return self.sessions.get(token)

    def revoke_session(self, token: str) -> None:
        self.sessions.pop(token, None)


class FakeGoogleIdentityProvider:
    def __init__(self, identity: GoogleIdentity | None = None) -> None:
        self.identity = identity or GoogleIdentity(
            subject="google-subject",
            email=EmailAddress("user@example.com"),
            email_verified=True,
            display_name="Google User",
        )
        self.authorization_calls: list[tuple[str, str]] = []
        self.exchange_calls: list[tuple[str, str]] = []

    def build_authorization_url(self, state: str, nonce: str) -> str:
        self.authorization_calls.append((state, nonce))
        return f"https://accounts.google.com/o/oauth2/v2/auth?state={state}&nonce={nonce}"

    def exchange_code_for_identity(self, code: str, expected_nonce: str) -> GoogleIdentity:
        self.exchange_calls.append((code, expected_nonce))
        return self.identity


class InMemoryOAuthStateStore:
    def __init__(self) -> None:
        self.states: dict[str, str] = {}
        self.next_value = 1

    def create_state(self) -> tuple[str, str]:
        state = f"state-{self.next_value}"
        nonce = f"nonce-{self.next_value}"
        self.next_value += 1
        self.states[state] = nonce
        return state, nonce

    def consume_state(self, state: str) -> str | None:
        return self.states.pop(state, None)


class AuthServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.users = InMemoryUserRepository()
        self.hasher = FakePasswordHasher()
        self.sessions = FakeSessionManager()
        self.google = FakeGoogleIdentityProvider()
        self.state_store = InMemoryOAuthStateStore()

    def test_register_user_creates_local_user_and_session(self) -> None:
        user, session = register_user(
            email=" USER@Example.COM ",
            password="password123",
            display_name="User",
            users=self.users,
            hasher=self.hasher,
            sessions=self.sessions,
        )

        self.assertEqual(user.email.value, "user@example.com")
        self.assertEqual(user.password_hash, "hashed:password123")
        self.assertEqual(user.auth_providers, {AuthProvider.LOCAL})
        self.assertEqual(session.user_id, user.id)
        self.assertIsNotNone(user.last_login_at)

    def test_register_user_rejects_weak_password(self) -> None:
        with self.assertRaises(WeakPassword):
            register_user(
                email="user@example.com",
                password="short",
                display_name="User",
                users=self.users,
                hasher=self.hasher,
                sessions=self.sessions,
            )

    def test_register_user_rejects_duplicate_local_email(self) -> None:
        register_user(
            email="user@example.com",
            password="password123",
            display_name="User",
            users=self.users,
            hasher=self.hasher,
            sessions=self.sessions,
        )

        with self.assertRaises(EmailAlreadyRegistered):
            register_user(
                email="USER@example.com",
                password="password456",
                display_name="User",
                users=self.users,
                hasher=self.hasher,
                sessions=self.sessions,
            )

    def test_register_user_links_local_provider_to_google_only_user(self) -> None:
        google_user = User(
            id=self.users.next_id(),
            email=EmailAddress("user@example.com"),
            display_name="Google User",
            auth_providers={AuthProvider.GOOGLE},
            google_subject="google-subject",
        )
        self.users.save(google_user)

        user, _ = register_user(
            email="user@example.com",
            password="password123",
            display_name="Local User",
            users=self.users,
            hasher=self.hasher,
            sessions=self.sessions,
        )

        self.assertEqual(user.id, google_user.id)
        self.assertEqual(user.auth_providers, {AuthProvider.GOOGLE, AuthProvider.LOCAL})
        self.assertEqual(user.password_hash, "hashed:password123")

    def test_login_with_password_returns_session_for_valid_credentials(self) -> None:
        registered, _ = register_user(
            email="user@example.com",
            password="password123",
            display_name="User",
            users=self.users,
            hasher=self.hasher,
            sessions=self.sessions,
        )

        user, session = login_with_password(
            email="user@example.com",
            password="password123",
            users=self.users,
            hasher=self.hasher,
            sessions=self.sessions,
        )

        self.assertEqual(user.id, registered.id)
        self.assertEqual(session.user_id, registered.id)

    def test_login_with_password_rejects_invalid_password(self) -> None:
        register_user(
            email="user@example.com",
            password="password123",
            display_name="User",
            users=self.users,
            hasher=self.hasher,
            sessions=self.sessions,
        )

        with self.assertRaises(InvalidCredentials):
            login_with_password(
                email="user@example.com",
                password="wrong-password",
                users=self.users,
                hasher=self.hasher,
                sessions=self.sessions,
            )

    def test_login_with_password_rejects_google_only_user(self) -> None:
        self.users.save(
            User(
                id=self.users.next_id(),
                email=EmailAddress("user@example.com"),
                display_name="Google User",
                auth_providers={AuthProvider.GOOGLE},
                google_subject="google-subject",
            )
        )

        with self.assertRaises(InvalidCredentials):
            login_with_password(
                email="user@example.com",
                password="password123",
                users=self.users,
                hasher=self.hasher,
                sessions=self.sessions,
            )

    def test_start_google_login_creates_state_and_returns_authorization_url(self) -> None:
        url = start_google_login(self.google, self.state_store)

        self.assertIn("state=state-1", url)
        self.assertIn("nonce=nonce-1", url)
        self.assertEqual(self.google.authorization_calls, [("state-1", "nonce-1")])

    def test_finish_google_login_rejects_invalid_state(self) -> None:
        with self.assertRaises(InvalidOAuthState):
            finish_google_login(
                code="code",
                state="missing-state",
                users=self.users,
                google=self.google,
                state_store=self.state_store,
                sessions=self.sessions,
            )

    def test_finish_google_login_rejects_unverified_email(self) -> None:
        state, _ = self.state_store.create_state()
        google = FakeGoogleIdentityProvider(
            GoogleIdentity(
                subject="google-subject",
                email=EmailAddress("user@example.com"),
                email_verified=False,
            )
        )

        with self.assertRaises(UnverifiedOAuthEmail):
            finish_google_login(
                code="code",
                state=state,
                users=self.users,
                google=google,
                state_store=self.state_store,
                sessions=self.sessions,
            )

    def test_finish_google_login_creates_new_google_user(self) -> None:
        state, _ = self.state_store.create_state()

        user, session = finish_google_login(
            code="code",
            state=state,
            users=self.users,
            google=self.google,
            state_store=self.state_store,
            sessions=self.sessions,
        )

        self.assertEqual(user.email.value, "user@example.com")
        self.assertEqual(user.auth_providers, {AuthProvider.GOOGLE})
        self.assertEqual(user.google_subject, "google-subject")
        self.assertEqual(session.user_id, user.id)
        self.assertEqual(self.google.exchange_calls, [("code", "nonce-1")])

    def test_finish_google_login_links_existing_user_by_verified_email(self) -> None:
        local_user, _ = register_user(
            email="user@example.com",
            password="password123",
            display_name="Local User",
            users=self.users,
            hasher=self.hasher,
            sessions=self.sessions,
        )
        state, _ = self.state_store.create_state()

        user, _ = finish_google_login(
            code="code",
            state=state,
            users=self.users,
            google=self.google,
            state_store=self.state_store,
            sessions=self.sessions,
        )

        self.assertEqual(user.id, local_user.id)
        self.assertEqual(user.auth_providers, {AuthProvider.LOCAL, AuthProvider.GOOGLE})
        self.assertEqual(user.google_subject, "google-subject")

    def test_finish_google_login_reuses_existing_user_by_subject(self) -> None:
        state, _ = self.state_store.create_state()
        first_user, _ = finish_google_login(
            code="code",
            state=state,
            users=self.users,
            google=self.google,
            state_store=self.state_store,
            sessions=self.sessions,
        )
        state, _ = self.state_store.create_state()

        user, _ = finish_google_login(
            code="code",
            state=state,
            users=self.users,
            google=self.google,
            state_store=self.state_store,
            sessions=self.sessions,
        )

        self.assertEqual(user.id, first_user.id)
        self.assertEqual(len(self.users.users), 1)

    def test_current_user_returns_user_for_valid_session(self) -> None:
        user, session = register_user(
            email="user@example.com",
            password="password123",
            display_name="User",
            users=self.users,
            hasher=self.hasher,
            sessions=self.sessions,
        )

        found = current_user(session.token, self.users, self.sessions)

        self.assertEqual(found, user)

    def test_current_user_returns_none_for_missing_or_invalid_session(self) -> None:
        self.assertIsNone(current_user(None, self.users, self.sessions))
        self.assertIsNone(current_user("missing-token", self.users, self.sessions))


if __name__ == "__main__":
    unittest.main()
