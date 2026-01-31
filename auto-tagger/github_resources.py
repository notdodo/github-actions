"""Domain models and enums used by the action."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Final

__all__ = ["BumpStrategy", "Commit", "Tag"]

_DEFAULT_TAG_TYPE: Final[str] = "commit"
_DEFAULT_BUMP_STRATEGY: Final[str] = "skip"


class BumpStrategy(StrEnum):
    """Enum containing the different version bump strategies for semver."""

    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    SKIP = _DEFAULT_BUMP_STRATEGY


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
