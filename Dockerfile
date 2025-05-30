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

# Copiar alembic.ini (asegurando que se copie al contenedor) para que alembic upgrade head funcione
COPY alembic.ini .

# Copiar la carpeta de migraciones (por ejemplo, "alembic") para que alembic upgrade head encuentre los scripts de migración
COPY alembic alembic

# Copiar el archivo alembic/env.py (o migrations/env.py) para que alembic upgrade head encuentre el archivo de entorno
COPY alembic/env.py alembic/env.py

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"] 