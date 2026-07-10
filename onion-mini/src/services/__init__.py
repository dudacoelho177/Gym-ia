from .auth_service import (
    AuthError,
    EmailAlreadyRegistered,
    InvalidCredentials,
    InvalidEmail,
    InvalidOAuthState,
    UnverifiedOAuthEmail,
    WeakPassword,
    current_user,
    finish_google_login,
    login_with_password,
    register_user,
    start_google_login,
)
from .generator import generate_discovery_roteiro

__all__ = [
    "AuthError",
    "EmailAlreadyRegistered",
    "InvalidCredentials",
    "InvalidEmail",
    "InvalidOAuthState",
    "UnverifiedOAuthEmail",
    "WeakPassword",
    "current_user",
    "finish_google_login",
    "generate_discovery_roteiro",
    "login_with_password",
    "register_user",
    "start_google_login",
]
