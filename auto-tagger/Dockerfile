FROM python:3-alpine AS builder
HEALTHCHECK NONE

ENV POETRY_VERSION=1.8.3 \
    PATH="${PATH}:/app/.local/bin" \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_CACHE_DIR=/app/.cache \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1

RUN addgroup -g 1000 app && adduser -G app -u 999 -s /sbin/nologin -h /app app -D
USER app
WORKDIR /app
COPY pyproject.toml poetry.lock /app/
RUN pip install --user --no-cache-dir poetry==${POETRY_VERSION} && poetry install --only main --no-root

FROM python:3-alpine AS runtime
HEALTHCHECK NONE

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:${PATH}"

RUN addgroup -g 1000 app && adduser -G app -u 999 -s /sbin/nologin -h /app app -D
USER app
WORKDIR /app
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY *.py /app/

CMD ["python", "/app/main.py"]
