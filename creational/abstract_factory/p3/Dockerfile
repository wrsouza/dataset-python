# Message Broker Factory — multi-stage Dockerfile
# Pattern: Abstract Factory | Framework: CLI (Typer) | Services: RabbitMQ, Kafka, SQS (LocalStack)

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

CMD ["python", "-m", "pytest"]

# ── prod ──────────────────────────────────────────────────────────────────────
FROM base AS prod

COPY pyproject.toml .
RUN pip install .

COPY src/ src/

CMD ["python", "-m", "broker_factory.cli", "--help"]
