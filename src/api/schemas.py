from pydantic import BaseModel, Field, validator
from typing import List, Dict
import re


class FAQ(BaseModel):
    q: str = Field(..., min_length=1, description="Pregunta")
    a: str = Field(..., min_length=1, description="Respuesta")


class AgentCreate(BaseModel):
    phone_number: str = Field(..., description="Número en formato E.164")
    faqs: List[FAQ] = Field(..., min_items=1, description="Lista de preguntas y respuestas")
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        # Validar formato E.164
        if not re.match(r'^\+[1-9]\d{1,14}$', v):
            raise ValueError('El número debe estar en formato E.164 (ej: +1234567890)')
        return v


class AgentResponse(BaseModel):
    agent_id: str
    phone_number_id: str
    status: str = "ok" 