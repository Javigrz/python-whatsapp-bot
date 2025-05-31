from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Optional
from datetime import datetime

from src.core.models import Client
from src.core.openai_client import create_assistant
from src.api.webhook import get_session

router = APIRouter()


class FAQ(BaseModel):
    q: str
    a: str


class CreateClientRequest(BaseModel):
    name: str
    phone_number: str
    phone_number_id: str
    faqs: List[FAQ]
    welcome_message: Optional[str] = None
    business_hours: Optional[str] = None


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
    Crear un nuevo cliente.
    
    Proceso:
    1. Recibe FAQs y datos del cliente
    2. Crea un assistant en OpenAI con las FAQs
    3. Guarda el cliente en la base de datos
    4. Retorna los datos del cliente creado
    """
    try:
        # Verificar si ya existe un cliente con ese phone_number_id
        result = await session.execute(
            select(Client).where(Client.phone_number_id == request.phone_number_id)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe un cliente con phone_number_id: {request.phone_number_id}"
            )
        
        # Crear assistant en OpenAI con las FAQs
        print(f"📝 Creando assistant para {request.name} con {len(request.faqs)} FAQs...")
        faqs_dict = [{"q": faq.q, "a": faq.a} for faq in request.faqs]
        assistant_id = create_assistant(faqs_dict)
        print(f"✅ Assistant creado: {assistant_id}")
        
        # Crear cliente en la base de datos
        client = Client(
            name=request.name,
            phone_number=request.phone_number,
            phone_number_id=request.phone_number_id,
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
        print(f"❌ Error creando cliente: {str(e)}")
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


@router.delete("/clients/{client_id}")
async def delete_client(
    client_id: int,
    session: AsyncSession = Depends(get_session),
    hard_delete: bool = False
):
    """
    Eliminar un cliente.
    
    - hard_delete=False: Solo desactiva el cliente (soft delete)
    - hard_delete=True: Elimina completamente el cliente de la base de datos
    """
    result = await session.execute(
        select(Client).where(Client.id == client_id)
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    if hard_delete:
        # Eliminación completa
        await session.delete(client)
        await session.commit()
        return {"message": f"Cliente '{client.name}' eliminado permanentemente"}
    else:
        # Soft delete (solo desactivar)
        client.active = False
        client.updated_at = datetime.utcnow()
        await session.commit()
        return {"message": f"Cliente '{client.name}' desactivado exitosamente"}


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