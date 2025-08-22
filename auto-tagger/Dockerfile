FROM python:3.13-alpine AS builder
HEALTHCHECK NONE

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.13 \
    UV_NO_PROGRESS=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync \
    --locked \
    --no-dev \
    --no-install-project --no-editable
COPY pyproject.toml uv.lock ./
COPY *.py ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable --no-dev

FROM python:3.13-alpine AS runtime
HEALTHCHECK NONE

ENV PATH="/app/.venv/bin:${PATH}"

RUN addgroup -g 1000 app && adduser -G app -u 999 -s /sbin/nologin -h /app app -D
WORKDIR /app
COPY --from=builder /app /app
RUN chmod -R a+r .
LABEL org.opencontainers.image.source=https://github.com/notdodo/github-actions/tree/main/auto-tagger
LABEL org.opencontainers.image.description="A GitHub Action to automatically bump and/or create tags upon push to the default branch, using SemVer formatting."

USER app
CMD ["python", "-OO", "/app/main.py"]
