# Multi-stage Dockerfile — db-factory (Django + PostgreSQL/MySQL/SQL Server drivers)
# Stage "dev" runs tests; stage "prod" serves via gunicorn.

# ── base ──────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DJANGO_SETTINGS_MODULE=db_factory.settings

# gcc/libpq-dev for psycopg2; unixodbc-dev for pyodbc (SQL Server, optional)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    default-libmysqlclient-dev \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# ── dev ───────────────────────────────────────────────────────────────────────
FROM base AS dev

COPY pyproject.toml .
RUN pip install -e ".[dev]"

COPY . .

# Run migrations then tests
CMD ["sh", "-c", "python src/manage.py migrate --no-input && pytest tests/ -v"]

# ── prod ──────────────────────────────────────────────────────────────────────
FROM base AS prod

COPY pyproject.toml .
RUN pip install . gunicorn

COPY src/ src/

# Run migrations then start the app server
CMD ["sh", "-c", "python src/manage.py migrate --no-input && gunicorn db_factory.wsgi:application --bind 0.0.0.0:8000 --chdir src"]

EXPOSE 8000
