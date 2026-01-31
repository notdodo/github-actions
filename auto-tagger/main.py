"""Python script to generate a new GitHub tag bumping its version following SemVer rules."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from semver import Version

from configuration import Configuration, ConfigurationError
from github_helpers import GitHubHelper
from github_resources import BumpStrategy

if TYPE_CHECKING:
    from collections.abc import Mapping


def _configure_logging(env: Mapping[str, str]) -> logging.Logger:
    """Configure a simple, consistent logger for action output."""
    level_name = env.get("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")
    return logging.getLogger("auto_tagger")


def run(
    config: Configuration,
    github: GitHubHelper,
    env: Mapping[str, str],
    logger: logging.Logger,
) -> int:
    """Execute the auto-tagging workflow."""
    if config.DRY_RUN:
        logger.info("Running in dry-run mode.")

    ref_name = env.get("GITHUB_REF_NAME")
    if ref_name and ref_name != config.DEFAULT_BRANCH:
        logger.info(
            "Not running from the default branch (%s != %s).",
            ref_name,
            config.DEFAULT_BRANCH,
        )
        return 0

    last_tag = github.last_available_tag
    logger.info("Last available tag: %s", last_tag.name)

    commits = github.get_commits_since(last_tag.date)
    bump_strategy = config.get_bump_strategy_from_commits(commits)

    if bump_strategy is BumpStrategy.SKIP:
        logger.info("No need to create a new tag, skipping.")
        return 0

    new_tag = github.bump_tag_version(bump_strategy, last_tag)
    logger.info("Creating new tag version: %s", new_tag.name)
    github.create_git_tag(new_tag)

    if config.BIND_TO_MAJOR:
        last_commit = github.get_last_commit()
        last_major_tag = github.last_available_major_tag
        last_major_tag.commit = env.get("GITHUB_SHA", last_commit.sha)
        last_major_tag.message = last_commit.message

        if bump_strategy is not BumpStrategy.MAJOR:
            github.delete_git_tag(last_major_tag.name)
            logger.info(
                "Binding major tag %s to latest commit: %s",
                last_major_tag.name,
                last_major_tag.commit,
            )
            github.create_git_tag(last_major_tag)
            return 0

        version_str = new_tag.name.removeprefix(config.PREFIX).removesuffix(
            config.SUFFIX
        )
        major_version = Version.parse(version_str).major
        last_major_tag.name = f"{config.PREFIX}{major_version}{config.SUFFIX}"
        logger.info("Creating new major tag %s", last_major_tag.name)
        github.create_git_tag(last_major_tag)

    return 0


def run_from_env(env: Mapping[str, str] | None = None) -> int:
    """Run the application using environment variables."""
    environment = env or os.environ
    logger = _configure_logging(environment)

    try:
        config = Configuration.from_env(environment)
        config.validate()
    except ConfigurationError:
        logger.exception("Invalid configuration.")
        return 2

    token = environment.get("INPUT_GITHUB_TOKEN", "").strip()
    if not token:
        logger.error(
            "Missing INPUT_GITHUB_TOKEN; refusing to call the GitHub API without credentials."
        )
        return 1

    try:
        github = GitHubHelper(token, config)
    except Exception:
        logger.exception("Failed to initialise GitHub helper.")
        return 1

    try:
        return run(config, github, environment, logger)
    except Exception:
        logger.exception("Auto-tagger failed.")
        return 1


def main() -> int:
    """CLI entrypoint for the GitHub Action container."""
    return run_from_env()


if __name__ == "__main__":
    raise SystemExit(main())
