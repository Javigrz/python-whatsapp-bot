#!/usr/bin/env python3
"""
Script para diagnosticar problemas con el webhook de WhatsApp
"""
import requests
import json
from datetime import datetime
import time

API_URL = "https://released-production.up.railway.app"

def verificar_api():
    """Verificar que la API esté funcionando"""
    print("🔍 VERIFICANDO API...")
    print("=" * 60)
    
    try:
        # Health check
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ API funcionando correctamente")
            print(f"   Status: {data['status']}")
            print(f"   Database: {data['database']}")
            print(f"   Webhook: {data['apis']['webhook']}")
        else:
            print(f"❌ API no responde correctamente: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando con API: {e}")
        return False
    
    return True

def verificar_webhook():
    """Verificar el endpoint del webhook"""
    print("\n🔍 VERIFICANDO WEBHOOK...")
    print("=" * 60)
    
    try:
        # Verificar webhook verification
        response = requests.get(f"{API_URL}/webhook?hub.mode=subscribe&hub.challenge=test123&hub.verify_token=13")
        if response.status_code == 200 and response.text == "test123":
            print("✅ Webhook verification funcionando")
        else:
            print(f"❌ Webhook verification fallando: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando webhook: {e}")
        return False
    
    return True

def verificar_clientes():
    """Verificar que el cliente de Released esté configurado"""
    print("\n🔍 VERIFICANDO CLIENTES...")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_URL}/clients")
        if response.status_code == 200:
            clientes = response.json()
            print(f"📊 Total clientes: {len(clientes)}")
            
            # Buscar el cliente de Released
            cliente_released = None
            for cliente in clientes:
                if cliente['name'] == 'Released':
                    cliente_released = cliente
                    break
            
            if cliente_released:
                print("✅ Cliente Released encontrado:")
                print(f"   ID: {cliente_released['id']}")
                print(f"   Número: {cliente_released['phone_number']}")
                print(f"   Phone Number ID: {cliente_released['phone_number_id']}")
                print(f"   Assistant ID: {cliente_released['assistant_id']}")
                print(f"   Activo: {'✅' if cliente_released['active'] else '❌'}")
                return cliente_released
            else:
                print("❌ Cliente Released no encontrado")
                return None
        else:
            print(f"❌ Error listando clientes: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error verificando clientes: {e}")
        return None

