from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class AuthProvider(str, Enum):
    LOCAL = "local"
    GOOGLE = "google"


@dataclass(frozen=True)
class UserId:
    value: str


@dataclass(frozen=True)
class EmailAddress:
    value: str

    def normalized(self) -> str:
        return self.value.strip().lower()


@dataclass
class User:
    id: UserId
    email: EmailAddress
    display_name: str = ""
    password_hash: str | None = None
    auth_providers: set[AuthProvider] = field(default_factory=set)
    google_subject: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_login_at: datetime | None = None

    def can_login_with_password(self) -> bool:
        return self.password_hash is not None and AuthProvider.LOCAL in self.auth_providers

    def can_login_with_google(self) -> bool:
        return self.google_subject is not None and AuthProvider.GOOGLE in self.auth_providers


@dataclass(frozen=True)
class AuthSession:
    token: str
    user_id: UserId
    expires_at: datetime


@dataclass(frozen=True)
class GoogleIdentity:
    subject: str
    email: EmailAddress
    email_verified: bool
    display_name: str = ""
