# Reusable GitHub Actions

Collection of reusable workflows designed to streamline automation.

## Available Workflows

- `notdodo/github-actions/.github/workflows/gitleaks.yml`: Uses [Gitleaks](https://gitleaks.io/index.html) to scan the code for secrets
- `notdodo/github-actions/.github/workflows/go-build-and-test.yml`: Used for Golang CI linting and testing
- `notdodo/github-actions/.github/workflows/go-security-scan.yml`: Used for Golang CI security scanning with Sarif support
- `notdodo/github-actions/.github/workflows/infra-security-scan.yml`: Used for docker, Makefiles, Kubernetes security scanning with Sarif support
- `notdodo/github-actions/.github/workflows/rust-ci.yml`: Used for Rust CI linting, building and testing

## Tagging

The repository is automatically tagged (no tag for each workflow) using [anothrNick/github-tag-action](https://github.com/anothrNick/github-tag-action).
To increase a specific semver include in any of the commit messages:

- `#major`
- `#minor`
- `#patch`
- `#none`

If no special string is used the default is `#patch`.

## Usage examples

### Gitleaks

```yaml
name: Gitleaks
on:
  push:

jobs:
  gitleaks:
    uses: notdodo/github-actions/.github/workflows/gitleaks.yml@ec54c76d4a9713ca6150253f38e14f4e4031e4a2
    # v0.1.1
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
    uses: notdodo/github-actions/.github/workflows/infra-security-scan.yml@ec54c76d4a9713ca6150253f38e14f4e4031e4a2
    # v0.1.1
```

### Rust CI

```yaml
name: Rust

on:
  push:
    branches:
      - "main"
  pull_request:
    branches:
      - "main"
    paths:
      - "**.rs"
      - "Cargo.*"
      - .github/workflows/rust-ci.yml

concurrency:
  group: your-repo-rust-ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  infra-security-scan:
    uses: notdodo/github-actions/.github/workflows/rust-ci.yml@ec54c76d4a9713ca6150253f38e14f4e4031e4a2
    # v0.1.1
```

## Golang CI

```yaml
name: Golang CI
on:
  push:
    branches:
      - main
    paths:
      - "**.go"
      - "go.mod"
      - "go.sum"
  pull_request:
    paths:
      - "**.go"
      - "go.mod"
      - "go.sum"

concurrency:
  group: your-repo-ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  sast:
    uses: notdodo/github-actions/.github/workflows/go-security-scan.yml@@ec54c76d4a9713ca6150253f38e14f4e4031e4a2
    # v0.1.1

  build-and-test:
    uses: notdodo/github-actions/.github/workflows/go-build-and-test.yml@@ec54c76d4a9713ca6150253f38e14f4e4031e4a2
    # v0.1.1
```
