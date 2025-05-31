FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar TODO el código fuente al directorio /app
COPY . .

# --- Comandos de Diagnóstico en Build ---
RUN echo "--- Listing /app contents during build ---" && ls -la /app
RUN echo "--- Checking for /app/boot.py during build ---" && ls -la /app/boot.py || echo "boot.py not found at /app/boot.py during build"
RUN echo "--- Verifying boot.py content during build ---" && head -5 /app/boot.py || echo "Could not read boot.py content during build"
# --- Fin Comandos de Diagnóstico en Build ---

# Usar boot.py como punto de entrada (ahora es el script de diagnóstico)
CMD ["python", "boot.py"]