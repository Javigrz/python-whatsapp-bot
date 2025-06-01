import httpx
import hashlib
import hmac
from typing import Optional
from src.core.settings import settings


class MetaError(Exception):
    """Excepción personalizada para errores de Meta"""
    pass


class MetaClient:
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v19.0"
        self.access_token = settings.meta_access_token
        self.app_secret = settings.meta_app_secret
        self.timeout = httpx.Timeout(10.0, connect=5.0)
    
    async def register_phone_number(self, phone_number: str) -> str:
        """Registra un número de teléfono en WhatsApp Business"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/{settings.phone_number_id}/whatsapp_business_accounts",
                    params={"access_token": self.access_token},
                    json={"phone_number": phone_number}
                )
                
                if response.status_code == 200:
                    return response.json().get("id", "")
                elif response.status_code == 400:
                    # Número ya registrado
                    return settings.phone_number_id
                else:
                    raise MetaError(f"Error registrando número: {response.text}")
                    
        except httpx.TimeoutException:
            raise MetaError("Timeout al registrar número")
        except Exception as e:
            raise MetaError(f"Error en registro: {str(e)}")
    
    async def set_webhook(self, phone_number_id: str, url: str) -> None:
        """Configura el webhook para recibir mensajes"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/{phone_number_id}/subscriptions",
                    params={"access_token": self.access_token},
                    json={
                        "callback_url": url,
                        "verify_token": "released_verify_token",
                        "fields": ["messages"]
                    }
                )
                
                if response.status_code != 200:
                    raise MetaError(f"Error configurando webhook: {response.text}")
                    
        except httpx.TimeoutException:
            raise MetaError("Timeout al configurar webhook")
        except Exception as e:
            raise MetaError(f"Error en webhook: {str(e)}")
    
    async def send_message(self, phone_number_id: str, wa_id: str, text: str) -> None:
        """Envía un mensaje de texto a través de WhatsApp"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/{phone_number_id}/messages",
                    headers={
                        "Authorization": f"Bearer {self.access_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "messaging_product": "whatsapp",
                        "to": wa_id,
                        "type": "text",
                        "text": {"body": text}
                    }
                )
                
                if response.status_code != 200:
                    raise MetaError(f"Error enviando mensaje: {response.text}")
                    
        except httpx.TimeoutException:
            raise MetaError("Timeout al enviar mensaje")
        except Exception as e:
            raise MetaError(f"Error en envío: {str(e)}")
    
    def send_message_sync(self, phone_number_id: str, wa_id: str, text: str) -> None:
        """Envía un mensaje de texto a través de WhatsApp (versión síncrona)"""
        import requests
        
        try:
            response = requests.post(
                f"{self.base_url}/{phone_number_id}/messages",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "messaging_product": "whatsapp",
                    "to": wa_id,
                    "type": "text",
                    "text": {"body": text}
                },
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise MetaError(f"Error enviando mensaje: {response.text}")
                
        except requests.Timeout:
            raise MetaError("Timeout al enviar mensaje")
        except requests.RequestException as e:
            raise MetaError(f"Error en envío: {str(e)}")
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verifica la firma del webhook de Meta"""
        expected_signature = hmac.new(
            self.app_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(f"sha256={expected_signature}", signature)


# Instancia global
meta_client = MetaClient()


# Funciones de conveniencia asíncronas
async def register_phone_number(phone_number: str) -> str:
    return await meta_client.register_phone_number(phone_number)


async def set_webhook(phone_number_id: str, url: str) -> None:
    await meta_client.set_webhook(phone_number_id, url)


async def send_message(phone_number_id: str, wa_id: str, text: str) -> None:
    await meta_client.send_message(phone_number_id, wa_id, text)


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    return meta_client.verify_webhook_signature(payload, signature)