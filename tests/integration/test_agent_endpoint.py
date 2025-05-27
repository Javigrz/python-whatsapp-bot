import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from src.main import app
from src.api.schemas import AgentCreate
import asyncio


@pytest.mark.asyncio
async def test_create_agent_success():
    """Test de creación exitosa de un agente"""
    # Mockear las llamadas externas
    with patch("src.api.ingest.meta_client") as mock_meta:
        with patch("src.api.ingest.openai_client") as mock_openai:
            with patch("src.api.ingest.AsyncSession") as mock_session:
                # Configurar mocks
                mock_meta.register_phone_number = AsyncMock(return_value="12345")
                mock_meta.set_webhook = AsyncMock()
                mock_openai.create_assistant = AsyncMock(return_value="asst_abc123")
                
                # Datos de prueba
                agent_data = {
                    "phone_number": "+1234567890",
                    "faqs": [
                        {"q": "¿Qué es esto?", "a": "Un bot"},
                        {"q": "¿Cómo funciona?", "a": "Con IA"}
                    ]
                }
                
                # Ejecutar petición
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.post("/agent", json=agent_data)
                
                # Verificar respuesta
                assert response.status_code == 201
                data = response.json()
                assert data["agent_id"] == "asst_abc123"
                assert data["phone_number_id"] == "12345"
                assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_create_agent_invalid_phone():
    """Test de error con número de teléfono inválido"""
    agent_data = {
        "phone_number": "123456",  # Formato inválido
        "faqs": [{"q": "Test", "a": "Test"}]
    }
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/agent", json=agent_data)
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_create_agent_timeout():
    """Test de timeout al crear agente"""
    with patch("src.api.ingest.asyncio.wait_for") as mock_wait:
        # Simular timeout
        mock_wait.side_effect = asyncio.TimeoutError()
        
        agent_data = {
            "phone_number": "+1234567890",
            "faqs": [{"q": "Test", "a": "Test"}]
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/agent", json=agent_data)
        
        assert response.status_code == 504
        assert "Timeout" in response.json()["detail"] 