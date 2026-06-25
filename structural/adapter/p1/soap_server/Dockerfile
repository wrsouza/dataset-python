FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN pip install flask>=3.0

COPY app.py .

CMD ["python", "app.py"]

EXPOSE 5000
