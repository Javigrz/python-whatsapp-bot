# 📊 Sistema de Guardado de Conversaciones y Reportes

## 🎯 Descripción General

Este sistema permite guardar automáticamente todas las conversaciones de WhatsApp y generar reportes detallados para cada cliente. Cada mensaje se almacena en la base de datos, manteniendo el contexto completo de las conversaciones.

## ✨ Características Principales

- **💾 Guardado Automático**: Todas las interacciones se guardan automáticamente
- **🧠 Contexto Persistente**: Cada usuario mantiene su propio historial de conversación
- **📈 Reportes Múltiples**: Genera reportes en JSON, texto plano y HTML
- **🔍 Filtros Avanzados**: Filtra por usuario, fecha y cliente
- **📊 Estadísticas**: Obtén métricas de uso y actividad
- **🔄 Estados de Mensajes**: Rastrea si los mensajes fueron enviados, entregados o fallaron

## 🏗️ Arquitectura del Sistema

### Componentes Principales

```
┌─────────────────────┐
│   WhatsApp User     │
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│    Webhook API      │
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│   Celery Tasks      │ ← Guarda mensajes en DB
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│   OpenAI Client     │ ← Mantiene threads persistentes
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│    PostgreSQL       │ ← Almacena conversaciones
└─────────────────────┘
```

### Modelos de Datos

#### 📦 Tabla `messages`
```sql
- id: ID único del mensaje
- thread_id: Referencia al thread de conversación
- role: 'user' o 'assistant'
- content: Contenido del mensaje
- wa_id: WhatsApp ID del usuario
- phone_number_id: ID del número de WhatsApp Business
- created_at: Timestamp de creación
- status: Estado del mensaje (sent, delivered, read, failed)
- error_message: Mensaje de error si falló
```

## 🛠️ Configuración

### 1. Aplicar la Migración de Base de Datos

```bash
# Opción 1: Usar el script SQL directamente
psql -U tu_usuario -d tu_base_de_datos -f scripts/add_messages_table.sql

# Opción 2: Si tienes Alembic configurado
alembic upgrade head
```

### 2. Verificar Dependencias

Asegúrate de tener las siguientes dependencias en tu `requirements.txt`:
```
sqlmodel
celery
redis
psycopg2-binary
```

## 📡 API Endpoints

### 1. Listar Conversaciones de un Cliente

```bash
GET /clients/{client_id}/conversations
```

**Parámetros opcionales:**
- `wa_id`: Filtrar por número de WhatsApp específico
- `start_date`: Fecha de inicio (ISO 8601)
- `end_date`: Fecha de fin (ISO 8601)

**Ejemplo:**
```bash
curl "http://localhost:8082/clients/1/conversations?start_date=2024-01-01"
```

**Respuesta:**
```json
{
  "client": {
    "id": 1,
    "name": "Released",
    "phone_number": "+15556383785"
  },
  "total_conversations": 3,
  "conversations": [
    {
      "thread_id": 1,
      "wa_id": "+34123456789",
      "created_at": "2024-01-15T10:30:00",
      "last_message_at": "2024-01-15T11:45:00",
      "message_count": 12
    }
  ]
}
```

### 2. Obtener Mensajes de una Conversación

```bash
GET /clients/{client_id}/conversations/{wa_id}/messages
```

**Parámetros:**
- `format`: Formato de salida (`json`, `text`, `html`)

**Ejemplos:**

```bash
# Formato JSON (default)
curl "http://localhost:8082/clients/1/conversations/+34123456789/messages"

# Formato texto plano
curl "http://localhost:8082/clients/1/conversations/+34123456789/messages?format=text"

# Formato HTML
curl "http://localhost:8082/clients/1/conversations/+34123456789/messages?format=html" > reporte.html
```

## 🖥️ Scripts de CLI

### Script de Generación de Reportes

```bash
python scripts/generate_report.py [opciones]
```

**Opciones disponibles:**
- `--list`: Lista todos los clientes activos
- `--client-id`: ID del cliente para generar reporte
- `--wa-id`: WhatsApp ID específico (opcional)
- `--format`: `summary` o `detailed`

**Ejemplos de uso:**

