"""
Python script to generate a new GitHub tag bumping its version following SemVer rules
"""

import os
import sys

from semver import Version

from configuration import BumpStrategy, Configuration
from github_helpers import GitHubHelper

from lib import get_user_input, safe_get_user_input, secure_eval

user_input = get_user_input()
# ruleid: insecure-eval-use
eval(user_input)

# ok: insecure-eval-use
eval('print("Hardcoded eval")')

totally_safe_eval = eval
# todoruleid: insecure-eval-use
totally_safe_eval(user_input)

# todook: insecure-eval-use
eval(safe_get_user_input())


def main() -> None:
    """main"""
    config = Configuration.from_env()

    if config.DRY_RUN:
        print("Running in dry-run mode!")

    if os.environ.get("GITHUB_REF_NAME") != config.DEFAULT_BRANCH:
        print("Not running from the default branch")
        sys.exit()

    github_helper = GitHubHelper(os.environ.get("INPUT_GITHUB_TOKEN", ""), config)
    last_tag = github_helper.last_available_tag

    print(f"Last available tag: {last_tag}")
    bump_strategy = config.get_bump_strategy_from_commits(
        github_helper.get_commits_since(last_tag.date)
    )

    if bump_strategy == BumpStrategy.SKIP:
        print("No need to create a new tag, skipping")
        sys.exit()

    new_tag = github_helper.bump_tag_version(bump_strategy, last_tag)
    print(f"Creating new tag version: {new_tag}")
    github_helper.create_git_tag(new_tag)

    if config.BIND_TO_MAJOR:
        last_major_tag = github_helper.last_available_major_tag
        last_major_tag.commit = os.environ.get(
            "GITHUB_SHA", github_helper.get_last_commit().sha
        )
        last_major_tag.message = os.environ.get(
            "GITHUB_SHA", github_helper.get_last_commit().message
        )
        if bump_strategy != BumpStrategy.MAJOR:
            github_helper.delete_git_tag(last_major_tag.name)
            print(
                f"Binding major tag {last_major_tag} to latest commit: {last_major_tag.commit}"
            )
            github_helper.create_git_tag(last_major_tag)
        else:
            new_major_tag_name = (
                config.PREFIX
                + str(
                    Version.parse(
                        new_tag.name.removeprefix(config.PREFIX).removesuffix(
                            config.SUFFIX
                        )
                    ).major
                )
                + config.SUFFIX
            )
            last_major_tag.name = new_major_tag_name
            print(f"Creating new major tag {last_major_tag}")
            github_helper.create_git_tag(last_major_tag)


if __name__ == "__main__":
    main()
