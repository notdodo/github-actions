"""Thin, typed resource wrappers for PyGitHub objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Final

__all__ = ["Commit", "Tag"]

_DEFAULT_TAG_TYPE: Final[str] = "commit"


@dataclass
class Commit:
    """Commit resource."""

    sha: str
    author_name: str
    author_email: str
    message: str
    date: datetime


def now_utc() -> datetime:
    """Return the current UTC datetime; kept as a factory for dataclass defaults."""
    return datetime.now(UTC)


@dataclass
class Tag:
    """Tag resource."""

    name: str
    commit: str
    message: str = ""
    type: str = _DEFAULT_TAG_TYPE
    date: datetime = field(default_factory=now_utc)
