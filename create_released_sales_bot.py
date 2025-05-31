#!/usr/bin/env python3
import requests
import json

PROMPT = """
[SISTEMA]
Eres Released, el asistente comercial oficial de Released (SaaS español para anfitriones y gestores de alquiler vacacional). Tu cometido es doble:
	1.	Vender con rigor el servicio “Asistente IA para alquiler vacacional”.
	2.	Resolver con precisión cualquier duda (técnica, operativa, precios) sin sobre-prometer ni inventar. Cuando desconozcas algo, decláralo y ofrece escalar al equipo humano.

1. Datos clave
	•	Nombre/Marca: released
	•	Visión: los anfitriones desconectan sin preocuparse; la tecnología libera tiempo, no sustituye el trato humano.
	•	Misión: recuperar tiempo y aumentar ingresos automatizando la atención al huésped dentro de WhatsApp.

2. Descripción del producto
	•	Responde 24/7 en WhatsApp Business API (+30 idiomas).
	•	Gestiona check-in/out, normas, incidencias leves.
	•	Detecta y ofrece upselling (late check-out, traslados, actividades).
	•	Panel web con métricas (consultas resueltas, ingresos extra, CSAT).
	•	Stack: backend propio + OpenAI LLM; integraciones WhatsApp API y Stripe; hosting UE/GDPR.

3. Planes y precios (IVA no incl.)

Plan	Mensual	Anual	Límite consultas	Extras clave
Básico	19 €	17 €/mes	10 / mes	FAQ 24/7, personalización básica
Pro	27 €	24 €/mes	Ilimitadas	Multilingüe, informes, prioridad
Élite	40 €	 €/mes	Ilimitadas	Todo Pro + gestor dedicado, upselling avanzado, branding, soporte VIP 24/7

	•	Prueba gratuita: 7 días (cancelable sin coste).
	•	Pago: tarjeta vía Stripe.

4. Proceso de configuración (≤ 24 h)
	1.	Pago seguro vía Stripe (elige plan o prueba gratuita).
	2.	Formulario de onboarding en nuestra web: cargas tus FAQ (horarios, normas, extras); tarda ≈ 10 min.
	3.	Alta automática: nuestro sistema entrena tu agente con esos datos.
	4.	En < 24 h recibes por email y SMS el número de WhatsApp de tu agente IA listo para usar.
	5.	Puedes escribirle de inmediato y, si lo deseas, integrar el widget en tus anuncios/plataformas.

5. Pilares conversacionales
	1.	Diagnostica → pregunta nº propiedades, idiomas, objetivo (ahorro tiempo, ingresos).
	2.	Alinea dolor-beneficio → relaciona funciones del plan con su problema.
	3.	Gestiona objeciones → datos verificables (precisión 90 % Q4-2024, GDPR…).
	4.	Cierre → ofrece acción concreta: demo, prueba gratuita, o “Activa ya y en < 24 h tendrás tu número”.
	5.	Escalado → si excede alcance, deriva a equipo técnico/compliance < 24 h.

6. Políticas y límites
	•	Sin asesoría legal/fiscal/médica; no pidas datos sensibles.
	•	Cumple GDPR y normas WhatsApp Business.
	•	Presentación como IA solo una vez; tono humano-profesional, directo, 1 emoji ocasional.

7. Estilo y longitud
	•	Idioma: responde en la lengua del usuario.
	•	Brevedad adaptativa: ≤ 120 palabras en dudas simples; ≤ 300 en explicaciones profundas.
	•	Tono: claro, empático, sin hype vacío; fundamenta con métricas.

8. Ejemplo de flujo

Cliente: «Tengo 3 apartamentos en Benidorm y pierdo horas al móvil. ¿Cómo me ayudáis?»
Agente:
	1.	«¿En qué horarios recibes más mensajes y en qué idiomas te escriben?»
	2.	«Con el plan Pro cubrimos todas tus consultas 24/7, traducimos +30 idiomas y verás los € extra por upselling. Nuestros clientes con 3-5 unidades ahorran ~18 h/mes y ganan +12 % de ingresos.»
	3.	«Ejemplo: anfitrión en Alicante con 2 pisos facturó +220 €/mes por late check-outs.»
	4.	«Puedes activar la prueba gratuita ahora y en menos de 24 h tendrás tu número de WhatsApp listo. ¿Te gustaría probarlo?»

SI ALGUNA DUDA NO PUEDES RESPONDER, DILE AL USUARIO QUE ESCALARÁS SU CONSULTA AL EQUIPO HUMANO Y QUE LE RESPONDERÁN EN MENOS DE 24 HORAS.
[SISTEMA]
"""

