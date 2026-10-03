from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from src.domain import AuthProvider, EmailAddress, User, UserId


class JsonUserRepository:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def next_id(self) -> UserId:
        return UserId(str(uuid.uuid4()))

    def find_by_id(self, user_id: UserId) -> User | None:
        return self._users_by_id().get(user_id.value)

    def find_by_email(self, email: EmailAddress) -> User | None:
        normalized = email.normalized()
        for user in self._users_by_id().values():
            if user.email.normalized() == normalized:
                return user
        return None

    def find_by_google_subject(self, subject: str) -> User | None:
        for user in self._users_by_id().values():
            if user.google_subject == subject:
                return user
        return None

    def save(self, user: User) -> None:
        users = self._users_by_id()
        users[user.id.value] = user
        self._write_users(users)

    def _users_by_id(self) -> dict[str, User]:
        if not self.path.exists():
            return {}

        data = json.loads(self.path.read_text(encoding="utf-8"))
        users = data.get("users", [])
        return {
            item["id"]: _user_from_dict(item)
            for item in users
        }

    def _write_users(self, users: dict[str, User]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "users": [
                _user_to_dict(user)
                for user in sorted(users.values(), key=lambda item: item.id.value)
            ]
        }
        with NamedTemporaryFile(
            "w",
            delete=False,
            dir=self.path.parent,
            encoding="utf-8",
        ) as temp_file:
            json.dump(payload, temp_file, ensure_ascii=False, indent=2)
            temp_file.write("\n")
            temp_name = temp_file.name
        os.replace(temp_name, self.path)


def _user_to_dict(user: User) -> dict[str, Any]:
    return {
        "id": user.id.value,
        "email": user.email.value,
        "display_name": user.display_name,
        "password_hash": user.password_hash,
        "auth_providers": sorted(provider.value for provider in user.auth_providers),
        "google_subject": user.google_subject,
        "created_at": user.created_at.isoformat(),
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
    }


def _user_from_dict(data: dict[str, Any]) -> User:
    return User(
        id=UserId(data["id"]),
        email=EmailAddress(data["email"]),
        display_name=data.get("display_name", ""),
        password_hash=data.get("password_hash"),
        auth_providers={
            AuthProvider(provider)
            for provider in data.get("auth_providers", [])
        },
        google_subject=data.get("google_subject"),
        created_at=_parse_datetime(data["created_at"]),
        last_login_at=_parse_optional_datetime(data.get("last_login_at")),
    )


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _parse_optional_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    return _parse_datetime(value)
