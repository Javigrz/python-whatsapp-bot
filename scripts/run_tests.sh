#!/usr/bin/env bash
set -e

echo "Ejecutando tests de Released WhatsApp Bot..."

# Verificar que estamos en el directorio correcto
if [ ! -f "requirements.txt" ]; then
    echo "Error: Debe ejecutarse desde la raíz del proyecto"
    exit 1
fi

# Instalar dependencias si no están instaladas
if ! command -v pytest &> /dev/null; then
    echo "Instalando dependencias de test..."
    pip install -r requirements.txt
fi

# Ejecutar tests unitarios
echo "=== Ejecutando tests unitarios ==="
pytest tests/unit -v --tb=short

# Ejecutar tests de integración
echo "=== Ejecutando tests de integración ==="
pytest tests/integration -v --tb=short

# Ejecutar tests E2E si está configurado
if [ -n "$RUN_E2E_TESTS" ]; then
    echo "=== Ejecutando tests E2E ==="
    
    # Verificar que ngrok esté instalado
    if ! command -v ngrok &> /dev/null; then
        echo "Error: ngrok no está instalado. Instálalo para ejecutar tests E2E"
        exit 1
    fi
    
    # Levantar servicios de test
    docker compose -f docker-compose.test.yml up -d
    
    # Esperar a que los servicios estén listos
    sleep 10
    
    # Ejecutar tests E2E
    pytest tests/e2e -v --tb=short
    
    # Limpiar
    docker compose -f docker-compose.test.yml down
fi

# Generar reporte de cobertura
echo "=== Generando reporte de cobertura ==="
pytest --cov=src --cov-report=html --cov-report=term

echo "Tests completados exitosamente!" 