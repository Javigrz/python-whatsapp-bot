import openai
from typing import List, Dict
import json
from src.core.settings import settings


class OpenAIError(Exception):
    """Excepción personalizada para errores de OpenAI"""
    pass


class OpenAIClient:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=settings.openai_api_key,
            default_headers={"OpenAI-Beta": "assistants=v2"}
        )
        self.conversation_threads = {}  # Almacena thread_id por phone_number o conversation_id
    
    def create_assistant(self, faqs: List[Dict[str, str]] = None, instructions: str = None) -> str:
        """Crea un assistant de OpenAI con el prompt proporcionado"""
        try:
            if not instructions:
                raise OpenAIError("Se requiere un system_prompt para crear el assistant")
            
            assistant = self.client.beta.assistants.create(
                model="gpt-4o-mini",
                instructions=instructions,
                name="WhatsApp Business Assistant"
            )
            
            return assistant.id
        except Exception as e:
            raise OpenAIError(f"Error creando assistant: {str(e)}")
    
    def update_assistant(self, assistant_id: str, faqs: List[Dict[str, str]] = None, instructions: str = None) -> str:
        """Actualiza un assistant existente con el nuevo prompt"""
        try:
            if not instructions:
                raise OpenAIError("Se requiere un system_prompt para actualizar el assistant")
            
            assistant = self.client.beta.assistants.update(
                assistant_id=assistant_id,
                instructions=instructions,
                model="gpt-4o-mini"
            )
            
            return assistant.id
        except Exception as e:
            raise OpenAIError(f"Error actualizando assistant: {str(e)}")
    
    def get_or_create_thread(self, conversation_id: str) -> str:
        """Obtiene o crea un thread para una conversación específica"""
        if conversation_id not in self.conversation_threads:
            thread = self.client.beta.threads.create()
            self.conversation_threads[conversation_id] = thread.id
        return self.conversation_threads[conversation_id]
    
    def get_answer(self, agent_id: str, text: str, conversation_id: str = None) -> str:
        """Obtiene respuesta del assistant para el texto dado manteniendo el contexto"""
        try:
            # Si no se proporciona conversation_id, usar el agent_id como default
            if conversation_id is None:
                conversation_id = agent_id
            
            # Obtener o crear thread para esta conversación
            thread_id = self.get_or_create_thread(conversation_id)
            
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
                    thread_id=thread_id
                )
                # El primer mensaje es la respuesta más reciente
                response = messages.data[0].content[0].text.value
                
                return response
            else:
                raise OpenAIError(f"Run falló con estado: {run.status}")
                
        except Exception as e:
            raise OpenAIError(f"Error obteniendo respuesta: {str(e)}")
    
    def clear_conversation(self, conversation_id: str):
        """Limpia el historial de una conversación específica"""
        if conversation_id in self.conversation_threads:
            del self.conversation_threads[conversation_id]
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """Obtiene el historial completo de una conversación"""
        if conversation_id not in self.conversation_threads:
            return []
        
        thread_id = self.conversation_threads[conversation_id]
        messages = self.client.beta.threads.messages.list(
            thread_id=thread_id,
            order="asc"  # Orden cronológico
        )
        
        history = []
        for msg in messages.data:
            history.append({
                "role": msg.role,
                "content": msg.content[0].text.value if msg.content else "",
                "created_at": msg.created_at
            })
        
        return history


# Instancia global
openai_client = OpenAIClient()


# Funciones de conveniencia
def create_assistant(faqs: List[Dict[str, str]] = None, instructions: str = None) -> str:
    return openai_client.create_assistant(faqs, instructions)


def update_assistant(assistant_id: str, faqs: List[Dict[str, str]] = None, instructions: str = None) -> str:
    return openai_client.update_assistant(assistant_id, faqs, instructions)


def get_answer(agent_id: str, text: str, conversation_id: str = None) -> str:
    return openai_client.get_answer(agent_id, text, conversation_id) 