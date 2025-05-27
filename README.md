# Released v1.0 - WhatsApp Business Bot Platform

Sistema automatizado para crear y gestionar bots de WhatsApp Business usando Meta Cloud API y OpenAI.

## 🏗️ Arquitectura

```
┌──────────────────────────┐
│  Meta WhatsApp Cloud API │
└─────────────┬────────────┘
              │ Webhook
              ▼
     ┌────────────────┐          Celery queue           ┌─────────────┐
     │ FastAPI (web)  │  ─────────────────────────────▶ │  Worker     │
     │  POST /agent   │                                 │(async tasks)│
     │  POST /webhook │ ◀────────────────────────────── │             │
     └────────────────┘          Redis broker           └─────────────┘
              │                                        ▲
              └── OpenAI (chat / assistants) ──────────┘
```

## 📦 Estructura del Proyecto

```
released/
├── src/
│   ├── api/
│   │   ├── ingest.py           # endpoint /agent
│   │   └── webhook.py          # endpoint /webhook
│   ├── core/
│   │   ├── settings.py         # gestión ENV (pydantic)
│   │   ├── openai_client.py    # wrapper OpenAI
│   │   ├── meta_client.py      # wrapper Meta Graph
│   │   └── models.py           # ORM (SQLModel)
│   ├── tasks.py                # definiciones Celery
│   └── main.py                 # create_app()
├── celery_worker/
│   └── worker.py               # arranca Celery
├── tests/                      # unit + integration + e2e
├── migrations/                 # Alembic
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── scripts/
    ├── provision_client.sh     # alta automática de cliente
    └── run_tests.sh
```

## 🚀 Instalación Rápida

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-org/released.git
cd released
```

### 2. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

### 3. Levantar servicios con Docker
```bash
docker compose up -d
```

### 4. Verificar que todo esté funcionando
```bash
curl http://localhost:8080/health
```

## 🔧 Configuración

### Variables de Entorno Requeridas

```env
# General
APP_ENV=prod
PORT=8080
ALLOWED_ORIGINS=*

# Meta
META_ACCESS_TOKEN=EAAG...        # Token de acceso de Meta
META_APP_SECRET=93c...           # App Secret de Meta
PHONE_NUMBER_ID=1098877...       # ID del número de WhatsApp

# OpenAI
OPENAI_API_KEY=sk-...            # API Key de OpenAI

# DB
POSTGRES_USER=released
POSTGRES_PASSWORD=released
POSTGRES_DB=released
DATABASE_URL=postgresql+asyncpg://released:released@db:5432/released

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
```

## 📡 API Endpoints

### POST /agent
Crea un nuevo agente de WhatsApp con FAQs personalizadas.

**Request:**
```json
{
  "phone_number": "+1234567890",
  "faqs": [
    {"q": "¿Qué es Released?", "a": "Un bot de WhatsApp"},
    {"q": "¿Cómo funciona?", "a": "Con inteligencia artificial"}
  ]
}
```

**Response (201):**
```json
{
  "agent_id": "asst_abc123",
  "phone_number_id": "1098877...",
  "status": "ok"
}
```

### POST /webhook
Recibe mensajes de WhatsApp (configurado automáticamente).

### GET /health
Verifica el estado del servicio.

## 🛠️ Desarrollo

### Ejecutar tests
```bash
./scripts/run_tests.sh
```

### Ejecutar localmente (sin Docker)
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar FastAPI
uvicorn src.main:app --reload

# En otra terminal, ejecutar Celery
celery -A src.tasks worker --loglevel=info
```

## 📦 Provisión de Nuevos Clientes

Para crear una nueva instancia para un cliente:

```bash
./scripts/provision_client.sh nombre_cliente +1234567890
```

Esto:
1. Crea una carpeta con la configuración del cliente
2. Configura el `.env` con el número proporcionado
3. Levanta los servicios Docker
4. La instancia queda lista para usar

## 🔍 Monitoreo y Observabilidad

- **Logs**: Disponibles en formato JSON para cada servicio
- **Métricas**: Prometheus exporta métricas de latencia y cola
- **Dashboards**: Grafana para visualización (configuración separada)

## 🔒 Seguridad

1. **HTTPS obligatorio** en producción
2. **Firma de webhooks** verificada con `X-Hub-Signature-256`
3. **Rate limiting**: 1 req/s por agente a OpenAI
4. **Rotación de tokens** cada 60 días
5. **No se almacenan mensajes** más de 14 días

## 🚦 CI/CD

El proyecto incluye GitHub Actions para:
- Ejecutar tests automáticamente
- Construir y publicar imagen Docker
- Desplegar automáticamente al hacer push a `main`

## 📊 Plan de Entrega

| Semana | Hito |
|--------|------|
| 1 | Estructura repo, Dockerfile, compose, .env |
| 2 | Endpoints /agent y /webhook operativos |
| 3 | Celery worker + OpenAI integración |
| 4 | CI/CD + script provisión funcionando |
| 5 | Tests 90% + observabilidad |
| 6 | Seguridad, hardening, documentación |

## ✅ Criterios de Completitud

- [ ] `pytest -q` devuelve 0 fallos
- [ ] `provision_client.sh demo +123456789` crea instancia funcional
- [ ] Webhook responde en < 2s
- [ ] Métricas disponibles en Prometheus
- [ ] Documentación completa

## 📝 Licencia

Propiedad de Released. Todos los derechos reservados.

---

**Nota**: No se deben añadir archivos o dependencias fuera de la estructura definida sin aprobación previa.

## ☝️ Alta de números de bot en WhatsApp Business

**IMPORTANTE:** El alta de nuevos números de bot (remitente) en WhatsApp Business Cloud API debe hacerse manualmente desde el panel de Meta Business. No es posible automatizar este proceso solo con la API, ya que Meta requiere verificación manual del número (OTP) y su aprobación.

**Flujo recomendado:**
1. El cliente te proporciona el número de bot (remitente).
2. Das de alta ese número manualmente en tu cuenta de WhatsApp Business desde el panel de Meta (https://business.facebook.com/).
3. Una vez aprobado, obtienes el `Phone Number ID` asociado a ese número en la sección de WhatsApp > Configuración de la API.
4. Guardas ese `Phone Number ID` en tu sistema para automatizar el envío de mensajes desde ese número.

A partir de ese momento, puedes gestionar y usar automáticamente los Phone Number ID para cada cliente en tu backend.
