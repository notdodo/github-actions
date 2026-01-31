"""Configuration helpers for the GitHub Action."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from github_resources import Commit

from github_resources import BumpStrategy

_TRUE_VALUES = {"1", "true", "yes", "y", "on"}
_FALSE_VALUES = {"0", "false", "no", "n", "off"}
_DEFAULT_BIND_TO_MAJOR = False
_DEFAULT_BUMP_STRATEGY = BumpStrategy.SKIP
_DEFAULT_BRANCH = "main"
_DEFAULT_PATH = "."
_DEFAULT_PREFIX = "v"
_DEFAULT_SUFFIX = ""
_DEFAULT_DRY_RUN = False


class ConfigurationError(ValueError):
    """Raised when configuration values are missing or invalid."""


def _env_flag(env: Mapping[str, str], var_name: str, *, default: bool) -> bool:
    """Return a boolean flag from an environment variable using a safe default."""
    value = env.get(var_name)
    if value is None:
        return default
    lowered = value.strip().lower()
    if lowered in _TRUE_VALUES:
        return True
    if lowered in _FALSE_VALUES:
        return False
    return default


def _env_str(
    env: Mapping[str, str], var_name: str, default: str, *, allow_empty: bool = False
) -> str:
    """Return a string value from env, falling back to default when empty."""
    value = env.get(var_name)
    if value is None:
        return default
    stripped = value.strip()
    if not stripped and not allow_empty:
        return default
    return stripped


def _parse_bump_strategy(value: str | None, *, default: BumpStrategy) -> BumpStrategy:
    """Parse a bump strategy value; fall back to default when invalid."""
    if value is None:
        return default
    try:
        return BumpStrategy(value.strip().lower())
    except ValueError:
        return default


@dataclass
class Configuration:
    """Configuration resource populated from the environment."""

    BIND_TO_MAJOR: bool = _DEFAULT_BIND_TO_MAJOR
    DEFAULT_BUMP_STRATEGY: BumpStrategy = _DEFAULT_BUMP_STRATEGY
    DEFAULT_BRANCH: str = _DEFAULT_BRANCH
    PATH: str = _DEFAULT_PATH
    PREFIX: str = _DEFAULT_PREFIX
    REPOSITORY: str = ""
    SUFFIX: str = _DEFAULT_SUFFIX
    DRY_RUN: bool = _DEFAULT_DRY_RUN

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Configuration:
        """Create default configuration instance with values from env variables."""
        environment = env or os.environ
        return cls(
            BIND_TO_MAJOR=_env_flag(
                environment, "INPUT_BIND_TO_MAJOR", default=_DEFAULT_BIND_TO_MAJOR
            ),
            DEFAULT_BUMP_STRATEGY=_parse_bump_strategy(
                environment.get("INPUT_DEFAULT_BUMP_STRATEGY"),
                default=_DEFAULT_BUMP_STRATEGY,
            ),
            DEFAULT_BRANCH=_env_str(
                environment, "INPUT_DEFAULT_BRANCH", _DEFAULT_BRANCH
            ),
            PATH=_env_str(environment, "INPUT_PATH", _DEFAULT_PATH),
            PREFIX=_env_str(
                environment, "INPUT_PREFIX", _DEFAULT_PREFIX, allow_empty=True
            ),
            REPOSITORY=_env_str(environment, "GITHUB_REPOSITORY", ""),
            SUFFIX=_env_str(
                environment, "INPUT_SUFFIX", _DEFAULT_SUFFIX, allow_empty=True
            ),
            DRY_RUN=_env_flag(environment, "INPUT_DRY_RUN", default=_DEFAULT_DRY_RUN),
        )

    def get_bump_strategy_from_commits(self, commits: Iterable[Commit]) -> BumpStrategy:
        """Return the bump strategy from commits using [#<strategy>] markers."""
        strategies_in_commits: set[BumpStrategy] = set()
        for commit in commits:
            lowered_message = commit.message.lower()
            for strategy in BumpStrategy:
                if f"[#{strategy.value}]" in lowered_message:
                    strategies_in_commits.add(strategy)
        if BumpStrategy.SKIP in strategies_in_commits:
            return BumpStrategy.SKIP
        for strategy in (BumpStrategy.MAJOR, BumpStrategy.MINOR, BumpStrategy.PATCH):
            if strategy in strategies_in_commits:
                return strategy
        return self.DEFAULT_BUMP_STRATEGY

    @property
    def commit_path_filter(self) -> str | None:
        """Return a path filter suitable for GitHub API, or None for the whole repo."""
        path = self.PATH.strip()
        if not path or path in {".", "./"}:
            return None
        return path

    def validate(self) -> None:
        """Validate configuration values required at runtime."""
        if not self.REPOSITORY:
            message = "GITHUB_REPOSITORY is required to resolve the repository."
            raise ConfigurationError(message)
        if not self.DEFAULT_BRANCH:
            message = "default_branch must be provided."
            raise ConfigurationError(message)
