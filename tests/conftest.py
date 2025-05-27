import pytest
import asyncio
from typing import Generator
import os

# Configurar variables de entorno para tests
os.environ["META_ACCESS_TOKEN"] = "test_token"
os.environ["META_APP_SECRET"] = "test_secret"
os.environ["PHONE_NUMBER_ID"] = "test_phone_id"
os.environ["OPENAI_API_KEY"] = "test_openai_key"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://test:test@localhost:5432/test"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Crea un event loop para toda la sesión de tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def anyio_backend():
    """Backend para tests asíncronos"""
    return "asyncio" 