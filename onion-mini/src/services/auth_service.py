from __future__ import annotations

from datetime import datetime, timezone

from src.domain import (
    AuthProvider,
    AuthSession,
    EmailAddress,
    GoogleIdentity,
    User,
)
from src.domain.ports import (
    GoogleIdentityProvider,
    OAuthStateStore,
    PasswordHasher,
    SessionManager,
    UserRepository,
)


class AuthError(Exception):
    pass


class EmailAlreadyRegistered(AuthError):
    pass


class InvalidCredentials(AuthError):
    pass


class InvalidEmail(AuthError):
    pass


class WeakPassword(AuthError):
    pass


class InvalidOAuthState(AuthError):
    pass


class UnverifiedOAuthEmail(AuthError):
    pass


def register_user(
    email: str,
    password: str,
    display_name: str,
    users: UserRepository,
    hasher: PasswordHasher,
    sessions: SessionManager,
) -> tuple[User, AuthSession]:
    email_address = _normalize_email(email)
    _validate_password(password)

    user = users.find_by_email(email_address)
    if user is not None and AuthProvider.LOCAL in user.auth_providers:
        raise EmailAlreadyRegistered("Email already registered.")

    if user is None:
        user = User(
            id=users.next_id(),
            email=email_address,
            display_name=display_name.strip(),
            password_hash=hasher.hash(password),
            auth_providers={AuthProvider.LOCAL},
        )
    else:
        user.password_hash = hasher.hash(password)
        user.auth_providers.add(AuthProvider.LOCAL)
        if display_name.strip() and not user.display_name:
            user.display_name = display_name.strip()

    user.last_login_at = _now()
    users.save(user)
    return user, sessions.create_session(user.id)


def login_with_password(
    email: str,
    password: str,
    users: UserRepository,
    hasher: PasswordHasher,
    sessions: SessionManager,
) -> tuple[User, AuthSession]:
    try:
        email_address = _normalize_email(email)
    except InvalidEmail as exc:
        raise InvalidCredentials("Invalid email or password.") from exc

    user = users.find_by_email(email_address)
    if user is None or not user.can_login_with_password():
        raise InvalidCredentials("Invalid email or password.")
    if user.password_hash is None or not hasher.verify(password, user.password_hash):
        raise InvalidCredentials("Invalid email or password.")

    user.last_login_at = _now()
    users.save(user)
    return user, sessions.create_session(user.id)


def start_google_login(
    google: GoogleIdentityProvider,
    state_store: OAuthStateStore,
) -> str:
    state, nonce = state_store.create_state()
    return google.build_authorization_url(state=state, nonce=nonce)


def finish_google_login(
    code: str,
    state: str,
    users: UserRepository,
    google: GoogleIdentityProvider,
    state_store: OAuthStateStore,
    sessions: SessionManager,
) -> tuple[User, AuthSession]:
    expected_nonce = state_store.consume_state(state)
    if expected_nonce is None:
        raise InvalidOAuthState("Invalid OAuth state.")

    identity = google.exchange_code_for_identity(code, expected_nonce)
    if not identity.email_verified:
        raise UnverifiedOAuthEmail("Google email is not verified.")

    user = _find_or_create_google_user(identity, users)
    user.last_login_at = _now()
    users.save(user)
    return user, sessions.create_session(user.id)


def current_user(
    session_token: str | None,
    users: UserRepository,
    sessions: SessionManager,
) -> User | None:
    if not session_token:
        return None

    session = sessions.verify_session(session_token)
    if session is None:
        return None
    return users.find_by_id(session.user_id)


def _find_or_create_google_user(
    identity: GoogleIdentity,
    users: UserRepository,
) -> User:
    user = users.find_by_google_subject(identity.subject)
    if user is not None:
        return user

    user = users.find_by_email(identity.email)
    if user is None:
        return User(
            id=users.next_id(),
            email=identity.email,
            display_name=identity.display_name,
            auth_providers={AuthProvider.GOOGLE},
            google_subject=identity.subject,
        )

    user.auth_providers.add(AuthProvider.GOOGLE)
    user.google_subject = identity.subject
    if identity.display_name and not user.display_name:
        user.display_name = identity.display_name
    return user


def _normalize_email(email: str) -> EmailAddress:
    email_address = EmailAddress(email).normalized()
    if not email_address or "@" not in email_address:
        raise InvalidEmail("Email is invalid.")
    local_part, _, domain = email_address.partition("@")
    if not local_part or "." not in domain:
        raise InvalidEmail("Email is invalid.")
    return EmailAddress(email_address)


def _validate_password(password: str) -> None:
    if len(password) < 8:
        raise WeakPassword("Password must have at least 8 characters.")


def _now() -> datetime:
    return datetime.now(timezone.utc)
