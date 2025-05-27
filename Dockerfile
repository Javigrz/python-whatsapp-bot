FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=0

WORKDIR /app

# Instalación de system deps mínimas
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src
COPY ./celery_worker ./celery_worker
COPY ./scripts ./scripts

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"] 