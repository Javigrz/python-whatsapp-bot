from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List


class Agent(SQLModel, table=True):
    """Modelo para agentes de WhatsApp"""
    __tablename__ = "agents"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    phone_number: str = Field(index=True, unique=True)
    phone_number_id: str = Field(index=True, unique=True)
    agent_id: str  # OpenAI Assistant ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relación con threads
    threads: List["Thread"] = Relationship(back_populates="agent")


class Client(SQLModel, table=True):
    """Modelo para gestionar múltiples clientes/números de WhatsApp"""
    __tablename__ = "clients"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str  # Nombre del cliente (ej: "Cliente 1", "Restaurante X")
    phone_number: str  # Número de teléfono (ej: +34123456789)
    phone_number_id: str = Field(index=True, unique=True)  # ID de Meta/WhatsApp
    assistant_id: str  # ID del assistant de OpenAI para este cliente
    host_email: str  # Email del host para recibir reportes
    active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Configuración adicional opcional
    welcome_message: Optional[str] = None
    business_hours: Optional[str] = None  # JSON string con horarios
    
    # Relación con threads
    threads: List["Thread"] = Relationship(back_populates="client")


class Thread(SQLModel, table=True):
    """Modelo para threads de conversación"""
    __tablename__ = "threads"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    wa_id: str = Field(index=True)  # WhatsApp ID del usuario
    thread_id: str  # OpenAI thread ID
    
    # Foreign keys
    agent_id: Optional[int] = Field(default=None, foreign_key="agents.id")
    client_id: Optional[int] = Field(default=None, foreign_key="clients.id")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_message_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relaciones
    agent: Optional[Agent] = Relationship(back_populates="threads")
    client: Optional[Client] = Relationship(back_populates="threads")
    messages: List["Message"] = Relationship(back_populates="thread")


class Message(SQLModel, table=True):
    """Modelo para almacenar todos los mensajes de una conversación"""
    __tablename__ = "messages"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    thread_id: int = Field(foreign_key="threads.id")
    
    # Información del mensaje
    role: str  # 'user' o 'assistant'
    content: str  # Contenido del mensaje
    wa_id: str  # WhatsApp ID del usuario
    phone_number_id: Optional[str] = None  # ID del número de WhatsApp Business
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata adicional
    message_id: Optional[str] = None  # ID del mensaje de WhatsApp
    status: Optional[str] = None  # sent, delivered, read, failed
    error_message: Optional[str] = None  # Si hubo error
    
    # Relación
    thread: Thread = Relationship(back_populates="messages") 