```bash
# Listar todos los clientes
python scripts/generate_report.py --list

# Reporte resumido de todas las conversaciones de un cliente
python scripts/generate_report.py --client-id 1 --format summary

# Reporte detallado de una conversación específica
python scripts/generate_report.py --client-id 1 --wa-id +34123456789 --format detailed
```

## 📋 Ejemplos de Reportes

### Reporte en Texto Plano
```
REPORTE DE CONVERSACIÓN
Cliente: Released
Usuario WhatsApp: +34123456789
Fecha inicio: 2024-01-15 10:30:00
Última actividad: 2024-01-15 11:45:00
Total mensajes: 12
==================================================

[2024-01-15 10:30:00] Usuario:
Hola, quisiera información sobre el alquiler

[2024-01-15 10:30:05] Asistente:
¡Hola! Soy Released, el agente de IA para alquileres vacacionales. 
¿En qué puedo ayudarte?
```

### Reporte HTML
El formato HTML genera un archivo con estilo visual que incluye:
- Encabezado con información del cliente
- Mensajes con formato de chat (burbujas)
- Timestamps para cada mensaje
- Diferenciación visual entre usuario y asistente

## 🔧 Funciones Adicionales en el Código

### Limpiar Contexto de Conversación

```python
from src.core.openai_client import openai_client

# Limpiar el contexto de un usuario específico
openai_client.clear_conversation(conversation_id="+34123456789")
```

### Obtener Historial desde el Código

```python
# Obtener historial de conversación
history = openai_client.get_conversation_history(conversation_id="+34123456789")
```

## 📊 Consultas SQL Útiles

### Total de mensajes por cliente
```sql
SELECT c.name, COUNT(m.id) as total_messages
FROM clients c
JOIN threads t ON t.client_id = c.id
JOIN messages m ON m.thread_id = t.id
GROUP BY c.id, c.name
ORDER BY total_messages DESC;
```

### Conversaciones activas en las últimas 24 horas
```sql
SELECT DISTINCT t.wa_id, c.name, t.last_message_at
FROM threads t
JOIN clients c ON c.id = t.client_id
WHERE t.last_message_at > NOW() - INTERVAL '24 hours'
ORDER BY t.last_message_at DESC;
```

### Mensajes fallidos
```sql
SELECT m.*, c.name as client_name
FROM messages m
JOIN threads t ON t.id = m.thread_id
JOIN clients c ON c.id = t.client_id
WHERE m.status = 'failed'
ORDER BY m.created_at DESC;
```

## ⚡ Rendimiento y Optimización

### Índices Creados
- `idx_messages_thread_id`: Optimiza búsquedas por thread
- `idx_messages_wa_id`: Optimiza búsquedas por usuario
- `idx_messages_created_at`: Optimiza búsquedas por fecha

### Consideraciones
- Los threads de OpenAI se mantienen persistentes por usuario
- Solo se guardan los últimos 10 mensajes en memoria para el contexto
- Todos los mensajes se guardan permanentemente en la base de datos
- Las consultas están optimizadas con índices apropiados

## 🔒 Seguridad y Privacidad

- **Datos Sensibles**: Los mensajes contienen información personal
- **Acceso**: Implementa autenticación en los endpoints de reportes
- **GDPR**: Considera implementar funciones de exportación/eliminación de datos
- **Encriptación**: Considera encriptar mensajes sensibles en la base de datos

## 🐛 Solución de Problemas

### El contexto no se mantiene
1. Verifica que `conversation_id` se esté pasando correctamente
2. Revisa que el thread persista en `openai_client.conversation_threads`

### Los mensajes no se guardan
1. Verifica que Celery esté ejecutándose
2. Revisa los logs de Celery para errores
3. Verifica la conexión a la base de datos

### Error al generar reportes
1. Verifica que el cliente existe
2. Asegúrate de que hay mensajes en la conversación
3. Revisa permisos de base de datos

## 🚀 Próximos Pasos

1. **Dashboard Web**: Crear interfaz web para visualizar reportes
2. **Exportación**: Añadir exportación a PDF/Excel
3. **Métricas**: Añadir análisis de sentimiento y métricas de satisfacción
4. **Webhooks**: Notificar eventos importantes (conversación finalizada, error, etc.)
5. **Archivado**: Sistema de archivado automático de conversaciones antiguas 