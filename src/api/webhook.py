from fastapi import APIRouter, Request, HTTPException, Header, Depends
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.core.models import Agent, Client
from src.core.meta_client import verify_webhook_signature
from src.core.settings import settings
from src.tasks import handle_message
from typing import Optional
import json

router = APIRouter()


async def get_session(request: Request) -> AsyncSession:
    """Obtiene la sesión de la base de datos del request"""
    return request.state.db


@router.get("/webhook")
async def webhook_verify(
    request: Request
):
    """Verificación del webhook por Meta"""
    # Meta envía los parámetros con puntos, no con guiones bajos
    hub_mode = request.query_params.get("hub.mode")
    hub_verify_token = request.query_params.get("hub.verify_token")
    hub_challenge = request.query_params.get("hub.challenge")
    
    print(f"🔍 Verificando webhook: mode={hub_mode}, token={hub_verify_token}, challenge={hub_challenge}")
    
    if hub_mode == "subscribe" and hub_verify_token == settings.verify_token:
        print("✅ Webhook verificado correctamente")
        # Meta espera que devolvamos el challenge como texto plano
        return PlainTextResponse(content=hub_challenge)
    
    print("❌ Verificación de webhook falló")
    raise HTTPException(status_code=403, detail="Verificación falló")


@router.post("/webhook")
async def webhook_handler(
    request: Request,
    session: AsyncSession = Depends(get_session),
    x_hub_signature_256: Optional[str] = Header(None)
):
    """
    Maneja los mensajes entrantes de WhatsApp.
    
    Proceso:
    1. Verificar firma
    2. Extraer datos del mensaje
    3. Buscar agente
    4. Encolar tarea en Celery
    5. Responder 200 inmediatamente
    """
    try:
        # 1. Verificar firma
        body = await request.body()
        
        if x_hub_signature_256:
            if not verify_webhook_signature(body, x_hub_signature_256):
                print("❌ Firma de webhook inválida")
                raise HTTPException(status_code=401, detail="Firma inválida")
        
        # 2. Parsear payload
        data = json.loads(body)
        print(f"📨 Webhook recibido: {json.dumps(data, indent=2)}")
        
        # Extraer información del mensaje
        entry = data.get("entry", [])
        if not entry:
            return JSONResponse(content={}, status_code=200)
        
        changes = entry[0].get("changes", [])
        if not changes:
            return JSONResponse(content={}, status_code=200)
        
        value = changes[0].get("value", {})
        messages = value.get("messages", [])
        metadata = value.get("metadata", {})
        
        if not messages:
            return JSONResponse(content={}, status_code=200)
        
        # Procesar cada mensaje
        phone_number_id = metadata.get("phone_number_id")
        
        for message in messages:
            # Solo procesar mensajes de texto
            if message.get("type") != "text":
                continue
            
            sender = message.get("from")
            text_data = message.get("text", {})
            body_text = text_data.get("body", "")
            
            print(f"💬 Mensaje de {sender}: {body_text}")
            
            if not all([phone_number_id, sender, body_text]):
                continue
            
            # 3. Buscar agente en la base de datos
            # Primero buscar en la tabla de clientes (nueva)
            result = await session.execute(
                select(Client).where(
                    Client.phone_number_id == phone_number_id,
                    Client.active == True
                )
            )
            client = result.scalar_one_or_none()
            
            if client:
                print(f"✅ Cliente encontrado: {client.name} (ID: {client.id})")
                # Encolar con el assistant del cliente
                handle_message.delay(
                    client.assistant_id,
                    client.phone_number_id,
                    sender,
                    body_text
                )
                continue
            
            # Si no hay cliente, buscar en agents (compatibilidad hacia atrás)
            result = await session.execute(
                select(Agent).where(Agent.phone_number_id == phone_number_id)
            )
            agent = result.scalar_one_or_none()
            
            if not agent:
                print(f"⚠️  No se encontró agente para phone_number_id: {phone_number_id}")
                # Por ahora, usar el assistant ID de las variables de entorno si existe
                if settings.openai_assistant_id:
                    print(f"📌 Usando assistant ID por defecto: {settings.openai_assistant_id}")
                    # Encolar con el assistant por defecto
                    handle_message.delay(
                        settings.openai_assistant_id,
                        phone_number_id,
                        sender,
                        body_text
                    )
                continue
            
            # 4. Encolar tarea en Celery
            print(f"📤 Encolando mensaje para procesamiento...")
            handle_message.delay(
                agent.agent_id,
                agent.phone_number_id,
                sender,
                body_text
            )
        
        # 5. Responder inmediatamente (< 100ms)
        return JSONResponse(content={}, status_code=200)
        
    except json.JSONDecodeError:
        print("❌ Error decodificando JSON")
        return JSONResponse(content={}, status_code=200)
    except Exception as e:
        # Log pero responder 200 para evitar reintentos de Meta
        print(f"❌ Error en webhook: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(content={}, status_code=200) 