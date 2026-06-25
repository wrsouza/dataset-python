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

ENV DJANGO_SETTINGS_MODULE=settings \
    PYTHONPATH=/app/src

CMD ["python", "-m", "pytest", "tests/", "-v"]

# ── prod ──────────────────────────────────────────────────────────────────────
FROM base AS prod

COPY pyproject.toml .
RUN pip install .

COPY src/ src/

ENV DJANGO_SETTINGS_MODULE=settings \
    PYTHONPATH=/app/src \
    FLAGS_JSON_PATH=/app/src/flags.json

EXPOSE 8000

CMD ["python", "-m", "gunicorn", "wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--worker-class", "sync"]
