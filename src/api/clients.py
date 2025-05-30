from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Optional
from datetime import datetime
from sqlalchemy import func

from src.core.models import Client, Thread, Message
from src.core.openai_client import create_assistant, update_assistant
from src.api.webhook import get_session

router = APIRouter()


class FAQ(BaseModel):
    q: str
    a: str
    context: Optional[bool] = False  # Indica si este FAQ debe mantener contexto de conversación


class CreateClientRequest(BaseModel):
    name: str
    phone_number: str
    phone_number_id: str
    host_email: str  # Email del host para recibir reportes
    faqs: List[FAQ]
    welcome_message: Optional[str] = None
    business_hours: Optional[str] = None
    system_prompt: Optional[str] = None
    maintain_context: Optional[bool] = True  # Por defecto, mantener contexto


class UpdateClientRequest(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    active: Optional[bool] = None
    welcome_message: Optional[str] = None
    business_hours: Optional[str] = None


class ClientResponse(BaseModel):
    id: int
    name: str
    phone_number: str
    phone_number_id: str
    assistant_id: str
    active: bool
    created_at: datetime
    updated_at: datetime
    welcome_message: Optional[str] = None
    business_hours: Optional[str] = None


@router.post("/clients", response_model=ClientResponse)
async def create_client(
    request: CreateClientRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Crear un nuevo cliente o actualizar uno existente si el phone_number_id ya existe.
    
    Proceso:
    1. Si el phone_number_id existe:
       - Actualiza el cliente existente con los nuevos datos
       - Actualiza el assistant en OpenAI con las nuevas FAQs
    2. Si no existe:
       - Crea un nuevo assistant en OpenAI con las FAQs
       - Guarda el nuevo cliente en la base de datos
    3. Retorna los datos del cliente
    """
    try:
        # Verificar si ya existe un cliente con ese phone_number_id
        result = await session.execute(
            select(Client).where(Client.phone_number_id == request.phone_number_id)
        )
        existing = result.scalar_one_or_none()
        
        # Modificar las instrucciones para incluir manejo de contexto si está habilitado
        if request.maintain_context:
            context_instructions = """
            MANEJO DE CONTEXTO:
            - Mantén el contexto de la conversación anterior
            - Si el huésped hace referencia a algo mencionado antes, úsalo para dar una respuesta más precisa
            - Si hay ambigüedad, pide clarificación
            - Mantén un tono conversacional y natural
            
            """
            if request.system_prompt:
                instructions = context_instructions + "\n" + request.system_prompt
            else:
                instructions = context_instructions + "\nEres un asistente virtual que responde preguntas basándote en las siguientes FAQs:\n\n"
                for faq in request.faqs:
                    instructions += f"P: {faq.q}\nR: {faq.a}\n\n"
                instructions += "Responde de manera clara y concisa. Si la pregunta no está relacionada con las FAQs, indica amablemente que solo puedes responder sobre los temas incluidos."
        else:
            instructions = "Eres un asistente virtual que responde preguntas basándote en las siguientes FAQs:\n\n"
            for faq in request.faqs:
                instructions += f"P: {faq.q}\nR: {faq.a}\n\n"
            instructions += "Responde de manera clara y concisa. Si la pregunta no está relacionada con las FAQs, indica amablemente que solo puedes responder sobre los temas incluidos."
        
        faqs_dict = [{"q": faq.q, "a": faq.a} for faq in request.faqs]
        
        if existing:
            print(f"⚠️ Cliente existente encontrado (ID: {existing.id}). Se actualizará con la nueva información.")
            # Actualizar el assistant existente
            assistant_id = update_assistant(existing.assistant_id, faqs_dict, instructions=instructions)
            print(f"✅ Assistant actualizado: {assistant_id}")
            
            # Actualizar cliente existente
            existing.name = request.name
            existing.phone_number = request.phone_number
            existing.assistant_id = assistant_id
            existing.welcome_message = request.welcome_message
            existing.business_hours = request.business_hours
            existing.updated_at = datetime.utcnow()
            
            await session.commit()
            await session.refresh(existing)
            
            print(f"✅ Cliente '{existing.name}' actualizado exitosamente (ID: {existing.id})")
            
            return ClientResponse(
                id=existing.id,
                name=existing.name,
                phone_number=existing.phone_number,
                phone_number_id=existing.phone_number_id,
                assistant_id=existing.assistant_id,
                active=existing.active,
                created_at=existing.created_at,
                updated_at=existing.updated_at,
                welcome_message=existing.welcome_message,
                business_hours=existing.business_hours
            )
        else:
            # Crear nuevo assistant
            assistant_id = create_assistant(faqs_dict, instructions=instructions)
            print(f"✅ Assistant creado: {assistant_id}")
            
            # Crear nuevo cliente
            client = Client(
                name=request.name,
                phone_number=request.phone_number,
                phone_number_id=request.phone_number_id,
                host_email=request.host_email,
                assistant_id=assistant_id,
                active=True,
                welcome_message=request.welcome_message,
                business_hours=request.business_hours
            )
            
            session.add(client)
            await session.commit()
            await session.refresh(client)
            
            print(f"✅ Cliente '{client.name}' creado exitosamente (ID: {client.id})")
            
            return ClientResponse(
                id=client.id,
                name=client.name,
                phone_number=client.phone_number,
                phone_number_id=client.phone_number_id,
                assistant_id=client.assistant_id,
                active=client.active,
                created_at=client.created_at,
                updated_at=client.updated_at,
                welcome_message=client.welcome_message,
                business_hours=client.business_hours
            )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error {'actualizando' if existing else 'creando'} cliente: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clients", response_model=List[ClientResponse])
async def list_clients(
    session: AsyncSession = Depends(get_session),
    active_only: bool = False
):
    """Listar todos los clientes"""
    query = select(Client)
    if active_only:
        query = query.where(Client.active == True)
    
    result = await session.execute(query)
    clients = result.scalars().all()
    
    return [
        ClientResponse(
            id=client.id,
            name=client.name,
            phone_number=client.phone_number,
            phone_number_id=client.phone_number_id,
            assistant_id=client.assistant_id,
            active=client.active,
            created_at=client.created_at,
            updated_at=client.updated_at,
            welcome_message=client.welcome_message,
            business_hours=client.business_hours
        )
        for client in clients
    ]


@router.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Obtener un cliente específico"""
    result = await session.execute(
        select(Client).where(Client.id == client_id)
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    return ClientResponse(
        id=client.id,
        name=client.name,
        phone_number=client.phone_number,
        phone_number_id=client.phone_number_id,
        assistant_id=client.assistant_id,
        active=client.active,
        created_at=client.created_at,
        updated_at=client.updated_at,
        welcome_message=client.welcome_message,
        business_hours=client.business_hours
    )


@router.patch("/clients/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    request: UpdateClientRequest,
    session: AsyncSession = Depends(get_session)
):
    """Actualizar un cliente"""
    result = await session.execute(
        select(Client).where(Client.id == client_id)
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Actualizar solo los campos proporcionados
    if request.name is not None:
        client.name = request.name
    if request.phone_number is not None:
        client.phone_number = request.phone_number
    if request.active is not None:
        client.active = request.active
    if request.welcome_message is not None:
        client.welcome_message = request.welcome_message
    if request.business_hours is not None:
        client.business_hours = request.business_hours
    
    client.updated_at = datetime.utcnow()
    
    await session.commit()
    await session.refresh(client)
    
    return ClientResponse(
        id=client.id,
        name=client.name,
        phone_number=client.phone_number,
        phone_number_id=client.phone_number_id,
        assistant_id=client.assistant_id,
        active=client.active,
        created_at=client.created_at,
        updated_at=client.updated_at,
        welcome_message=client.welcome_message,
        business_hours=client.business_hours
    )


@router.delete("/{client_id}", response_model=ClientResponse)
async def delete_client(
    client_id: int,
    session: AsyncSession = Depends(get_session),
    hard_delete: bool = Query(False, description="Si es True, elimina permanentemente")
):
    """Eliminar un cliente (soft delete por defecto)"""
    # Buscar el cliente
    result = await session.execute(
        select(Client).where(Client.id == client_id)
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    if hard_delete:
        # Eliminar permanentemente
        await session.delete(client)
        message = f"Cliente {client.name} eliminado permanentemente"
    else:
        # Soft delete
        client.active = False
        session.add(client)
        message = f"Cliente {client.name} desactivado"
    
    await session.commit()
    
    return {"message": message}


@router.delete("/clients")
async def delete_all_clients(
    session: AsyncSession = Depends(get_session),
    confirm: bool = False
):
    """
    Eliminar TODOS los clientes de la base de datos.
    Requiere confirmación explícita con confirm=true
    """
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Debes confirmar la eliminación de todos los clientes con ?confirm=true"
        )
    
    # Obtener todos los clientes
    result = await session.execute(select(Client))
    clients = result.scalars().all()
    
    count = len(clients)
    
    # Eliminar todos los clientes
    for client in clients:
        await session.delete(client)
    
    await session.commit()
    
    return {"message": f"{count} clientes eliminados permanentemente"}


@router.get("/{client_id}/conversations")
async def get_client_conversations(
    client_id: int,
    session: AsyncSession = Depends(get_session),
    wa_id: Optional[str] = Query(None, description="Filtrar por número de WhatsApp del usuario"),
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin")
):
    """Obtener todas las conversaciones de un cliente"""
    # Verificar que el cliente existe
    result = await session.execute(
        select(Client).where(Client.id == client_id)
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Construir query base
    query = select(Thread).where(Thread.client_id == client_id)
    
    # Aplicar filtros
    if wa_id:
        query = query.where(Thread.wa_id == wa_id)
    
    if start_date:
        query = query.where(Thread.created_at >= start_date)
    
    if end_date:
        query = query.where(Thread.created_at <= end_date)
    
    # Ejecutar query
    result = await session.execute(query.order_by(Thread.created_at.desc()))
    threads = result.scalars().all()
    
    # Preparar respuesta
    conversations = []
    for thread in threads:
        # Contar mensajes
        message_count_result = await session.execute(
            select(func.count(Message.id)).where(Message.thread_id == thread.id)
        )
        message_count = message_count_result.scalar()
        
        conversations.append({
            "thread_id": thread.id,
            "wa_id": thread.wa_id,
            "created_at": thread.created_at,
            "last_message_at": thread.last_message_at,
            "message_count": message_count
        })
    
    return {
        "client": {
            "id": client.id,
            "name": client.name,
            "phone_number": client.phone_number
        },
        "total_conversations": len(conversations),
        "conversations": conversations
    }


@router.get("/{client_id}/conversations/{wa_id}/messages")
async def get_conversation_messages(
    client_id: int,
    wa_id: str,
    session: AsyncSession = Depends(get_session),
    format: str = Query("json", description="Formato de salida: json, text, html")
):
    """Obtener todos los mensajes de una conversación específica"""
    # Verificar que el cliente existe
    result = await session.execute(
        select(Client).where(Client.id == client_id)
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Buscar el thread
    result = await session.execute(
        select(Thread).where(
            Thread.client_id == client_id,
            Thread.wa_id == wa_id
        )
    )
    thread = result.scalar_one_or_none()
    
    if not thread:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    # Obtener todos los mensajes
    result = await session.execute(
        select(Message)
        .where(Message.thread_id == thread.id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()
    
    if format == "text":
        # Formato texto plano
        report = f"REPORTE DE CONVERSACIÓN\n"
        report += f"Cliente: {client.name}\n"
        report += f"Usuario WhatsApp: {wa_id}\n"
        report += f"Fecha inicio: {thread.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Última actividad: {thread.last_message_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Total mensajes: {len(messages)}\n"
        report += "="*50 + "\n\n"
        
        for msg in messages:
            timestamp = msg.created_at.strftime('%Y-%m-%d %H:%M:%S')
            role = "Usuario" if msg.role == "user" else "Asistente"
            report += f"[{timestamp}] {role}:\n{msg.content}\n\n"
        
        return PlainTextResponse(content=report)
    
    elif format == "html":
        # Formato HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Conversación - {client.name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f0f0f0; padding: 15px; border-radius: 5px; }}
                .message {{ margin: 10px 0; padding: 10px; border-radius: 5px; }}
                .user {{ background: #e3f2fd; margin-left: 0; margin-right: 20%; }}
                .assistant {{ background: #f5f5f5; margin-left: 20%; margin-right: 0; }}
                .timestamp {{ font-size: 0.8em; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Reporte de Conversación</h1>
                <p><strong>Cliente:</strong> {client.name}</p>
                <p><strong>Usuario WhatsApp:</strong> {wa_id}</p>
                <p><strong>Total mensajes:</strong> {len(messages)}</p>
            </div>
        """
        
        for msg in messages:
            role_class = "user" if msg.role == "user" else "assistant"
            role_name = "Usuario" if msg.role == "user" else "Asistente"
            timestamp = msg.created_at.strftime('%Y-%m-%d %H:%M:%S')
            
            html += f"""
            <div class="message {role_class}">
                <div class="timestamp">{timestamp} - {role_name}</div>
                <div>{msg.content}</div>
            </div>
            """
        
        html += "</body></html>"
        
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=html)
    
    else:
        # Formato JSON (default)
        return {
            "client": {
                "id": client.id,
                "name": client.name,
                "phone_number": client.phone_number
            },
            "conversation": {
                "wa_id": wa_id,
                "thread_id": thread.id,
                "created_at": thread.created_at,
                "last_message_at": thread.last_message_at,
                "total_messages": len(messages)
            },
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at,
                    "status": msg.status
                }
                for msg in messages
            ]
        } 