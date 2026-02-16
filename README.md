# Reusable GitHub Actions

Collection of reusable workflows and custom actions designed to streamline automation.

![Alt](https://repobeats.axiom.co/api/embed/39be58fe920770fc61a415d2a67806ee014f7d82.svg "Repobeats analytics image")

## Available Workflows

- `notdodo/github-actions/.github/workflows/clean-branch-cache.yml`: Use to cleanup the cache for a merge branch
- `notdodo/github-actions/.github/workflows/docker-build-and-push.yml`: Builds a Dockerfile, optionally signs it with cosign, uploads the image to a registry, and performs a scan using [Trivy](https://trivy.dev/latest/)
- `notdodo/github-actions/.github/workflows/gitleaks.yml`: Uses [Gitleaks](https://gitleaks.io/index.html) to scan the code for secrets
- `notdodo/github-actions/.github/workflows/go-ci.yml`: Used for Golang CI linting and testing
- `notdodo/github-actions/.github/workflows/go-security-scan.yml`: Used for Golang CI security scanning with Sarif support
- `notdodo/github-actions/.github/workflows/infra-security-scan.yml`: Used for docker, Makefiles, Kubernetes security scanning with Sarif support
- `notdodo/github-actions/.github/workflows/pulumi-preview.yml`: Used to run Pulumi preview with PR comments and OIDC authentication
- `notdodo/github-actions/.github/workflows/pulumi-up.yml`: Used to run Pulumi up for stack deployments with OIDC authentication
- `notdodo/github-actions/.github/workflows/python-ci.yml`: Used for Python CI linting and checking for [Poetry](https://python-poetry.org/) projects
- `notdodo/github-actions/.github/workflows/rust-ci.yml`: Used for Rust CI linting, building and testing
- `notdodo/github-actions/.github/workflows/sast.yml`: Used to run Semgrep on the repository with Sarif support
- `notdodo/github-actions/.github/workflows/terraform-ci.yml`: Used for Terraform CI linting and show plan output on Pull Requests

## Tagging

The repository is automatically tagged (tag for each workflow) using [notdodo/auto-tagger](https://github.com/notdodo/github-actions/tree/main/auto-tagger).
To increase a specific semver include in any of the commit messages:

- `[#major]`
- `[#minor]`
- `[#patch]`
- `[#skip]`

If no special string is used the default is `[#skip]`.

## Usage examples

### Clean up cache

```yaml
name: Cleanup caches by a branch
on:
  pull_request:
    types:
      - closed

jobs:
  cleanup:
    uses: notdodo/github-actions/.github/workflows/clean-branch-cache.yml@cleanup-v0
```

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

### Pulumi Preview

```yaml
name: Pulumi Preview
on:
  pull_request:
    branches:
      - main

jobs:
  pulumi-preview:
    permissions:
      contents: read
      pull-requests: write
      id-token: write
    uses: notdodo/github-actions/.github/workflows/pulumi-preview.yml@pulumi-preview-v0
    with:
      stack-name: notdodo/my-project/dev
      working-directory: infra
      aws-role: arn:aws:iam::123456789012:role/github-actions-pulumi-preview
      aws-region: eu-west-1
```

### Pulumi Up

```yaml
name: Pulumi Up
on:
  push:
    branches:
      - main

jobs:
  pulumi-up:
    permissions:
      contents: read
      id-token: write
    uses: notdodo/github-actions/.github/workflows/pulumi-up.yml@pulumi-up-v0
    with:
      stack-name: notdodo/my-project/prod
      working-directory: infra
      aws-role: arn:aws:iam::123456789012:role/github-actions-pulumi-up
      aws-region: eu-west-1
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

### Rust CI

### Docker build and push

```yaml
name: "Docker image builder and publisher"

on:
  push:
    tags:
      - "new-version-v[0-9]+.[0-9]+.[0-9]+"

jobs:
  build-push-docker-image:
    uses: notdodo/github-actions/.github/workflows/docker-build-and-push.yml@docker-build-and-push-v1
    with:
      image: notdodo/my-app
      platforms: linux/amd64
      push: true
      registry: ghcr.io
      working-directory: .
      tags: |
        type=match,pattern=new-version-v(.*),group=1
    secrets:
      registry-username: notdodo
      registry-password: ${{ secrets.GITHUB_TOKEN }}
```

By default, this workflow signs pushed images with cosign (`sign-image: true`) using the reusable workflow identity (the certificate identity belongs to the reusable workflow reference).

To skip signing in the reusable workflow:

```yaml
jobs:
  build-push-docker-image:
    uses: notdodo/github-actions/.github/workflows/docker-build-and-push.yml@docker-build-and-push-v1
    with:
      image: notdodo/my-app
      push: true
      registry: ghcr.io
      sign-image: false
    secrets:
      registry-username: notdodo
      registry-password: ${{ secrets.GITHUB_TOKEN }}
```

Example: sign in the caller workflow instead of the reusable workflow.

When used as a reusable workflow, these job outputs are available to the caller:

- `image_name`: `<registry>/<image>`
- `image_digest`: pushed digest (`sha256:...`), empty when `push: false`
- `image_ref`: immutable image reference (`<registry>/<image>@<digest>`), empty when `push: false`
- `local_image_ref`: local image reference (`localimage:<sha>`), only set when `push: false`

```yaml
name: Docker Build, Then Sign in Caller
on:
  push:
    branches: [main]

jobs:
  build-image:
    permissions:
      attestations: write
      contents: read
      id-token: write
      packages: write
      security-events: write
    uses: notdodo/github-actions/.github/workflows/docker-build-and-push.yml@docker-build-and-push-v1
    with:
      image: notdodo/my-app
      push: true
      registry: ghcr.io
      sign-image: false
    secrets:
      registry-username: notdodo
      registry-password: ${{ secrets.GITHUB_TOKEN }}

  sign-image:
    needs: [build-image]
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: sigstore/cosign-installer@v4.0.0
      - name: Sign and verify
        env:
          COSIGN_YES: "true"
          IMAGE_REF: ${{ needs.build-image.outputs.image_ref }}
          CERT_OIDC_ISSUER: https://token.actions.githubusercontent.com
          CERT_IDENTITY: ${{ format('https://github.com/{0}', github.workflow_ref) }}
        run: |
          cosign sign "${IMAGE_REF}"
          cosign verify \
            --certificate-identity "${CERT_IDENTITY}" \
            --certificate-oidc-issuer "${CERT_OIDC_ISSUER}" \
            "${IMAGE_REF}"
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
