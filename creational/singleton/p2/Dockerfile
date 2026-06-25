# Multi-stage Dockerfile for P2 — Cache Manager (Flask + Redis)

FROM python:3.11-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/src

FROM base AS dev

COPY pyproject.toml .
RUN pip install -e ".[dev]"

COPY . .

CMD ["pytest", "tests/", "-v"]

FROM base AS prod

COPY pyproject.toml .
RUN pip install .

COPY src/ src/

EXPOSE 5000
CMD ["flask", "--app", "main", "run", "--host", "0.0.0.0", "--port", "5000"]
