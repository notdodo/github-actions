"""PyGitHub wrapper with strong typing and safer defaults."""

from __future__ import annotations

import copy
import os
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Protocol, cast

if TYPE_CHECKING:
    from collections.abc import Sequence

from github import Github, InputGitAuthor
from semver import Version, VersionInfo

from configuration import BumpStrategy, Configuration
from github_resources import Commit, Tag


class GitCommitAuthor(Protocol):
    """Author metadata from a Git commit payload."""

    name: str
    email: str
    date: datetime


class GitCommitData(Protocol):
    """Structured commit data within a commit payload."""

    author: GitCommitAuthor
    message: str


class GitCommitPayload(Protocol):
    """Full commit payload coming from PyGitHub."""

    sha: str
    commit: GitCommitData
    author: GitCommitAuthor | None  # PyGitHub attaches a second author object


class GitTagPayload(Protocol):
    """Tag payload returned by PyGitHub."""

    name: str
    commit: GitCommitPayload


class GitReference(Protocol):
    """Lightweight interface for a Git reference."""

    def delete(self) -> None:
        """Delete the reference from the repository."""


class GitRepository(Protocol):
    """Typed interface representing the subset of repository operations used by the helper."""

    def get_commits(
        self, *, since: datetime, path: str | None = None
    ) -> Sequence[GitCommitPayload]:
        """Return commits after a specific timestamp for an optional path."""

    def get_commit(self, sha: str) -> GitCommitPayload:
        """Fetch a commit by SHA."""

    def get_tags(self) -> Sequence[GitTagPayload]:
        """Return all tags on the repository."""

    def create_git_tag(
        self,
        *,
        tag: str,
        message: str,
        object: str,  # noqa: A002
        type: str,  # noqa: A002
        tagger: InputGitAuthor,
    ) -> None:
        """Create a new annotated tag."""

    def create_git_ref(self, ref: str, sha: str) -> None:
        """Create a reference pointing to a specific SHA."""

    def get_git_ref(self, ref: str) -> GitReference:
        """Return a mutable reference object."""


class GitHubClient(Protocol):
    """Minimal subset of the GitHub client used by the helper."""

    def get_repo(self, full_name_or_id: str) -> GitRepository:
        """Return a typed repository instance."""


def _parse_major_version(version_str: str) -> int | None:
    """Convert a major-only tag value to an int if it is strictly numeric."""
    try:
        return int(version_str)
    except ValueError:
        return None


