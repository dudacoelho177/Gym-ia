from __future__ import annotations

from typing import Protocol

from src.domain.auth import EmailAddress, User, UserId


class UserRepository(Protocol):
    def next_id(self) -> UserId:
        ...

    def find_by_id(self, user_id: UserId) -> User | None:
        ...

    def find_by_email(self, email: EmailAddress) -> User | None:
        ...

    def find_by_google_subject(self, subject: str) -> User | None:
        ...

    def save(self, user: User) -> None:
        ...
