"""
PyGitHub resource wrappers
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Commit:
    """Commit resource"""

    sha: str
    author_name: str
    author_email: str
    message: str
    date: datetime


@dataclass
class Tag:
    """Tag resource"""

    name: str
    commit: str
    message: str = ""
    type: str = "commit"
    date: datetime = datetime.now()
