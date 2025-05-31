#!/usr/bin/env python3
"""
Prueba final para verificar que todo funciona correctamente
"""
import requests
import json
import time

API_URL = "https://released-production.up.railway.app"

def test_health():
    """Verificar que la API esté sana"""
    print("🔍 Verificando salud de la API...")
    response = requests.get(f"{API_URL}/health")
    data = response.json()
    print(f"✅ Status: {data['status']}")
    print(f"✅ Database: {data['database']}")
    return True

def test_webhook_verification():
    """Verificar que el webhook verification funcione"""
    print("\n🔍 Verificando webhook verification...")
    response = requests.get(f"{API_URL}/webhook?hub.mode=subscribe&hub.challenge=test123&hub.verify_token=13")
    if response.status_code == 200 and response.text == "test123":
        print("✅ Webhook verification funcionando")
        return True
    else:
        print(f"❌ Fallo: {response.status_code} - {response.text}")
        return False

def test_message_processing():
    """Simular un mensaje de WhatsApp"""
    print("\n🔍 Simulando mensaje de WhatsApp...")
    
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "ENTRY_ID",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "15556383785",
                        "phone_number_id": "631261586727899"  # ID real del cliente
                    },
                    "messages": [{
                        "from": "test_user_123",
                        "id": "wamid.test123",
                        "timestamp": str(int(time.time())),
                        "text": {
                            "body": "Hola, necesito información sobre Released"
                        },
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    }
    
    response = requests.post(f"{API_URL}/webhook", json=payload)
    if response.status_code == 200:
        print("✅ Mensaje procesado correctamente")
        return True
    else:
        print(f"❌ Error procesando mensaje: {response.status_code}")
        return False

def test_client_lookup():
    """Verificar que el cliente esté registrado"""
    print("\n🔍 Verificando cliente Released...")
    response = requests.get(f"{API_URL}/clients")
    clients = response.json()
    
    released_client = next((c for c in clients if c['name'] == 'Released'), None)
    if released_client:
        print("✅ Cliente 'Released' encontrado:")
        print(f"   - Teléfono: {released_client['phone_number']}")
        print(f"   - Phone Number ID: {released_client['phone_number_id']}")
        print(f"   - Assistant ID: {released_client['assistant_id']}")
        print(f"   - Activo: {released_client['active']}")
        return True
    else:
        print("❌ Cliente 'Released' no encontrado")
        return False

if __name__ == "__main__":
    print("🚀 PRUEBA FINAL DEL BOT RELEASED")
    print("=" * 50)
    
    tests = [
        test_health,
        test_webhook_verification,
        test_client_lookup,
        test_message_processing
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Error en {test.__name__}: {e}")
    
    print(f"\n📊 RESULTADOS: {passed}/{len(tests)} pruebas pasaron")
    
    if passed == len(tests):
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! El bot está listo para producción.")
        print("\n📱 Para probar con WhatsApp real:")
        print("   1. Envía un mensaje a +1 (555) 638-3785")
        print("   2. El bot debería responder automáticamente")
        print("   3. Verifica los logs en Railway si hay problemas")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
