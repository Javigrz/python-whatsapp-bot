#!/bin/bash

# Script para gestionar clientes del WhatsApp Bot
# Este script activa el entorno virtual y ejecuta el gestor de clientes

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🤖 WhatsApp Bot - Gestor de Clientes${NC}"
echo -e "${BLUE}======================================${NC}"

# Verificar si el entorno virtual existe
if [ ! -d "venv_client" ]; then
    echo -e "${RED}❌ Entorno virtual no encontrado. Creando...${NC}"
    python3 -m venv venv_client
    echo -e "${GREEN}✅ Entorno virtual creado${NC}"
fi

# Verificar si requests está instalado
if ! venv_client/bin/pip list | grep -q requests; then
    echo -e "${BLUE}📦 Instalando requests...${NC}"
    venv_client/bin/pip install requests > /dev/null 2>&1
    echo -e "${GREEN}✅ requests instalado${NC}"
fi

echo -e "${GREEN}🚀 Iniciando gestor de clientes...${NC}"
echo ""

# Activar entorno virtual y ejecutar script
source venv_client/bin/activate && python test_create_client.py
