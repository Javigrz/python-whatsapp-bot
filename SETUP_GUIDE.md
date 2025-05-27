# 🚀 Guía de Configuración y Uso - Bot WhatsApp Multi-Cliente

Esta guía te llevará paso a paso desde la instalación hasta enviar tu primer mensaje de prueba.

## 📋 Requisitos Previos

- Docker y Docker Compose instalados
- ngrok instalado (`brew install ngrok` en Mac)
- Cuenta de Meta Business con acceso a WhatsApp Business API
- API Key de OpenAI
- Python 3.8+ instalado localmente

## 🔧 Paso 1: Configuración Inicial

### 1.1 Clonar el repositorio
```bash
git clone <tu-repositorio>
cd python-whatsapp-bot
```

### 1.2 Crear archivo de variables de entorno
Crea un archivo `.env` en la raíz del proyecto:

```env
# FastAPI
PORT=8082

# WhatsApp Business API
ACCESS_TOKEN="tu_access_token_de_meta"
APP_ID="tu_app_id"
APP_SECRET="tu_app_secret"
WEBHOOK_VERIFY_TOKEN="un_token_secreto_que_tu_elijas"
VERSION="v18.0"

# OpenAI
OPENAI_API_KEY="tu_openai_api_key"

# Database
DATABASE_URL=postgresql://whatsapp_user:whatsapp_pass@db:5432/whatsapp_bot

# Redis
REDIS_URL=redis://redis:6379/0

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

## 🐳 Paso 2: Levantar los Servicios con Docker

### 2.1 Construir y levantar los contenedores
```bash
# Levantar todos los servicios
docker compose up -d --build

# Verificar que todos estén funcionando
docker compose ps
```

Deberías ver 4 contenedores corriendo:
- `python-whatsapp-bot-web-1` (FastAPI)
- `python-whatsapp-bot-worker-1` (Celery)
- `python-whatsapp-bot-redis-1` (Redis)
- `python-whatsapp-bot-db-1` (PostgreSQL)

### 2.2 Verificar logs (opcional)
```bash
# Ver logs de todos los servicios
docker compose logs -f

# O solo web y worker
docker compose logs -f web worker
```

## 🌐 Paso 3: Configurar ngrok

### 3.1 Iniciar ngrok
En una terminal separada, ejecuta:
```bash
ngrok http 8082
```

### 3.2 Copiar la URL HTTPS
Verás algo como:
```
Forwarding  https://3d34-148-56-140-192.ngrok-free.app -> http://localhost:8082
```

Copia la URL HTTPS (ejemplo: `https://3d34-148-56-140-192.ngrok-free.app`)

## 📱 Paso 4: Configurar Webhook en Meta

### 4.1 Ir a Meta for Developers
1. Ve a [developers.facebook.com](https://developers.facebook.com)
2. Selecciona tu app
3. Ve a WhatsApp > Configuration > Webhook

### 4.2 Configurar el Webhook
- **Callback URL**: `https://tu-url-ngrok.ngrok-free.app/webhook`
- **Verify Token**: El mismo que pusiste en `.env` (WEBHOOK_VERIFY_TOKEN)
- **Webhook fields**: Selecciona `messages`

### 4.3 Verificar el webhook
Haz clic en "Verify and Save". Si todo está bien, verás "Webhook verified"

## 👥 Paso 5: Crear un Cliente

### 5.1 Preparar datos del cliente
Edita el archivo `test_create_client.py` con los datos de tu cliente:

```python
CLIENTE = {
    "name": "Mi Negocio",
    "phone_number": "+1234567890",  # Tu número de WhatsApp Business
    "phone_number_id": "123456789",  # El ID que te da Meta
    "welcome_message": "¡Hola! Bienvenido a Mi Negocio. ¿En qué puedo ayudarte?",
    "business_hours": "L-V: 9:00-18:00"
}
```

### 5.2 Ejecutar el script de gestión
```bash
python test_create_client.py
```

### 5.3 Crear el cliente
1. Selecciona opción `2` (Crear nuevo cliente)
2. Confirma con `s`
3. El sistema creará:
   - Un assistant en OpenAI con las FAQs
   - Un registro en la base de datos

Verás algo como:
```
✅ ¡Cliente creado exitosamente!
--------------------------------------------------
ID del cliente: 1
Assistant ID: asst_xxxxxxxxxxxxx
Estado: Activo
```

## 📤 Paso 6: Enviar Mensaje de Prueba

### 6.1 Desde WhatsApp
1. Abre WhatsApp en tu teléfono
2. Envía un mensaje al número de WhatsApp Business que configuraste
3. Escribe cualquier mensaje, por ejemplo: "Hola"

### 6.2 Verificar funcionamiento
En los logs de Docker deberías ver:
```
web-1     | 💬 Mensaje de 34674620669: Hola
web-1     | ✅ Cliente encontrado: Mi Negocio (ID: 1)
worker-1  | Task handle_message succeeded
```

### 6.3 Respuesta del bot
Recibirás una respuesta automática basada en:
- El mensaje de bienvenida configurado
- Las FAQs que definiste
- El contexto de la conversación

## 🛠️ Gestión de Clientes

El script `test_create_client.py` ofrece un menú completo:

```
1. Listar clientes          - Ver todos los clientes
2. Crear nuevo cliente      - Agregar un nuevo cliente
3. Desactivar cliente       - Soft delete (mantiene datos)
4. Borrar permanentemente   - Hard delete (elimina todo)
5. BORRAR TODOS            - Eliminar todos los clientes
6. Salir
```

### Comandos útiles con curl:

```bash
# Listar clientes
curl http://localhost:8082/clients | python3 -m json.tool

# Borrar un cliente permanentemente
curl -X DELETE "http://localhost:8082/clients/1?hard_delete=true"

# Borrar TODOS los clientes
curl -X DELETE "http://localhost:8082/clients?confirm=true"
```

## 🔍 Monitoreo y Debugging

### Ver logs en tiempo real
```bash
# Logs filtrados de mensajes
docker compose logs -f web worker | grep -E "💬|📤|✅|❌"
```

### Verificar estado de servicios
```bash
# Estado de contenedores
docker compose ps

# Verificar base de datos
docker compose exec db psql -U whatsapp_user -d whatsapp_bot -c "SELECT * FROM client;"
```

## ⚠️ Solución de Problemas

### El webhook no se verifica
- Verifica que ngrok esté corriendo
- Confirma que el WEBHOOK_VERIFY_TOKEN coincida
- Revisa los logs: `docker compose logs web`

### No llegan mensajes
- Verifica que el webhook esté suscrito a "messages"
- Confirma que el ACCESS_TOKEN sea válido
- Revisa que el phone_number_id sea correcto

### Error "Ya existe un cliente con phone_number_id"
- Usa el script para borrar el cliente anterior
- O actualiza el existente en lugar de crear uno nuevo

## 🚀 Deployment a Producción

Para producción, reemplaza ngrok con un dominio real:
1. Despliega en Railway, Render, o tu servidor
2. Configura HTTPS con certificado SSL
3. Actualiza el webhook en Meta con tu dominio
4. Configura variables de entorno en tu plataforma

## 📞 Soporte

Si encuentras problemas:
1. Revisa los logs detallados
2. Verifica las credenciales en `.env`
3. Confirma que todos los servicios estén activos
4. Consulta la documentación de Meta WhatsApp Business API 