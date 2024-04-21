# Reusable GitHub Actions

Collection of reusable workflows and custom actions designed to streamline automation.

## Available Workflows

- `notdodo/github-actions/.github/workflows/gitleaks.yml`: Uses [Gitleaks](https://gitleaks.io/index.html) to scan the code for secrets
- `notdodo/github-actions/.github/workflows/go-ci.yml`: Used for Golang CI linting and testing
- `notdodo/github-actions/.github/workflows/go-security-scan.yml`: Used for Golang CI security scanning with Sarif support
- `notdodo/github-actions/.github/workflows/infra-security-scan.yml`: Used for docker, Makefiles, Kubernetes security scanning with Sarif support
- `notdodo/github-actions/.github/workflows/python-ci.yml`: Used for Python CI linting and checking for [Poetry](https://python-poetry.org/) projects
- `notdodo/github-actions/.github/workflows/rust-ci.yml`: Used for Rust CI linting, building and testing

## Tagging

The repository is automatically tagged (tag for each workflow) using [notdodo/auto-tagger](https://github.com/notdodo/github-actions/tree/main/auto-tagger).
To increase a specific semver include in any of the commit messages:

- `[#major]`
- `[#minor]`
- `[#patch]`
- `[#skip]`

If no special string is used the default is `[#skip]`.

## Usage examples

### Gitleaks

```yaml
name: Gitleaks
on:
  push:

jobs:
  gitleaks:
    uses: notdodo/github-actions/.github/workflows/gitleaks.yml@2e84638563b65587b42ba8ab87ccdf1922c412dd
    # gitleaks-v0.0.0
```

### Infrastructure Security Scan

```yaml
name: Infrastructure Security Scan
on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

concurrency:
  group: your-repo-kics-${{ github.ref }}
  cancel-in-progress: true

jobs:
  infra-security-scan:
    uses: notdodo/github-actions/.github/workflows/infra-security-scan.yml@2e84638563b65587b42ba8ab87ccdf1922c412dd
    # infra-scan-v0.0.0
```

### Python CI

```yaml
name: Python CI
on:
  push:
    branches:
      - main
    paths:
      - auto-tagger/**
  pull_request:
    paths:
      - auto-tagger/**
      - .github/workflows/my-python-ci.yml

concurrency:
  group: your-repo-python-ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  python-ci:
    uses: notdodo/github-actions/.github/workflows/python-ci.yml@main
    with:
      poetry-version: 1.8.2
      python-version: 3.11
      working-directory: my-workdir
```

### Auto tagger

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
      - uses: actions/checkout@1d96c772d19495a3b5c517cd2bc0cb401ea0529f
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