class GitHubHelper:
    """PyGitHub support class."""

    def __init__(
        self,
        token: str,
        config: Configuration,
        github_client: GitHubClient | None = None,
    ) -> None:
        """Create the helper; a non-empty token is mandatory to avoid anonymous calls."""
        self.token = token.strip()
        if not self.token:
            message = "GitHub token must be provided for API access."
            raise ValueError(message)
        self.config = config
        self.github_client: GitHubClient = cast(
            "GitHubClient", github_client or Github(self.token)
        )
        self.repo: GitRepository = self.github_client.get_repo(self.config.REPOSITORY)
        self.last_available_tag: Tag = self.get_latest_tag()
        self.last_available_major_tag: Tag = self.get_latest_major_tag()

    def bump_tag_version(self, strategy: BumpStrategy, tag: Tag) -> Tag:
        """Create a new Tag resource with the increased version number."""
        new_tag = copy.deepcopy(tag)
        current_version = Version.parse(
            tag.name.removeprefix(self.config.PREFIX).removesuffix(self.config.SUFFIX)
        )
        new_version = current_version
        if strategy == BumpStrategy.MAJOR:
            new_version = current_version.bump_major()
        elif strategy == BumpStrategy.MINOR:
            new_version = current_version.bump_minor()
        elif strategy == BumpStrategy.PATCH:
            new_version = current_version.bump_patch()

        new_tag.name = f"{self.config.PREFIX}{new_version}{self.config.SUFFIX}"
        last_commit = self.get_last_commit()
        new_tag.commit = os.environ.get("GITHUB_SHA", last_commit.sha)
        new_tag.message = last_commit.message
        return new_tag

    def get_commits_since(self, since: datetime) -> list[Commit]:
        """Get commits since a predefined datetime."""
        return [
            self._to_commit_resource(commit)
            for commit in self.repo.get_commits(
                since=since + timedelta(seconds=1), path=self.config.PATH
            )
        ]

    def get_last_commit(self) -> Commit:
        """Get the latest commit available on the repository."""
        default_commit_list = self.repo.get_commits(
            since=datetime.fromtimestamp(0, tz=UTC), path=self.config.PATH
        )
        if not default_commit_list:
            message = "Unable to resolve last commit: repository returned no commits."
            raise RuntimeError(message)
        fallback_sha = default_commit_list[0].sha
        commit = self.repo.get_commit(os.environ.get("GITHUB_SHA", fallback_sha))
        return self._to_commit_resource(commit)

    def get_latest_tag(self) -> Tag:
        """Get the latest semver tag matching prefix and suffix on the repository (e.g. v0.2.1)."""
        matching_tags: list[Tag] = []
        for tag in self.repo.get_tags():
            name = tag.name
            if not name.startswith(self.config.PREFIX) or not name.endswith(
                self.config.SUFFIX
            ):
                continue
            version_str = name.removeprefix(self.config.PREFIX).removesuffix(
                self.config.SUFFIX
            )
            if not VersionInfo.is_valid(version_str):
                continue
            matching_tags.append(
                Tag(
                    name=name,
                    commit=tag.commit.sha,
                    message=tag.commit.commit.message,
                    date=tag.commit.commit.author.date,
                )
            )

        if matching_tags:
            return max(matching_tags, key=lambda candidate: candidate.date)

        last_commit = self.get_last_commit()
        default_tag = Tag(
            name=f"{self.config.PREFIX}0.0.0{self.config.SUFFIX}",
            commit=last_commit.sha,
            message=last_commit.message,
            date=last_commit.date,
        )
        if not self.config.DRY_RUN:
            self.create_git_tag(default_tag)
        return default_tag

    def get_latest_major_tag(self) -> Tag:
        """Get the latest major-only tag matching prefix and suffix on the repository (e.g. v1)."""
        valid_tags: list[tuple[int, Tag]] = []
        for tag in self.repo.get_tags():
            name = tag.name
            if not (
                name.startswith(self.config.PREFIX)
                and name.endswith(self.config.SUFFIX)
            ):
                continue
            version_str = name.removeprefix(self.config.PREFIX).removesuffix(
                self.config.SUFFIX
            )
            if VersionInfo.is_valid(version_str):
                continue
            major = _parse_major_version(version_str)
            if major is None:
                continue
            valid_tags.append(
                (
                    major,
                    Tag(
                        name=name,
                        commit=tag.commit.sha,
                        message=tag.commit.commit.message,
                        date=tag.commit.commit.author.date,
                    ),
                )
            )

        if valid_tags:
            _, latest_tag = max(valid_tags, key=lambda value: value[0])
            return latest_tag

        last_commit = self.get_last_commit()
        default_tag_name = f"{self.config.PREFIX}0{self.config.SUFFIX}"
        initial_tag = Tag(
            name=default_tag_name,
            commit=last_commit.sha,
            message=last_commit.message,
            date=last_commit.date,
        )
        if not self.config.DRY_RUN:
            self.create_git_tag(initial_tag)
        return initial_tag

    def create_git_tag(self, tag: Tag) -> None:
        """Create a new tag on the repository bound to a specific commit."""
        commit = self.repo.get_commit(tag.commit)
        author = commit.author or commit.commit.author
        author_name = getattr(author, "name", "automation")
        author_email = getattr(author, "email", "automation@users.noreply.github.com")
        tagger = InputGitAuthor(
            name=str(author_name),
            email=str(author_email),
            date=str(datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")),
        )

        if self.config.DRY_RUN:
            return

        self.repo.create_git_tag(
            tag=tag.name,
            message=tag.message,
            object=tag.commit,
            type="commit",
            tagger=tagger,
        )
        self.repo.create_git_ref(f"refs/tags/{tag.name}", tag.commit)

    def delete_git_tag(self, tag_name: str) -> None:
        """Delete a tag on the repository (no-op in dry-run)."""
        if self.config.DRY_RUN:
            return
        ref = self.repo.get_git_ref(f"tags/{tag_name}")
        ref.delete()

    @staticmethod
    def _to_commit_resource(commit: GitCommitPayload) -> Commit:
        """Convert a PyGitHub commit payload to a typed Commit resource."""
        return Commit(
            sha=commit.sha,
            author_name=commit.commit.author.name,
            author_email=commit.commit.author.email,
            message=commit.commit.message,
            date=commit.commit.author.date,
        )
