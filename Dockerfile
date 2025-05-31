FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=0

WORKDIR /app

# Simplificar las dependencias del sistema
RUN apt-get update && \
    apt-get install -y build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar archivos de la raíz (scripts de inicio)
COPY run_app.py .
COPY boot.py .
COPY start.py .
COPY app.py .
COPY main.py .
COPY config.py .
COPY Procfile .

# Copiar directorios
COPY ./src ./src
COPY ./celery_worker ./celery_worker
COPY ./scripts ./scripts

# Usar el script que ya sabemos que funciona
CMD ["python", "run_app.py"]