#!/bin/bash
set -e

PORT="${PORT:-8000}"
MAX_RETRIES=30
RETRY_INTERVAL=2

# Función para esperar que la app esté saludable
wait_for_app() {
    local url="http://localhost:$PORT/health"
    echo "Esperando que la aplicación esté lista..."
    
    for i in $(seq 1 $MAX_RETRIES); do
        if curl -s "$url" | grep -q "healthy"; then
            echo "¡Aplicación lista!"
            return 0
        fi
        echo "Intento $i de $MAX_RETRIES..."
        sleep $RETRY_INTERVAL
    done
    
    echo "La aplicación no respondió en tiempo"
    return 1
}

# Iniciar la aplicación
uvicorn main:app --host 0.0.0.0 --port "$PORT" --workers 4 &
APP_PID=$!

# Esperar que la app esté lista
wait_for_app

# Si la app no está lista, terminar
if [ $? -ne 0 ]; then
    kill $APP_PID
    exit 1
fi

# Mantener el script corriendo
wait $APP_PID
