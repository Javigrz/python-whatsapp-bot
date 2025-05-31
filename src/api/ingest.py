from fastapi import APIRouter, HTTPException, Request, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.api.schemas import AgentCreate, AgentResponse
from src.core.models import Agent
from src.core import meta_client
from src.core.openai_client import create_assistant, OpenAIError
from src.core.settings import settings
import asyncio
from typing import Dict

router = APIRouter()


async def get_session(request: Request) -> AsyncSession:
    """Obtiene la sesión de la base de datos del request"""
    return request.state.db


@router.post("/agent", response_model=AgentResponse, status_code=201)
async def create_agent(
    agent_data: AgentCreate,
    request: Request,
    session: AsyncSession = Depends(get_session)
) -> Dict:
    """
    Crea un nuevo agente de WhatsApp con las FAQs proporcionadas.
    
    Proceso:
    1. Validar entrada
    2. Registrar número en Meta
    3. Configurar webhook
    4. Crear assistant en OpenAI
    5. Guardar en base de datos
    """
    try:
        # Establecer timeout de 3 segundos
        async def create_with_timeout():
            # 1. Registrar número (si no está registrado)
            try:
                phone_number_id = await meta_client.register_phone_number(
                    agent_data.phone_number
                )
            except Exception as e:
                # Si el número ya está registrado, usar el ID de settings
                phone_number_id = settings.phone_number_id
            
            # 2. Configurar webhook
            webhook_url = f"https://{request.headers.get('host', 'localhost')}/webhook"
            await meta_client.set_webhook(phone_number_id, webhook_url)
            
            # 3. Crear assistant en OpenAI
            faqs_dict = [{"q": faq.q, "a": faq.a} for faq in agent_data.faqs]
            agent_id = await asyncio.to_thread(
                create_assistant,
                faqs_dict
            )
            
            # 4. Guardar en base de datos
            agent = Agent(
                phone_number_id=phone_number_id,
                agent_id=agent_id
            )
            session.add(agent)
            await session.commit()
            
            return {
                "agent_id": agent_id,
                "phone_number_id": phone_number_id,
                "status": "ok"
            }
        
        # Ejecutar con timeout
        result = await asyncio.wait_for(create_with_timeout(), timeout=3.0)
        return result
        
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Timeout al crear agente")
    except meta_client.MetaError as e:
        raise HTTPException(status_code=400, detail=f"Error con Meta: {str(e)}")
    except OpenAIError as e:
        raise HTTPException(status_code=400, detail=f"Error con OpenAI: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}") 