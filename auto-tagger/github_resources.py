"""
PyGitHub resource wrappers
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Commit:
    """Commit resource"""

    sha: str
    author_name: str
    author_email: str
    message: str
    date: datetime


def now_utf() -> datetime:
    """Factory for Datetime"""
    return datetime.now(timezone.utc)


@dataclass
class Tag:
    """Tag resource"""

    name: str
    commit: str
    message: str = ""
    type: str = "commit"
    date: datetime = field(default_factory=now_utf)
