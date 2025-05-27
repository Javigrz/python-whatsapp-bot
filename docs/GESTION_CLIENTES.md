# Gestión de Clientes - WhatsApp Bot Multi-Tenant

## Resumen

Este sistema permite gestionar múltiples clientes/números de WhatsApp en una sola instalación. Cada cliente tiene su propio número de teléfono, assistant de OpenAI y configuración independiente.

## Arquitectura Multi-Cliente

```
┌──────────────────────┐
│   WhatsApp API       │
│ (Múltiples números)  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│    Webhook único     │ ← Un solo endpoint recibe todos los mensajes
│     /webhook         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Identificación por  │
│  phone_number_id     │ ← El sistema identifica de qué cliente viene
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   Base de datos     │
│  Tabla: clients     │ ← Busca la configuración del cliente
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   Procesamiento     │
│   (Celery + OpenAI) │ ← Usa el assistant_id específico del cliente
└──────────────────────┘
```

## Proceso Manual de Alta de Cliente

### Paso 1: Dar de alta el número en Meta Business

1. Ve a [Meta Business Manager](https://business.facebook.com/)
2. En tu cuenta de WhatsApp Business, ve a "Configuración" > "Números de teléfono"
3. Haz clic en "Agregar número de teléfono"
4. Sigue el proceso de verificación (código SMS/llamada)
5. Una vez verificado, obtendrás:
   - **Phone Number ID**: Un ID único como `631261586727899`
   - **Display Phone Number**: El número formateado como `+1 555 638 3785`

### Paso 2: Crear un Assistant en OpenAI

1. Ve a [OpenAI Platform](https://platform.openai.com/assistants)
2. Crea un nuevo assistant
3. Configura las instrucciones específicas para este cliente
4. Guarda el **Assistant ID** (ej: `asst_YBQJCXsLVp2IkB8UaYvgJshL`)

### Paso 3: Registrar el cliente en tu sistema

Usa el script de gestión de clientes:

```bash
# Dentro del contenedor
docker compose exec web python scripts/manage_clients.py add "Nombre Cliente" "+34123456789" "phone_number_id" "assistant_id"

# Ejemplo real:
docker compose exec web python scripts/manage_clients.py add "Mi Primer Cliente" "+15556383785" "631261586727899" "asst_YBQJCXsLVp2IkB8UaYvgJshL"
```

### Paso 4: Verificar el cliente

```bash
# Listar todos los clientes
docker compose exec web python scripts/manage_clients.py list
```

## Comandos de Gestión

### Agregar un cliente
```bash
docker compose exec web python scripts/manage_clients.py add "Nombre" "+34XXX" "phone_id" "assistant_id"
```

### Listar clientes
```bash
docker compose exec web python scripts/manage_clients.py list
```

### Desactivar un cliente
```bash
docker compose exec web python scripts/manage_clients.py deactivate <ID>
```

### Reactivar un cliente
```bash
docker compose exec web python scripts/manage_clients.py activate <ID>
```

## Estructura de la Base de Datos

### Tabla: clients
```sql
- id: ID interno del cliente
- name: Nombre descriptivo del cliente
- phone_number: Número de teléfono completo
- phone_number_id: ID de Meta/WhatsApp
- assistant_id: ID del assistant de OpenAI
- active: Estado activo/inactivo
- created_at: Fecha de creación
- updated_at: Última actualización
```

## Flujo de Mensajes

1. **Mensaje entrante**: WhatsApp envía al webhook
2. **Identificación**: El sistema extrae el `phone_number_id`
3. **Búsqueda**: Consulta en la tabla `clients`
4. **Procesamiento**: Usa el `assistant_id` del cliente
5. **Respuesta**: Envía desde el número del cliente

## Escalabilidad

- **Un deployment**: Maneja todos los clientes
- **Workers escalables**: Añade más workers según la carga
- **Base de datos compartida**: Todos los clientes en una BD
- **Sin límite de clientes**: El sistema escala horizontalmente

## Ejemplo Completo

```bash
# 1. Crear las tablas (solo la primera vez)
docker compose exec web python scripts/create_tables.py

# 2. Agregar un cliente
docker compose exec web python scripts/manage_clients.py add \
  "Restaurante La Plaza" \
  "+34666777888" \
  "631261586727899" \
  "asst_abc123xyz"

# 3. Verificar
docker compose exec web python scripts/manage_clients.py list

# 4. El cliente ya puede recibir mensajes
```

## Notas Importantes

1. **Webhook único**: Todos los números apuntan al mismo webhook
2. **Sin reinicio**: Puedes agregar clientes sin reiniciar el sistema
3. **Independencia**: Cada cliente tiene su propia configuración
4. **Historial separado**: Los threads de conversación son independientes
5. **Activación inmediata**: Los clientes están activos al crearlos 