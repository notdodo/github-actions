FROM python:3.13-alpine AS builder
HEALTHCHECK NONE

ENV PATH="${PATH}:/app/.local/bin" \
    POETRY_VERSION=2.1.2 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_CACHE_DIR=/app/.cache \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1

# kics-scan ignore-line
RUN apk add --no-cache musl-dev libffi-dev gcc
RUN addgroup -g 1000 app && adduser -G app -u 999 -s /sbin/nologin -h /app app -D
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN chmod -R app:app . && chmod -R a+r .
USER app
RUN pip install poetry==${POETRY_VERSION} --no-cache-dir
RUN poetry install --only main

FROM python:3.13-alpine AS runtime
HEALTHCHECK NONE

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:${PATH}"

RUN addgroup -g 1000 app && adduser -G app -u 999 -s /sbin/nologin -h /app app -D
WORKDIR /app
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY *.py ./
RUN chmod -R a+r .
USER app
LABEL org.opencontainers.image.source=https://github.com/notdodo/github-actions/tree/main/auto-tagger
LABEL org.opencontainers.image.description="A GitHub Action to automatically bump and/or create tags upon push to the default branch, using SemVer formatting."

CMD ["python", "/app/main.py"]
