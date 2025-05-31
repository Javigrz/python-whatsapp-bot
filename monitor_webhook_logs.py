#!/usr/bin/env python3
"""
Monitor de logs de Railway para detectar mensajes de WhatsApp en tiempo real
"""
import requests
import json
import time
from datetime import datetime
import threading

API_URL = "https://released-production.up.railway.app"

def crear_endpoint_monitor():
    """Crear un endpoint temporal para monitorear requests"""
    print("🔍 MONITOR DE WEBHOOK EN TIEMPO REAL")
    print("=" * 60)
    print("📱 Ahora envía un mensaje de WhatsApp al número configurado")
    print("🔍 Buscando actividad en el webhook...")
    print("-" * 60)
    
    # Contador de requests
    request_count = 0
    last_health_check = datetime.now()
    
    def verificar_actividad():
        nonlocal request_count, last_health_check
        
        while True:
            try:
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                # Hacer una petición de prueba cada 10 segundos
                if (datetime.now() - last_health_check).seconds >= 10:
                    response = requests.get(f"{API_URL}/health", timeout=5)
                    if response.status_code == 200:
                        print(f"[{timestamp}] 💚 API activa - Esperando mensajes...")
                    last_health_check = datetime.now()
                
                # Simular un mensaje de prueba cada 30 segundos para verificar
                time.sleep(5)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[{timestamp}] ❌ Error: {str(e)}")
                time.sleep(5)
    
    try:
        verificar_actividad()
    except KeyboardInterrupt:
        print("\n\n🛑 Monitor detenido")

def test_mensaje_directo():
    """Enviar un mensaje de prueba directamente al webhook"""
    print("\n🧪 ENVIANDO MENSAJE DE PRUEBA AL WEBHOOK...")
    print("=" * 60)
    
    # Timestamp actual
    timestamp = int(datetime.now().timestamp())
    
    # Payload de prueba realista
    test_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "BUSINESS_ACCOUNT_ID",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "+15556383785",
                                "phone_number_id": "631261586727899"
                            },
                            "contacts": [
                                {
                                    "profile": {
                                        "name": "Test User"
                                    },
                                    "wa_id": "34612345678"
                                }
                            ],
                            "messages": [
                                {
                                    "from": "34612345678",
                                    "id": f"wamid.test_{timestamp}",
                                    "timestamp": str(timestamp),
                                    "text": {
                                        "body": "Hola, ¿qué servicios ofrecéis?"
                                    },
                                    "type": "text"
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }
    
    print(f"📤 Enviando mensaje: '{test_payload['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']}'")
    print(f"📱 Simulando usuario: {test_payload['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']}")
    
    try:
        start_time = datetime.now()
        response = requests.post(
            f"{API_URL}/webhook",
            json=test_payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "WhatsApp/2.23.0"
            },
            timeout=30
        )
        end_time = datetime.now()
        
        print(f"📥 Respuesta HTTP: {response.status_code}")
        print(f"⏱️  Tiempo de respuesta: {(end_time - start_time).total_seconds():.2f}s")
        print(f"📄 Contenido respuesta: {response.text}")
        
        if response.status_code == 200:
            print("✅ El webhook procesó el mensaje correctamente")
            if response.text and response.text != "{}":
                print("💬 El bot generó una respuesta")
            else:
                print("⚠️  El webhook respondió OK pero sin contenido")
        else:
            print(f"❌ Error en webhook: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - El webhook tardó más de 30 segundos en responder")
    except Exception as e:
        print(f"❌ Error enviando al webhook: {e}")

