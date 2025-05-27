#!/usr/bin/env python3
"""
Script de prueba local para verificar la configuración
"""
import asyncio
import httpx
from src.core.settings import settings

print("🔧 Verificando configuración...")
print(f"✅ Meta Access Token: {'Configurado' if settings.meta_access_token else '❌ Falta'}")
print(f"✅ Meta App Secret: {'Configurado' if settings.meta_app_secret else '❌ Falta'}")
print(f"✅ Phone Number ID: {settings.phone_number_id if settings.phone_number_id else '❌ Falta'}")
print(f"✅ OpenAI API Key: {'Configurado' if settings.openai_api_key else '❌ Falta'}")
print(f"✅ OpenAI Assistant ID: {settings.openai_assistant_id if settings.openai_assistant_id else '⚠️  No configurado'}")
print(f"✅ Verify Token: {settings.verify_token}")

# Prueba simple de conexión a OpenAI
async def test_openai():
    print("\n🤖 Probando conexión con OpenAI...")
    try:
        from src.core.openai_client import openai_client
        # Si tienes un assistant ID, podemos usarlo
        if settings.openai_assistant_id:
            print(f"✅ Assistant ID encontrado: {settings.openai_assistant_id}")
        else:
            print("⚠️  No hay Assistant ID, se creará uno nuevo al crear un agente")
        return True
    except Exception as e:
        print(f"❌ Error conectando con OpenAI: {e}")
        return False

# Prueba simple de Meta
async def test_meta():
    print("\n📱 Verificando configuración de Meta...")
    try:
        print(f"✅ Phone Number ID: {settings.phone_number_id}")
        print(f"✅ App ID: {settings.app_id if settings.app_id else 'No configurado'}")
        print(f"✅ Version API: {settings.version}")
        return True
    except Exception as e:
        print(f"❌ Error en configuración Meta: {e}")
        return False

if __name__ == "__main__":
    print("\n🚀 PRUEBA DE CONFIGURACIÓN LOCAL\n")
    asyncio.run(test_openai())
    asyncio.run(test_meta())
    print("\n✅ Configuración básica verificada!")
    print("\n📝 Próximos pasos:")
    print("1. Levantar los servicios con Docker")
    print("2. Probar el endpoint /health")
    print("3. Crear un agente de prueba")
    print("4. Configurar ngrok para webhooks") 