# Dockerfile multi-stage — Virtual File System (Composite + Flask + AWS S3)

# ── base ──────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# ── dev ───────────────────────────────────────────────────────────────────────
FROM base AS dev

COPY pyproject.toml .
RUN pip install -e ".[dev]"

COPY . .

CMD ["python", "-m", "pytest"]

# ── prod ──────────────────────────────────────────────────────────────────────
FROM base AS prod

COPY pyproject.toml .
RUN pip install .

COPY src/ src/

CMD ["flask", "--app", "filesystem.app:app", "run", "--host", "0.0.0.0", "--port", "8000"]

EXPOSE 8000
