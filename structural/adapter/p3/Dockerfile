# Multi-stage Dockerfile — cloud-adapter (Django + boto3)
# Stage "dev" runs tests; stage "prod" serves via gunicorn.

# ── base ──────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DJANGO_SETTINGS_MODULE=cloud_adapter.settings

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ── dev ───────────────────────────────────────────────────────────────────────
FROM base AS dev

COPY pyproject.toml .
RUN pip install -e ".[dev]"

COPY . .

# Run migrations then tests
CMD ["sh", "-c", "python src/manage.py migrate && pytest tests/ -v"]

# ── prod ──────────────────────────────────────────────────────────────────────
FROM base AS prod

COPY pyproject.toml .
RUN pip install . gunicorn

COPY src/ src/

# Collect static and run migrations before starting
CMD ["sh", "-c", "python src/manage.py migrate && gunicorn cloud_adapter.wsgi:application --bind 0.0.0.0:8000"]

EXPOSE 8000