def verificar_configuracion_actual():
    """Verificar la configuración actual del cliente Released"""
    print("\n🔍 VERIFICANDO CONFIGURACIÓN ACTUAL...")
    print("=" * 60)
    
    try:
        # Obtener clientes
        response = requests.get(f"{API_URL}/clients")
        if response.status_code == 200:
            clientes = response.json()
            
            # Buscar Released
            cliente_released = None
            for cliente in clientes:
                if cliente['name'] == 'Released':
                    cliente_released = cliente
                    break
            
            if cliente_released:
                print("✅ CLIENTE RELEASED ENCONTRADO:")
                print(f"   🆔 ID: {cliente_released['id']}")
                print(f"   📱 Número: {cliente_released['phone_number']}")
                print(f"   🆔 Phone Number ID: {cliente_released['phone_number_id']}")
                print(f"   🤖 Assistant ID: {cliente_released['assistant_id']}")
                print(f"   📊 Activo: {'✅' if cliente_released['active'] else '❌'}")
                print(f"   📝 Mensaje bienvenida: {cliente_released.get('welcome_message', 'No configurado')[:100]}...")
                
                return cliente_released
            else:
                print("❌ Cliente Released no encontrado")
                return None
        else:
            print(f"❌ Error obteniendo clientes: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def mostrar_instrucciones_railway():
    """Mostrar instrucciones detalladas para ver logs en Railway"""
    print("\n📊 CÓMO VER LOGS EN RAILWAY:")
    print("=" * 60)
    print("🌐 1. Ve a https://railway.app/ y haz login")
    print("📁 2. Selecciona tu proyecto 'released-production'")
    print("🔧 3. Haz clic en tu servicio principal")
    print("📋 4. Ve a la pestaña 'Deployments'")
    print("🚀 5. Haz clic en el deployment más reciente (el de arriba)")
    print("📜 6. Haz clic en la pestaña 'Logs'")
    print()
    print("🔍 QUÉ BUSCAR EN LOS LOGS (en tiempo real):")
    print("• 'Received webhook POST' - Confirma que llega la petición")
    print("• 'Processing message from +34...' - Muestra procesamiento del mensaje")
    print("• 'OpenAI API call' - Confirma que se llama a OpenAI")
    print("• 'Sending WhatsApp message' - Confirma que se envía respuesta")
    print("• Cualquier texto en ROJO = Error")
    print()
    print("📱 MIENTRAS VES LOS LOGS:")
    print("• Mantén la pestaña de logs abierta")
    print("• Envía un mensaje de WhatsApp")
    print("• Deberías ver logs aparecer en 1-2 segundos")
    print("• Si NO aparecen logs = el mensaje no llega al servidor")
    print()
    print("🚨 SI NO VES LOGS:")
    print("• El webhook en Meta Business sigue apuntando a ngrok")
    print("• Revisa la configuración del webhook en Meta Business")
    print("• Asegúrate de que la URL sea exactamente:")
    print(f"  {API_URL}/webhook")

def menu_monitor():
    """Menú de monitoreo"""
    while True:
        print("\n🔍 MONITOR DE WEBHOOK WHATSAPP")
        print("=" * 60)
        print("1. 🧪 Enviar mensaje de prueba al webhook")
        print("2. 📊 Ver configuración actual de Released")
        print("3. 📜 Instrucciones para ver logs en Railway")
        print("4. 🔄 Test completo (prueba + verificación)")
        print("5. 🌐 Abrir Railway en navegador")
        print("6. 🚪 Salir")
        
        opcion = input("\nSelecciona una opción (1-6): ").strip()
        
        if opcion == "1":
            test_mensaje_directo()
            
        elif opcion == "2":
            verificar_configuracion_actual()
            
        elif opcion == "3":
            mostrar_instrucciones_railway()
            
        elif opcion == "4":
            print("🔄 EJECUTANDO TEST COMPLETO...")
            print("=" * 60)
            
            # Verificar configuración
            cliente = verificar_configuracion_actual()
            if not cliente:
                print("❌ No se puede continuar sin cliente configurado")
                continue
            
            # Enviar mensaje de prueba
            test_mensaje_directo()
            
            # Mostrar instrucciones
            print("\n" + "="*60)
            mostrar_instrucciones_railway()
            
        elif opcion == "5":
            print("🌐 Abriendo Railway...")
            import webbrowser
            webbrowser.open("https://railway.app/")
            
        elif opcion == "6":
            print("\n👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción no válida")
        
        input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    print("🔍 WEBHOOK LOG MONITOR")
    print("Monitor de logs para detectar mensajes de WhatsApp")
    print("=" * 60)
    menu_monitor()
