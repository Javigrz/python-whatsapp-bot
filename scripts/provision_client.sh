#!/usr/bin/env bash
set -e

# Verificar parámetros
if [ $# -ne 2 ]; then
    echo "Uso: $0 <client_name> <phone_number>"
    echo "Ejemplo: $0 demo +1234567890"
    exit 1
fi

CLIENT=$1
PHONE=$2

echo "Aprovisionando cliente: $CLIENT con número: $PHONE"

# Crear directorio del cliente
if [ -d "$CLIENT" ]; then
    echo "Error: El directorio $CLIENT ya existe"
    exit 1
fi

# Copiar template (asumiendo que estamos en la raíz del proyecto)
cp -r . "$CLIENT"
cd "$CLIENT"

# Copiar y personalizar .env
cp .env.example .env

# Reemplazar el número de teléfono
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/PHONE_NUMBER_ID=.*/PHONE_NUMBER_ID=$PHONE/" .env
else
    # Linux
    sed -i "s/PHONE_NUMBER_ID=.*/PHONE_NUMBER_ID=$PHONE/" .env
fi

# Levantar servicios con Docker Compose
echo "Levantando servicios Docker..."
docker compose up -d

# Esperar a que los servicios estén listos
echo "Esperando a que los servicios estén listos..."
sleep 10

# Verificar que los servicios estén corriendo
docker compose ps

echo "Cliente $CLIENT aprovisionado exitosamente!"
echo "Servicios corriendo en el puerto configurado"
echo "Puedes verificar el estado con: docker compose -f $CLIENT/docker-compose.yml ps" 