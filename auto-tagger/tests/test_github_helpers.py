"""Tests for the GitHub helper wrapper."""

# ruff: noqa: S101

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import cast

from configuration import Configuration
from github_helpers import GitHubHelper, GitRepository
from github_resources import BumpStrategy, Tag


@dataclass
class DummyAuthor:
    """Minimal author representation for testing."""

    name: str
    email: str
    date: datetime


@dataclass
class DummyCommitData:
    """Simplified commit data for tests."""

    author: DummyAuthor
    message: str


@dataclass
class DummyCommit:
    """Commit payload with author and message."""

    sha: str
    commit: DummyCommitData
    author: DummyAuthor


@dataclass
class DummyTag:
    """Tag payload containing commit data."""

    name: str
    commit: DummyCommit


class DummyRef:
    """Test reference that tracks deletion."""

    deleted: bool = False

    def delete(self) -> None:
        """Mark the reference as deleted."""
        self.deleted = True


class DummyRepo:
    """In-memory repository fake used to test helper behavior."""

    def __init__(self, tags: list[DummyTag], commits: list[DummyCommit]) -> None:
        """Store deterministic commit and tag data."""
        self._tags = tags
        self._commits = sorted(
            commits, key=lambda commit: commit.commit.author.date, reverse=True
        )
        self.created_refs: list[tuple[str, str]] = []
        self.created_tags: list[str] = []

    def get_commits(
        self, *, since: datetime, path: str | None = None
    ) -> list[DummyCommit]:
        """Return commits newer than the requested timestamp."""
        _ = path
        return [
            commit for commit in self._commits if commit.commit.author.date >= since
        ]

    def get_commit(self, sha: str) -> DummyCommit:
        """Find a commit by SHA or raise."""
        for commit in self._commits:
            if commit.sha == sha:
                return commit
        message = f"Commit {sha} not found"
        raise ValueError(message)

    def get_tags(self) -> list[DummyTag]:
        """Return all available tags."""
        return self._tags

    def create_git_tag(
        self,
        *,
        tag: str,
        message: str,
        object: str,  # noqa: A002
        type: str,  # noqa: A002
        tagger: object,
    ) -> None:
        """Record a created tag without mutating remote state."""
        _ = (message, object, type, tagger)
        self.created_tags.append(tag)

    def create_git_ref(self, ref: str, sha: str) -> None:
        """Record a created reference."""
        self.created_refs.append((ref, sha))

    def get_git_ref(self, ref: str) -> DummyRef:
        """Return a fresh dummy reference instance."""
        _ = ref
        return DummyRef()


class DummyGithub:
    """Minimal GitHub client stub."""

    def __init__(self, repo: DummyRepo) -> None:
        """Hold a reference to the dummy repository."""
        self.repo = repo

    def get_repo(self, full_name_or_id: str) -> GitRepository:
        """Return the configured dummy repository."""
        _ = full_name_or_id
        return cast("GitRepository", self.repo)


def build_commit(sha_suffix: str, date: datetime, message: str) -> DummyCommit:
    """Factory for building commits with a predictable SHA."""
    author = DummyAuthor(name="dev", email="dev@example.com", date=date)
    return DummyCommit(
        sha=f"sha-{sha_suffix}",
        commit=DummyCommitData(author=author, message=message),
        author=author,
    )


def test_bump_tag_version_uses_latest_commit() -> None:
    """Ensure new tags point to the most recent commit data."""
    commit_time = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
    commits = [
        build_commit("1", commit_time, "initial"),
        build_commit("2", commit_time + timedelta(minutes=5), "follow-up"),
    ]
    repo = DummyRepo(tags=[], commits=commits)
    helper = GitHubHelper(
        "token", Configuration(DRY_RUN=True), github_client=DummyGithub(repo)
    )
    base_tag = Tag(
        name="v0.1.0",
        commit="sha-1",
        message="initial",
        date=commit_time,
    )

    new_tag = helper.bump_tag_version(BumpStrategy.PATCH, base_tag)

    assert new_tag.name == "v0.1.1"
    assert new_tag.commit == "sha-2"
    assert new_tag.message == "follow-up"


def test_get_latest_major_tag_prefers_highest_numeric_value() -> None:
    """Prefer the numerically highest major-only tag."""
    commit_time = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
    commits = [
        build_commit("1", commit_time, "initial"),
        build_commit("2", commit_time, "another"),
    ]
    major_two = DummyTag(name="v2", commit=commits[0])
    major_ten = DummyTag(name="v10", commit=commits[1])
    repo = DummyRepo(tags=[major_two, major_ten], commits=commits)
    helper = GitHubHelper(
        "token", Configuration(DRY_RUN=True), github_client=DummyGithub(repo)
    )
    assert helper.last_available_major_tag.name == "v10"


def test_get_latest_tag_prefers_highest_semver() -> None:
    """Prefer the highest semver tag, even if older."""
    older = datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
    newer = datetime(2025, 1, 2, 12, 0, tzinfo=UTC)
    commits = [
        build_commit("1", older, "older"),
        build_commit("2", newer, "newer"),
    ]
    tag_newer_date = DummyTag(name="v1.9.0", commit=commits[1])
    tag_higher_version = DummyTag(name="v1.10.0", commit=commits[0])
    repo = DummyRepo(tags=[tag_newer_date, tag_higher_version], commits=commits)
    helper = GitHubHelper(
        "token", Configuration(DRY_RUN=True), github_client=DummyGithub(repo)
    )

    assert helper.last_available_tag.name == "v1.10.0"
