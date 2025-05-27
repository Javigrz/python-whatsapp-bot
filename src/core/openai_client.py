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
    
    def create_assistant(self, faqs: List[Dict[str, str]], instructions: str = None) -> str:
        """Crea un assistant de OpenAI con las FAQs proporcionadas y/o un prompt personalizado"""
        try:
            if not instructions:
                instructions = "Eres un asistente virtual que responde preguntas basándote en las siguientes FAQs:\n\n"
                for faq in faqs:
                    instructions += f"P: {faq['q']}\nR: {faq['a']}\n\n"
                instructions += "Responde de manera clara y concisa. Si la pregunta no está relacionada con las FAQs, indica amablemente que solo puedes responder sobre los temas incluidos."
            assistant = self.client.beta.assistants.create(
                model="gpt-4o-mini",
                instructions=instructions,
                name="WhatsApp Business Assistant"
            )
            return assistant.id
        except Exception as e:
            raise OpenAIError(f"Error creando assistant: {str(e)}")
    
    def update_assistant(self, assistant_id: str, faqs: List[Dict[str, str]], instructions: str = None) -> str:
        """Actualiza un assistant existente con nuevas FAQs y/o prompt personalizado"""
        try:
            if not instructions:
                instructions = "Eres un asistente virtual que responde preguntas basándote en las siguientes FAQs:\n\n"
                for faq in faqs:
                    instructions += f"P: {faq['q']}\nR: {faq['a']}\n\n"
                instructions += "Responde de manera clara y concisa. Si la pregunta no está relacionada con las FAQs, indica amablemente que solo puedes responder sobre los temas incluidos."
            assistant = self.client.beta.assistants.update(
                assistant_id=assistant_id,
                instructions=instructions,
                model="gpt-4o-mini"
            )
            return assistant.id
        except Exception as e:
            raise OpenAIError(f"Error actualizando assistant: {str(e)}")
    
    def get_answer(self, agent_id: str, text: str) -> str:
        """Obtiene respuesta del assistant para el texto dado"""
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


# Instancia global
openai_client = OpenAIClient()


# Funciones de conveniencia
def create_assistant(faqs: List[Dict[str, str]], instructions: str = None) -> str:
    return openai_client.create_assistant(faqs, instructions)


def update_assistant(assistant_id: str, faqs: List[Dict[str, str]], instructions: str = None) -> str:
    return openai_client.update_assistant(assistant_id, faqs, instructions)


def get_answer(agent_id: str, text: str) -> str:
    return openai_client.get_answer(agent_id, text) 