# ── base ──────────────────────────────────────────────
FROM python:3.11-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gnupg unixodbc-dev gcc g++ \
    && curl -sSL -O https://packages.microsoft.com/keys/microsoft.asc \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ── dev ───────────────────────────────────────────────
FROM base AS dev
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]"
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "src/data_view/app.py", "--server.address=0.0.0.0"]

# ── prod ──────────────────────────────────────────────
FROM base AS prod
COPY pyproject.toml .
RUN pip install --no-cache-dir -e "."
COPY src/ src/
EXPOSE 8501
CMD ["streamlit", "run", "src/data_view/app.py", "--server.address=0.0.0.0"]
