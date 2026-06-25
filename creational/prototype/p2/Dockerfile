# Multi-stage Dockerfile for Document Template Cloner (Flask)

# ── base ──────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ── dev ───────────────────────────────────────────────────────────────────────
FROM base AS dev

COPY pyproject.toml .
RUN pip install -e ".[dev]"

COPY . .

ENV PYTHONPATH=/app/src
ENV FLASK_APP=main
ENV FLASK_ENV=development

CMD ["flask", "--app", "src.main", "run", "--host", "0.0.0.0", "--port", "5000", "--debug"]

# ── prod ──────────────────────────────────────────────────────────────────────
FROM base AS prod

COPY pyproject.toml .
RUN pip install .

COPY src/ src/

ENV PYTHONPATH=/app/src

CMD ["flask", "--app", "src.main", "run", "--host", "0.0.0.0", "--port", "5000"]

EXPOSE 5000
