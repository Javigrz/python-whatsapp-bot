# Flujo de Producción - WhatsApp Bot Multi-Cliente

## Resumen del Flujo

Este documento describe el proceso completo para dar de alta y gestionar clientes en producción.

## Flujo de Alta de Cliente

### 1. Proceso Manual (Tu lado)

1. **Registrar número en Meta Business**
   - Acceder a Meta Business Manager
   - Añadir el número de teléfono del cliente
   - Verificar el número (SMS/llamada)
   - Obtener el `PHONE_NUMBER_ID`

2. **Preparar las FAQs del cliente**
   - Recopilar las preguntas y respuestas del cliente
   - Formatear como JSON

### 2. Proceso Automático (API)

Llamar al endpoint de creación de cliente:

```bash
POST https://tu-dominio.com/clients
Content-Type: application/json

{
  "name": "Restaurante La Plaza",
  "phone_number": "+34666777888",
  "phone_number_id": "631261586727899",
  "faqs": [
    {
      "q": "¿Cuál es vuestro horario?",
      "a": "Abrimos de lunes a viernes de 9:00 a 22:00, y sábados de 10:00 a 23:00"
    },
    {
      "q": "¿Hacéis reservas?",
      "a": "Sí, puedes reservar llamando al +34666777888 o a través de nuestra web"
    },
    {
      "q": "¿Tenéis menú del día?",
      "a": "Sí, nuestro menú del día cuesta 12€ e incluye primer plato, segundo, postre y bebida"
    }
  ],
  "welcome_message": "¡Hola! Soy el asistente virtual del Restaurante La Plaza. ¿En qué puedo ayudarte?",
  "business_hours": "L-V: 9:00-22:00, S: 10:00-23:00"
}
```

### 3. Lo que hace la API automáticamente

1. **Crea un Assistant en OpenAI** con las FAQs proporcionadas
2. **Guarda el cliente** en la base de datos con:
   - Datos del cliente
   - `phone_number_id` de Meta
   - `assistant_id` de OpenAI
3. **Retorna la confirmación** con todos los IDs

### 4. Respuesta de la API

```json
{
  "id": 2,
  "name": "Restaurante La Plaza",
  "phone_number": "+34666777888",
  "phone_number_id": "631261586727899",
  "assistant_id": "asst_xyz123abc",
  "active": true,
  "created_at": "2024-05-27T22:00:00Z",
  "updated_at": "2024-05-27T22:00:00Z",
  "welcome_message": "¡Hola! Soy el asistente virtual...",
  "business_hours": "L-V: 9:00-22:00, S: 10:00-23:00"
}
```

## Endpoints Disponibles

### 1. Crear Cliente
```
POST /clients
```
- Crea el assistant en OpenAI automáticamente
- Guarda el cliente en la BD
- El cliente queda activo inmediatamente

### 2. Listar Clientes
```
GET /clients
GET /clients?active_only=true
```

### 3. Ver Cliente Específico
```
GET /clients/{id}
```

### 4. Actualizar Cliente
```
PATCH /clients/{id}
```
- Actualiza datos del cliente
- NO actualiza el assistant (las FAQs no se pueden cambiar por API)

### 5. Desactivar Cliente
```
DELETE /clients/{id}
```
- Soft delete: marca como inactivo
- Los mensajes a ese número dejarán de procesarse

## Configuración del Webhook en Meta

**IMPORTANTE**: Todos los clientes usan el mismo webhook.

En Meta Business, para cada número añadido:
1. Configurar webhook URL: `https://tu-dominio.com/webhook`
2. Token de verificación: El mismo para todos
3. Suscribirse a eventos: `messages`

## Diagrama del Flujo Completo

```
┌─────────────────┐
│  1. Alta Manual │
│  en Meta        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. POST a API  │
│  /clients       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. API crea:    │
│ - Assistant     │
│ - Cliente en BD │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. Cliente      │
│ activo y listo  │
└─────────────────┘
```

## Ejemplo con cURL

```bash
# Crear cliente
curl -X POST https://tu-api.com/clients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mi Cliente",
    "phone_number": "+34123456789",
    "phone_number_id": "123456789",
    "faqs": [
      {"q": "Pregunta 1", "a": "Respuesta 1"},
      {"q": "Pregunta 2", "a": "Respuesta 2"}
    ]
  }'

# Listar clientes activos
curl https://tu-api.com/clients?active_only=true

# Ver cliente específico
curl https://tu-api.com/clients/1

# Desactivar cliente
curl -X DELETE https://tu-api.com/clients/1
```

## Notas Importantes

1. **No necesitas acceso al servidor** después del deployment
2. **Todo se gestiona por API** excepto el alta en Meta
3. **Las FAQs se convierten en Assistant** automáticamente
4. **Un webhook para todos** los clientes
5. **Sin límite de clientes** en el mismo sistema 