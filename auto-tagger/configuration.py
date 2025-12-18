"""Configuration helpers for the GitHub Action."""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

    from github_resources import Commit


class BumpStrategy(StrEnum):
    """Enum containing the different version bump strategy for semver."""

    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    SKIP = "skip"


def _env_flag(var_name: str, *, default: bool) -> bool:
    """Return a boolean flag from an environment variable using a safe default."""
    return os.environ.get(var_name, str(default)).strip().lower() == "true"


@dataclass
class Configuration:
    """Configuration resource populated from the environment."""

    BIND_TO_MAJOR: bool = False
    DEFAULT_BUMP_STRATEGY: BumpStrategy = BumpStrategy.SKIP
    DEFAULT_BRANCH: str = "main"
    PATH: str = "."
    PREFIX: str = "v"
    REPOSITORY: str = os.environ.get("GITHUB_REPOSITORY", "")
    SUFFIX: str = ""
    DRY_RUN: bool = False

    @classmethod
    def from_env(cls) -> Configuration:
        """Create default configuration instance with values from env variables."""
        return cls(
            BIND_TO_MAJOR=_env_flag("INPUT_BIND_TO_MAJOR", default=cls.BIND_TO_MAJOR),
            DEFAULT_BUMP_STRATEGY=BumpStrategy(
                os.environ.get("INPUT_DEFAULT_BUMP_STRATEGY", cls.DEFAULT_BUMP_STRATEGY)
            ),
            DEFAULT_BRANCH=os.environ.get("INPUT_MAIN_BRANCH", cls.DEFAULT_BRANCH),
            PATH=os.environ.get("INPUT_PATH", cls.PATH),
            PREFIX=os.environ.get("INPUT_PREFIX", cls.PREFIX),
            REPOSITORY=os.environ.get("GITHUB_REPOSITORY", ""),
            SUFFIX=os.environ.get("INPUT_SUFFIX", cls.SUFFIX),
            DRY_RUN=_env_flag("INPUT_DRY_RUN", default=cls.DRY_RUN),
        )

    def get_bump_strategy_from_commits(self, commits: Iterable[Commit]) -> BumpStrategy:
        """Get the bump strategy from a list of commits parsing the keywords [#<strategy>]."""
        strategies = tuple(strategy.value for strategy in BumpStrategy)
        for commit in commits:
            lowered_message = commit.message.lower()
            for strategy in strategies:
                if f"[#{strategy}]" in lowered_message:
                    return BumpStrategy(strategy)
        return self.DEFAULT_BUMP_STRATEGY
