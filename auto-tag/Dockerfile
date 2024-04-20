FROM python:3-slim AS builder
# HEALTHCHECK NONE

ENV POETRY_VERSION=1.8.2
ENV PATH="${PATH}:/app/.local/bin"
ENV POETRY_CACHE_DIR=/app/.cache

RUN groupadd -g 999 app && useradd -g 999 -u 999 --system --shell /usr/sbin/nologin -m -d /app app
USER app
WORKDIR /app
RUN pip install --user --no-cache-dir poetry==${POETRY_VERSION}

COPY pyproject.toml poetry.lock *.py /app/
RUN poetry config --local virtualenvs.in-project true && poetry install --only main --no-root

CMD ["/app/.venv/bin/python", "/app/main.py"]