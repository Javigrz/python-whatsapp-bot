import openai
from typing import List, Dict
import json
from src.core.settings import settings


class OpenAIError(Exception):
    """Excepción personalizada para errores de OpenAI"""
    pass


class OpenAIClient:
    def __init__(self):
        self.client = None
    
    def _ensure_client(self):
        """Inicializar el cliente de OpenAI de forma lazy"""
        if self.client is None:
            if not settings.openai_api_key:
                raise OpenAIError("OPENAI_API_KEY no está configurada")
            self.client = openai.OpenAI(
                api_key=settings.openai_api_key,
                default_headers={"OpenAI-Beta": "assistants=v2"}
            )
    
    def create_assistant(self, faqs: List[Dict[str, str]]) -> str:
        """Crea un assistant de OpenAI con las FAQs proporcionadas"""
        self._ensure_client()
        try:
            # Crear contenido para el assistant
            instructions = "Eres un asistente virtual que responde preguntas basándote en las siguientes FAQs:\n\n"
            for faq in faqs:
                instructions += f"P: {faq['q']}\nR: {faq['a']}\n\n"
            
            instructions += "Responde de manera clara y concisa. Si la pregunta no está relacionada con las FAQs, indica amablemente que solo puedes responder sobre los temas incluidos."
            
            # Crear assistant
            assistant = self.client.beta.assistants.create(
                model="gpt-4o-mini",
                instructions=instructions,
                name="WhatsApp Business Assistant"
            )
            
            return assistant.id
        except Exception as e:
            raise OpenAIError(f"Error creando assistant: {str(e)}")
    
    def create_assistant_with_instructions(self, instructions: str, name: str = "WhatsApp Business Assistant") -> str:
        """Crea un assistant de OpenAI con instrucciones personalizadas"""
        self._ensure_client()
        try:
            # Crear assistant con instrucciones personalizadas
            assistant = self.client.beta.assistants.create(
                model="gpt-4o-mini",
                instructions=instructions,
                name=name
            )
            
            return assistant.id
        except Exception as e:
            raise OpenAIError(f"Error creando assistant: {str(e)}")
    
    def get_answer_with_thread(self, agent_id: str, thread_id: str, text: str) -> str:
        """Obtiene respuesta del assistant usando un thread específico"""
        self._ensure_client()
        try:
            # Añadir mensaje al thread existente
            self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=text
            )
            
            # Ejecutar assistant
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=agent_id
            )
            
            # Esperar a que termine
            import time
            while run.status in ["queued", "in_progress"]:
                time.sleep(0.5)
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )
            
            if run.status == "completed":
                # Obtener mensajes
                messages = self.client.beta.threads.messages.list(
                    thread_id=thread_id,
                    limit=1
                )
                # El primer mensaje es la respuesta más reciente
                return messages.data[0].content[0].text.value
            else:
                raise OpenAIError(f"Run falló con estado: {run.status}")
                
        except Exception as e:
            raise OpenAIError(f"Error obteniendo respuesta: {str(e)}")
    
    def create_thread(self) -> str:
        """Crea un nuevo thread de conversación"""
        self._ensure_client()
        try:
            thread = self.client.beta.threads.create()
            return thread.id
        except Exception as e:
            raise OpenAIError(f"Error creando thread: {str(e)}")
    
    def get_answer(self, agent_id: str, text: str) -> str:
        """Obtiene respuesta del assistant para el texto dado"""
        self._ensure_client()
        try:
            # Crear thread
            thread = self.client.beta.threads.create()
            
            # Añadir mensaje
            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=text
            )
            
            # Ejecutar assistant
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=agent_id
            )
            
            # Esperar a que termine
            import time
            while run.status in ["queued", "in_progress"]:
                time.sleep(0.5)
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
            
            if run.status == "completed":
                # Obtener mensajes
                messages = self.client.beta.threads.messages.list(
                    thread_id=thread.id
                )
                # El primer mensaje es la respuesta más reciente
                return messages.data[0].content[0].text.value
            else:
                raise OpenAIError(f"Run falló con estado: {run.status}")
                
        except Exception as e:
            raise OpenAIError(f"Error obteniendo respuesta: {str(e)}")


# Instancia global (lazy initialization)
_openai_client = None

def get_openai_client() -> OpenAIClient:
    """Obtener la instancia global del cliente OpenAI (lazy initialization)"""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAIClient()
    return _openai_client


# Funciones de conveniencia
def create_assistant(faqs: List[Dict[str, str]]) -> str:
    return get_openai_client().create_assistant(faqs)


def create_assistant_with_instructions(instructions: str, name: str = "WhatsApp Business Assistant") -> str:
    return get_openai_client().create_assistant_with_instructions(instructions, name)


def get_answer(agent_id: str, text: str) -> str:
    return get_openai_client().get_answer(agent_id, text) 