def simular_mensaje():
    """Simular un mensaje de WhatsApp"""
    print("\n🔍 SIMULANDO MENSAJE DE WHATSAPP...")
    print("=" * 60)
    
    # Mensaje de prueba
    test_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "test_entry",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "+15556383785",
                                "phone_number_id": "631261586727899"
                            },
                            "messages": [
                                {
                                    "from": "34612345678",
                                    "id": f"test_message_{int(datetime.now().timestamp())}",
                                    "timestamp": str(int(datetime.now().timestamp())),
                                    "text": {
                                        "body": "Hola, ¿qué es Released?"
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
    
    try:
        response = requests.post(
            f"{API_URL}/webhook",
            json=test_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📤 Mensaje enviado al webhook")
        print(f"📥 Respuesta: {response.status_code}")
        print(f"📄 Contenido: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook procesó el mensaje correctamente")
            return True
        else:
            print("❌ Webhook no procesó el mensaje correctamente")
            return False
            
    except Exception as e:
        print(f"❌ Error simulando mensaje: {e}")
        return False

def mostrar_configuracion_meta():
    """Mostrar la configuración necesaria para Meta Business"""
    print("\n⚙️ CONFIGURACIÓN META BUSINESS:")
    print("=" * 60)
    print("🔧 PASOS PARA ACTUALIZAR WEBHOOK:")
    print()
    print("1. Ve a https://developers.facebook.com/apps/")
    print("2. Selecciona tu app de WhatsApp Business")
    print("3. Ve a WhatsApp > Configuration")
    print("4. En la sección 'Webhook', haz clic en 'Edit'")
    print("5. Actualiza la URL del webhook:")
    print(f"   🔗 Nueva URL: {API_URL}/webhook")
    print("   🔑 Verify Token: 13")
    print("6. Suscríbete a estos eventos:")
    print("   ✅ messages")
    print("   ✅ message_deliveries")
    print("   ✅ message_status")
    print()
    print("🚨 IMPORTANTE:")
    print("   - Asegúrate de ELIMINAR cualquier webhook de ngrok anterior")
    print("   - Solo debe haber UN webhook activo")
    print("   - El verify token debe ser exactamente '13'")

def menu_diagnostico():
    """Menú principal de diagnóstico"""
    while True:
        print("\n🩺 DIAGNÓSTICO WEBHOOK WHATSAPP")
        print("=" * 60)
        print("1. 🔍 Verificar API completa")
        print("2. 📱 Simular mensaje de WhatsApp")
        print("3. 👥 Ver clientes configurados")
        print("4. ⚙️ Mostrar configuración Meta Business")
        print("5. 🔧 Ejecutar diagnóstico completo")
        print("6. 📊 Ver instrucciones para logs Railway")
        print("7. 🧪 Test webhook completo")
        print("8. 🔴 Monitorear mensajes en tiempo real")
        print("9. 🚪 Salir")
        
        opcion = input("\nSelecciona una opción (1-9): ").strip()
        
        if opcion == "1":
            verificar_api()
            verificar_webhook()
            
        elif opcion == "2":
            simular_mensaje()
            
        elif opcion == "3":
            verificar_clientes()
            
        elif opcion == "4":
            mostrar_configuracion_meta()
            
        elif opcion == "5":
            print("🩺 EJECUTANDO DIAGNÓSTICO COMPLETO...")
            print("=" * 60)
            
            # Verificar todo paso a paso
            if not verificar_api():
                print("\n❌ PROBLEMA: API no funciona")
                break
                
            if not verificar_webhook():
                print("\n❌ PROBLEMA: Webhook no funciona")
                break
                
            cliente = verificar_clientes()
            if not cliente:
                print("\n❌ PROBLEMA: Cliente Released no configurado")
                break
                
            if not simular_mensaje():
                print("\n❌ PROBLEMA: Webhook no procesa mensajes")
                break
                
            print("\n✅ DIAGNÓSTICO COMPLETO: Todo funciona correctamente")
            print("🔧 Si aún no recibes mensajes, verifica la configuración en Meta Business")
            mostrar_configuracion_meta()
            
        elif opcion == "6":
            verificar_logs_railway()
            
        elif opcion == "7":
            test_webhook_completo()
            
        elif opcion == "8":
            monitorear_mensajes()
            
        elif opcion == "9":
            print("\n👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción no válida")
        
        input("\nPresiona Enter para continuar...")

def monitorear_mensajes():
    """Monitorear mensajes en tiempo real"""
    print("\n🔍 MONITOREANDO MENSAJES EN TIEMPO REAL...")
    print("=" * 60)
    print("📺 Presiona Ctrl+C para parar el monitoreo")
    print("💬 Envía un mensaje de WhatsApp ahora para verificar...")
    print("-" * 60)
    
    # Crear un endpoint de prueba para ver si llegan requests
    contador = 0
    try:
        while True:
            contador += 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Hacer una petición cada 2 segundos para verificar si hay actividad
            try:
                response = requests.get(f"{API_URL}/health", timeout=5)
                if response.status_code == 200:
                    print(f"[{timestamp}] 🟢 API activa (check #{contador})")
                else:
                    print(f"[{timestamp}] 🔴 API problema: {response.status_code}")
            except Exception as e:
                print(f"[{timestamp}] ❌ Error: {str(e)}")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoreo detenido")
        return

def verificar_logs_railway():
    """Instrucciones para verificar logs en Railway"""
    print("\n📊 VERIFICAR LOGS EN RAILWAY:")
    print("=" * 60)
    print("🔧 PASOS PARA VER LOS LOGS:")
    print()
    print("1. Ve a https://railway.app/")
    print("2. Entra a tu proyecto 'released-production'")
    print("3. Haz clic en tu servicio (backend/API)")
    print("4. Ve a la pestaña 'Deployments'")
    print("5. Haz clic en el deployment activo")
    print("6. Ve a la pestaña 'Logs'")
    print()
    print("🔍 QUÉ BUSCAR EN LOS LOGS:")
    print("• 'Received webhook message' - Confirma que llegan mensajes")
    print("• 'Processing message from' - Muestra el procesamiento")
    print("• 'OpenAI response' - Muestra respuestas de IA")
    print("• Errores en rojo")
    print()
    print("📱 MIENTRAS VES LOS LOGS:")
    print("• Envía un mensaje de WhatsApp")
    print("• Deberías ver logs aparecer inmediatamente")
    print("• Si no aparecen logs = mensajes no llegan")

def test_webhook_completo():
    """Test completo del webhook con payload real"""
    print("\n🧪 TEST WEBHOOK COMPLETO...")
    print("=" * 60)
    
    # Mensaje de prueba más realista
    test_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
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
                                        "name": "Usuario Test"
                                    },
                                    "wa_id": "34612345678"
                                }
                            ],
                            "messages": [
                                {
                                    "from": "34612345678",
                                    "id": f"wamid.test_{int(datetime.now().timestamp())}",
                                    "timestamp": str(int(datetime.now().timestamp())),
                                    "text": {
                                        "body": "Hola, tengo 3 apartamentos y necesito ayuda"
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
    
    print("📤 Enviando mensaje de prueba al webhook...")
    print(f"📱 Simulando mensaje: '{test_payload['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']}'")
    
    try:
        response = requests.post(
            f"{API_URL}/webhook",
            json=test_payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "WhatsApp/2.0"
            }
        )
        
        print(f"📥 Respuesta HTTP: {response.status_code}")
        print(f"📄 Contenido: {response.text}")
        print(f"⏱️  Tiempo respuesta: {response.elapsed.total_seconds():.2f}s")
        
        if response.status_code == 200:
            print("✅ Webhook procesó el mensaje correctamente")
            print("💡 Si esto funciona pero WhatsApp real no, el problema está en Meta Business")
        else:
            print("❌ Webhook tiene problemas procesando el mensaje")
            
    except Exception as e:
        print(f"❌ Error enviando al webhook: {e}")

if __name__ == "__main__":
    print("🩺 WEBHOOK DIAGNOSTIC TOOL")
    print("Herramienta para diagnosticar problemas con WhatsApp webhook")
    print("=" * 60)
    menu_diagnostico()
