import pytest
from unittest.mock import patch, MagicMock
from src.core.openai_client import OpenAIClient, OpenAIError


@pytest.fixture
def openai_client():
    """Fixture que proporciona un cliente de OpenAI con mocks"""
    with patch("openai.OpenAI") as mock_openai:
        client = OpenAIClient()
        client.client = mock_openai.return_value
        yield client


def test_create_assistant_success(openai_client):
    """Test de creación exitosa de un assistant"""
    # Configurar mock
    mock_assistant = MagicMock()
    mock_assistant.id = "asst_abc123"
    openai_client.client.beta.assistants.create.return_value = mock_assistant
    
    # Datos de prueba
    faqs = [
        {"q": "¿Qué es Released?", "a": "Un bot de WhatsApp"},
        {"q": "¿Cómo funciona?", "a": "Con OpenAI"}
    ]
    
    # Ejecutar
    assistant_id = openai_client.create_assistant(faqs)
    
    # Verificar
    assert assistant_id == "asst_abc123"
    openai_client.client.beta.assistants.create.assert_called_once()


def test_create_assistant_error(openai_client):
    """Test de error al crear un assistant"""
    # Configurar mock para que falle
    openai_client.client.beta.assistants.create.side_effect = Exception("API error")
    
    # Datos de prueba
    faqs = [{"q": "Test", "a": "Test"}]
    
    # Verificar que se lanza la excepción correcta
    with pytest.raises(OpenAIError) as excinfo:
        openai_client.create_assistant(faqs)
    
    assert "Error creando assistant" in str(excinfo.value) 