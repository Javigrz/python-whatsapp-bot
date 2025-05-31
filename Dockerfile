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

# Verificar que boot.py existe y es ejecutable
RUN ls -la /app/boot.py
RUN chmod +x /app/boot.py

# Usar boot.py como punto de entrada
CMD ["python", "boot.py"]