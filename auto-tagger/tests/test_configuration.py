"""Tests for configuration helpers."""

# ruff: noqa: S101

from datetime import UTC, datetime

import pytest

from configuration import BumpStrategy, Configuration
from github_resources import Commit


def test_configuration_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Populate configuration from environment variables."""
    monkeypatch.setenv("INPUT_BIND_TO_MAJOR", "true")
    monkeypatch.setenv("INPUT_DEFAULT_BUMP_STRATEGY", "minor")
    monkeypatch.setenv("INPUT_MAIN_BRANCH", "develop")
    monkeypatch.setenv("INPUT_PATH", "src")
    monkeypatch.setenv("INPUT_PREFIX", "release-")
    monkeypatch.setenv("INPUT_SUFFIX", "-beta")
    monkeypatch.setenv("INPUT_DRY_RUN", "true")
    monkeypatch.setenv("GITHUB_REPOSITORY", "octocat/hello-world")

    config = Configuration.from_env()

    assert config.BIND_TO_MAJOR is True
    assert config.DEFAULT_BUMP_STRATEGY is BumpStrategy.MINOR
    assert config.DEFAULT_BRANCH == "develop"
    assert config.PATH == "src"
    assert config.PREFIX == "release-"
    assert config.SUFFIX == "-beta"
    assert config.DRY_RUN is True
    assert config.REPOSITORY == "octocat/hello-world"


def test_get_bump_strategy_from_commits_detects_keyword() -> None:
    """Detect bump strategy keyword in commit messages."""
    config = Configuration(DEFAULT_BUMP_STRATEGY=BumpStrategy.PATCH)
    commits = [
        Commit(
            sha="1",
            author_name="test",
            author_email="test@example.com",
            message="chore: housekeeping",
            date=datetime.now(UTC),
        ),
        Commit(
            sha="2",
            author_name="test",
            author_email="test@example.com",
            message="[#minor] upd: stuff",
            date=datetime.now(UTC),
        ),
    ]

    strategy = config.get_bump_strategy_from_commits(commits)

    assert strategy is BumpStrategy.MINOR
