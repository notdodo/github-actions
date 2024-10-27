FROM python:3.12-alpine AS builder
HEALTHCHECK NONE

ENV PATH="${PATH}:/app/.local/bin" \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_CACHE_DIR=/app/.cache \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1

RUN apk add musl-dev libffi-dev gcc --no-cache
RUN addgroup -g 1000 app && adduser -G app -u 999 -s /sbin/nologin -h /app app -D
WORKDIR /app
COPY pyproject.toml poetry.lock /app/
RUN chmod -R a+r /app
USER app
RUN pip install poetry
RUN poetry install --only main

FROM python:3.12-alpine AS runtime
HEALTHCHECK NONE

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:${PATH}"

RUN addgroup -g 1000 app && adduser -G app -u 999 -s /sbin/nologin -h /app app -D
WORKDIR /app
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY *.py /app/
RUN chmod -R a+r /app
RUN ls -la
USER app

CMD ["python", "/app/main.py"]
