# Action auto-tagger

A GitHub Action to automatically bump and/or create tags upon push to the default branch, using SemVer formatting.

![Latest Tag](https://img.shields.io/github/v/tag/notdodo/github-actions?sort=semver&filter=auto-tagger*)
[![Python CI](https://github.com/notdodo/github-actions/actions/workflows/local-python-ci.yml/badge.svg?branch=main)](https://github.com/notdodo/github-actions/actions/workflows/local-python-ci.yml)

The action automatically creates tags, increasing a specific SemVer version if any of the commit messages include the following keywords:

- `[#major]`
- `[#minor]`
- `[#patch]`
- `[#skip]`

If no special string is used, the default is configured by the parameter `default_bump_strategy` (default: `skip`).

## Usage

To run the action when a new push is performed on the `main` branch:

```yaml
name: auto-tagger
on:
  push:
    branches:
      - main

jobs:
  auto-tagger:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run action
        uses: notdodo/github-actions/auto-tagger@auto-tagger-v0
        with:
          bind_to_major: true
          default_bump_strategy: skip
          default_branch: main
          prefix: test-v
          github_token: ${{ secrets.GITHUB_TOKEN }}
          dry_run: false
```

If there are no tags already available with the specified format, a new one with version `0.0.0` is created.

### Options

| Option                    | Required | Default Value | Description                                                                                 |
| ------------------------- | -------- | ------------- | ------------------------------------------------------------------------------------------- |
| **bind_to_major**         | No       | false         | If 'true' creates a new tag with only the major number and binds it to the latest full tag. |
| **default_branch**        | No       | main          | Default branch to bind the tag to (e.g., 'master').                                         |
| **default_bump_strategy** | No       | skip          | Bump strategy to use by default if no instruction is provided.                              |
| **dry_run**               | No       | false         | Run the Action in dry-run mode: do not create tags.                                         |
| **github_token**          | **Yes**  |               | The GITHUB_TOKEN required to create the tag from the action.                                |
| **prefix**                | No       | v             | Prefix to use for tag generation (e.g., 'v').                                               |
| **suffix**                | No       | ""            | Suffix to use for tag generation (e.g., '-test').                                           |

### Bump Strategy

Bumping a tag version can happen in two methods:

- Any commit message that includes `[#major]`, `[#minor]`, `[#patch]` triggers the respective SemVer bump. If two or more are present, the order is from `major` to `patch`.
- If no commit message contains the keyword, the default value is used from `default_bump_strategy`.
