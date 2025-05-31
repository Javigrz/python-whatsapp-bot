FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar TODO el código fuente
COPY . .

# --- Comandos de Diagnóstico ---
RUN echo "=== BUILD DIAGNOSTICS ===" && \
    ls -la /app && \
    echo "=== CHECKING src/main.py ===" && \
    ls -la /app/src/main.py && \
    echo "=== TESTING IMPORT ===" && \
    python -c "from src.main import app; print('✅ FastAPI app imported successfully')" && \
    echo "=== END DIAGNOSTICS ==="

# Railway proporciona PORT como variable de entorno
# Usamos el Procfile para manejar el puerto dinámicamente
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
