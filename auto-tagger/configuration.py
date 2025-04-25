"""
Module with the configuration of the action
"""

import os
from dataclasses import dataclass
from enum import StrEnum

from github_resources import Commit


class BumpStrategy(StrEnum):
    """Enum containing the different version bump strategy for semver"""

    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    SKIP = "skip"


@dataclass
class Configuration:
    """Configuration resource"""

    BIND_TO_MAJOR: bool = False
    DEFAULT_BUMP_STRATEGY: BumpStrategy = BumpStrategy.SKIP
    DEFAULT_BRANCH: str = "main"
    PATH: str = "."
    PREFIX: str = "v"
    REPOSITORY: str = os.environ.get("GITHUB_REPOSITORY", "")
    SUFFIX: str = ""
    DRY_RUN: bool = False

    @classmethod
    def from_env(cls) -> "Configuration":
        """Create default configuration instance with values from env variables"""
        return cls(
            BIND_TO_MAJOR=os.environ.get("INPUT_BIND_TO_MAJOR", cls.BIND_TO_MAJOR)
            == "true",
            DEFAULT_BUMP_STRATEGY=BumpStrategy(
                os.environ.get("INPUT_DEFAULT_BUMP_STRATEGY", cls.DEFAULT_BUMP_STRATEGY)
            ),
            DEFAULT_BRANCH=os.environ.get("INPUT_MAIN_BRANCH", cls.DEFAULT_BRANCH),
            PATH=os.environ.get("INPUT_PATH", cls.PATH),
            PREFIX=os.environ.get("INPUT_PREFIX", cls.PREFIX),
            REPOSITORY=os.environ.get("GITHUB_REPOSITORY", ""),
            SUFFIX=os.environ.get("INPUT_SUFFIX", cls.SUFFIX),
            DRY_RUN=os.environ.get("INPUT_DRY_RUN", cls.DRY_RUN) == "true",
        )

    def get_bump_strategy_from_commits(self, commits: list[Commit]) -> BumpStrategy:
        """Get the bump strategy from a list of commits parsing the keywords [#<strategy>]"""
        strategies = [strategy.value for strategy in BumpStrategy]
        for commit in commits:
            for strategy in strategies:
                if f"[#{strategy.lower()}]" in commit.message:
                    return BumpStrategy(strategy)
        return self.DEFAULT_BUMP_STRATEGY