# ===== CONFIGURACIÓN API =====
API_URL = "https://released-production.up.railway.app"

# ===== CONFIGURACIÓN BOT RELEASED =====
CLIENTE_RELEASED = {
    "name": "Released",
    "phone_number": "+15556383785",  # 🔄 ACTUALIZAR con tu número real de WhatsApp Business
    "phone_number_id": "631261586727899",  # 🔄 ACTUALIZAR con tu Phone Number ID de Meta
    "host_email": "javier.gil@released.es",  # 🔄 ACTUALIZAR con tu email real
    "welcome_message": "¡Hola! 👋 Soy el asistente comercial de Released. Ayudo a propietarios de alquileres vacacionales a automatizar la atención a huéspedes y aumentar sus ingresos. ¿Te gustaría saber cómo podemos ayudarte?"
}

def crear_bot_ventas_released():
    """Crear el bot de ventas de Released"""
    
    print("🚀 CREANDO BOT DE VENTAS RELEASED")
    print("=" * 60)
    
    # Preparar datos para el API
    data = {
        "name": CLIENTE_RELEASED["name"],
        "phone_number": CLIENTE_RELEASED["phone_number"],
        "phone_number_id": CLIENTE_RELEASED["phone_number_id"],
        "host_email": CLIENTE_RELEASED["host_email"],
        "faqs": [
            {
                "q": "Información de Released",
                "a": ""
            }
        ],
        "welcome_message": CLIENTE_RELEASED["welcome_message"],
        "system_prompt": PROMPT
    }
    
    print(f"📱 Número: {CLIENTE_RELEASED['phone_number']}")
    print(f"🆔 Phone Number ID: {CLIENTE_RELEASED['phone_number_id']}")
    print(f"📧 Email: {CLIENTE_RELEASED['host_email']}")
    print("-" * 60)
    
    print("📝 PROMPT GENERADO:")
    # print(sales_prompt[:500] + "..." if len(sales_prompt) > 500 else sales_prompt)
    # print("-" * 60)
    
    try:
        response = requests.post(
            f"{API_URL}/clients",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print("✅ ¡BOT DE VENTAS CREADO EXITOSAMENTE!")
            print("-" * 60)
            print(f"🆔 ID del cliente: {result['id']}")
            print(f"🤖 Assistant ID: {result['assistant_id']}")
            print(f"📊 Estado: {'✅ Activo' if result['active'] else '❌ Inactivo'}")
            print("-" * 60)
            print("🎯 PRÓXIMOS PASOS:")
            print("1. Configura el webhook en Meta Business:")
            print(f"   URL: {API_URL}/webhook")
            print("   Verify Token: 13")
            print("2. Prueba enviando un mensaje a tu número de WhatsApp")
            print("3. El bot responderá como asistente comercial de Released")
            print("-" * 60)
            
            return result
        else:
            print(f"❌ Error al crear el bot: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar con la API")
        print(f"   Verifica que la API esté corriendo en {API_URL}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return None

def mostrar_ejemplos_conversacion():
    """Mostrar ejemplos de cómo interactuará el bot"""
    print("\n💬 EJEMPLOS DE CONVERSACIONES:")
    print("=" * 60)
    
    ejemplos = [
        {
            "usuario": "Hola, ¿qué es Released?",
            "bot": "¡Hola! 👋 Released es una solución de IA que automatiza la atención a huéspedes en WhatsApp 24/7. Ayudamos a propietarios de alquileres vacacionales a ahorrar tiempo y aumentar ingresos. ¿Tienes propiedades en alquiler?"
        },
        {
            "usuario": "Sí, tengo 3 apartamentos en la costa. ¿Cómo me puede ayudar?",
            "bot": "¡Perfecto! 🏠 Con 3 apartamentos seguro recibes muchas consultas repetitivas sobre check-in, Wi-Fi, normas... Released se hace cargo automáticamente y además ofrece servicios extras a tus huéspedes (late checkout, limpieza, actividades). ¿Cuántas horas dedicas ahora a responder mensajes?"
        },
        {
            "usuario": "¿Cuánto cuesta?",
            "bot": "Tenemos 3 planes desde 19€/mes 💰. Pero antes, ¿cuánto tiempo ahorrarías si no tuvieras que responder las mismas preguntas? Con el Plan Pro (27€/mes) recuperas la inversión solo con 1-2 servicios extra vendidos. ¿Te gustaría probarlo gratis 7 días? ✨"
        }
    ]
    
    for i, ejemplo in enumerate(ejemplos, 1):
        print(f"\n{i}. Usuario: {ejemplo['usuario']}")
        print(f"   Bot: {ejemplo['bot']}")
    
    print("\n" + "=" * 60)

def mostrar_configuracion():
    """Mostrar la configuración necesaria"""
    print("\n⚙️ CONFIGURACIÓN NECESARIA:")
    print("=" * 60)
    print("ANTES DE CREAR EL BOT, ACTUALIZA:")
    print(f"📱 phone_number: {CLIENTE_RELEASED['phone_number']} → Tu número real")
    print(f"🆔 phone_number_id: {CLIENTE_RELEASED['phone_number_id']} → Tu Phone Number ID de Meta")
    print(f"📧 host_email: {CLIENTE_RELEASED['host_email']} → Tu email real")
    print("\n📋 CONFIGURACIÓN EN META BUSINESS:")
    print("1. Ve a https://business.facebook.com/")
    print("2. Configura WhatsApp Business API")
    print("3. Obtén tu Phone Number ID")
    print("4. Configura webhook:")
    print(f"   - URL: {API_URL}/webhook")
    print("   - Verify Token: 13")
    print("   - Eventos: messages, message_deliveries")

def menu_principal():
    """Menú principal del script"""
    while True:
        print("\n🚀 RELEASED - CREADOR DE BOT DE VENTAS")
        print("=" * 60)
        print("1. 📋 Mostrar configuración necesaria")
        print("2. 💬 Ver ejemplos de conversaciones")
        print("3. 🤖 Crear bot de ventas Released")
        print("4. 📊 Listar clientes existentes")
        print("5. 🚪 Salir")
        
        opcion = input("\nSelecciona una opción (1-5): ").strip()
        
        if opcion == "1":
            mostrar_configuracion()
            
        elif opcion == "2":
            mostrar_ejemplos_conversacion()
            
        elif opcion == "3":
            print("\n⚠️ ¿Has actualizado phone_number y phone_number_id? (s/n): ", end="")
            confirmacion = input().strip().lower()
            if confirmacion == 's':
                crear_bot_ventas_released()
            else:
                print("❌ Actualiza primero la configuración en la sección CLIENTE_RELEASED")
                
        elif opcion == "4":
            try:
                response = requests.get(f"{API_URL}/clients")
                if response.status_code == 200:
                    clientes = response.json()
                    print(f"\n📋 Total de clientes: {len(clientes)}")
                    print("-" * 60)
                    for cliente in clientes:
                        estado = "✅ Activo" if cliente['active'] else "❌ Inactivo"
                        print(f"🆔 {cliente['id']} | {cliente['name']} | {cliente['phone_number']} | {estado}")
                else:
                    print(f"❌ Error al listar: {response.status_code}")
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                
        elif opcion == "5":
            print("\n👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción no válida")
        
        input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    print("🎯 RELEASED SALES BOT CREATOR")
    print("Creador de asistente comercial para Released")
    print("=" * 60)
    menu_principal()
