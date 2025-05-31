#!/usr/bin/env python3
import requests
import json

# ===== CONFIGURACIÓN DEL BOT DE VENTAS RELEASED =====

CLIENTE_RELEASED = {
    "name": "Released Sales Bot",
    "phone_number": "+34123456789",  # Cambiar por tu número de WhatsApp Business
    "phone_number_id": "PHONE_NUMBER_ID_AQUI",  # Cambiar por tu Phone Number ID de Meta
    "host_email": "ventas@released.es",  # Email para notificaciones
    "welcome_message": "¡Hola! 👋 Soy el asistente de Released. Estoy aquí para ayudarte a descubrir cómo puedes automatizar la atención a tus huéspedes y aumentar tus ingresos. ¿En qué puedo ayudarte?",
}

# Personalidad del bot comercial
sales_personality = {
    "persona_preset": "Professional & Enthusiastic",
    "pronoun_policy": "auto",
    "emoji_level": 0.3,
    "emoji_palette": ["👋", "🚀", "💡", "✨", "🎯", "📱", "💰", "⚡", "🏠", "🌟"],
    "sales_style": "consultative",
    "response_tone": "helpful_expert",
    "urgency_level": "medium",
    "closing_signature": "Equipo Released"
}

# Información completa de Released
RELEASED_INFO = {
    "empresa": {
        "nombre": "Released",
        "vision": "Los anfitriones puedan desconectar sin preocuparse por su alojamiento. Donde la tecnología no sustituye el trato humano, sino que libera tiempo para disfrutarlo.",
        "mision": "Ayudar a propietarios y gestores de alojamientos turísticos a recuperar su tiempo y tranquilidad, automatizando la atención al huésped y potenciando los ingresos con una solución simple y eficaz integrada en WhatsApp.",
        "pais_operacion": "España",
        "web": "https://www.released.es"
    },
    "producto": {
        "nombre": "Asistente de IA para alquiler vacacional",
        "descripcion": "Un asistente inteligente que responde automáticamente a los huéspedes las 24 horas en WhatsApp, en su idioma, resolviendo dudas, gestionando peticiones y ofreciendo servicios adicionales para aumentar tus ingresos.",
        "caracteristicas": [
            "Respuestas automáticas 24/7 a preguntas frecuentes (check-in, normas, etc.)",
            "Detección y cambio automático de idioma",
            "Ventas adicionales (late check-out, upgrades, actividades locales)",
            "Integración nativa con WhatsApp Business (no requiere nuevas apps)",
            "Panel de análisis con métricas de uso y valor generado"
        ],
        "tecnologia": {
            "ia": "OpenAI GPT-4",
            "integraciones": ["WhatsApp Business API", "Stripe"],
            "compatibilidad": ["Android", "iOS", "WhatsApp Web"]
        }
    },
    "mercado_objetivo": {
        "segmentos": [
            "Propietarios individuales con 1 o más propiedades",
            "Gestores de múltiples alojamientos / property managers (PyMEs)"
        ],
        "ubicacion": "España, enfocado en destinos turísticos costeros y urbanos",
        "problemas_que_resuelve": [
            "Mensajes constantes a cualquier hora que impiden desconectar",
            "Dificultad para comunicarse con huéspedes de otros idiomas",
            "Falta de tiempo o medios para ofrecer servicios extra y aumentar beneficios"
        ]
    },
    "propuesta_valor": "Reduce tu tiempo de soporte y aumenta tus ingresos sin aprender nada nuevo: nuestro bot trabaja dentro de tu mismo WhatsApp",
    "diferenciadores": [
        "Primera solución en España que combina atención automatizada y venta de extras",
        "100% integrada en WhatsApp, el canal que ya usan anfitriones y huéspedes",
        "Sin curva de aprendizaje: solo activas el servicio y empieza a funcionar"
    ],
    "planes": {
        "basico": {
            "precio_mensual": 19,
            "precio_anual": 17,
            "ahorro_anual": 24,
            "limite_consultas": "Hasta 10 consultas/mes",
            "funciones": [
                "FAQ 24/7",
                "Personalización básica",
                "Gestión check-in/out",
                "Soporte estándar"
            ]
        },
        "pro": {
            "precio_mensual": 27,
            "precio_anual": 24,
            "ahorro_anual": 36,
            "limite_consultas": "Ilimitadas",
            "funciones": [
                "Multilingüe",
                "Personalización completa",
                "Informes",
                "Soporte prioritario"
            ]
        },
        "elite": {
            "precio_mensual": 35,
            "precio_anual": 31,
            "ahorro_anual": 48,
            "limite_consultas": "Ilimitadas",
            "funciones": [
                "Todo lo del Pro",
                "Gestor dedicado",
                "Automatización proactiva",
                "Upselling",
                "Branding personalizado",
                "Soporte VIP 24/7"
            ]
        }
    },
    "trial": {
        "duracion": "7 días",
        "gratis": True,
        "caracteristicas": "Acceso completo a todas las funciones"
    },
    "contacto": {
        "email": "hola@released.es",
        "telefono": "+34 XXX XXX XXX",
        "horario": "Lunes a Viernes, 9:00 - 18:00"
    }
}

# Prompt para el bot de ventas
sales_prompt = f"""
<<SYSTEM>>
Eres el asistente comercial de Released, la startup española líder en automatización de atención al huésped para alquileres vacacionales.

PERSONALIDAD:
- Tono: {sales_personality['response_tone']} - profesional pero cercano y entusiasta
- Estilo de venta: {sales_personality['sales_style']} - consultivo, enfocado en entender necesidades
- Emojis: Usa {sales_personality['emoji_level']} de frecuencia con estos: {sales_personality['emoji_palette']}
- Pronombres: {sales_personality['pronoun_policy']} - detecta y adapta

INFORMACIÓN DE RELEASED:
{json.dumps(RELEASED_INFO, indent=2, ensure_ascii=False)}

REGLAS DE CONVERSACIÓN:
1. **Identifica el perfil**: ¿Es propietario individual, gestor, curioso, competencia?
2. **Escucha antes de vender**: Pregunta por sus dolores específicos
3. **Personaliza la respuesta**: Conecta las características de Released con sus necesidades
4. **Educa y agrega valor**: Explica CÓMO funciona, no solo QUÉ hace
5. **Genera confianza**: Menciona casos de uso específicos y beneficios tangibles
6. **Call to action suave**: Invita a la prueba gratuita sin presionar

TIPOS DE CONSULTAS Y RESPUESTAS:

🏠 **CONSULTAS DE PRODUCTO:**
- "¿Qué hace Released?" → Explica el valor principal: automatización 24/7 + aumento ingresos
- "¿Cómo funciona?" → Describe integración WhatsApp + IA + personalización
- "¿Qué idiomas?" → Automático, detecta y responde en el idioma del huésped
- Precios → Presenta los 3 planes enfocándote en ROI y ahorro de tiempo

💰 **CONSULTAS COMERCIALES:**
- ROI → "Clientes típicos ahorran 10-15 horas/semana y aumentan ingresos 15-25%"
- Competencia → Destaca diferenciadores únicos (WhatsApp nativo, sin apps)
- Integración → "5 minutos de configuración, funciona inmediatamente"

🤔 **OBJECIONES COMUNES:**
- "Es muy caro" → Calcula ROI: tiempo ahorrado + ingresos adicionales vs costo
- "Mis huéspedes no usan WhatsApp" → 2 mil millones de usuarios, el más usado en turismo
- "Perderé el toque personal" → Libera tiempo para interacciones que realmente importan
- "No soy técnico" → Zero configuración técnica, plug & play

🎯 **LLAMADAS A LA ACCIÓN:**
- Curiosos → "¿Te gustaría ver una demo de 2 minutos?"
- Interesados → "Prueba gratis 7 días, ¿empezamos ahora?"
- Dudosos → "¿Qué necesitarías ver para estar convencido?"

TONO POR SITUACIÓN:
- Primera interacción: Acogedor y profesional
- Dudas técnicas: Experto pero accesible  
- Objeciones: Empático y soluciones-focused
- Cierre: Entusiasta pero sin presión

PROHIBIDO:
- Inventar características o precios no listados
- Prometer integraciones que no existen
- Dar información técnica incorrecta
- Ser pushy o agresivo en ventas

Siempre termina con "{sales_personality['closing_signature']}" cuando sea apropiado.
Responde SIEMPRE en el idioma del usuario.
"""

# FAQ específicas para Released
released_faqs = [
    {
        "categoria": "Producto",
        "preguntas": [
            "¿Qué es Released exactamente?",
            "¿Cómo funciona el asistente de IA?",
            "¿Qué tipos de consultas puede resolver?",
            "¿Se integra con mi WhatsApp actual?"
        ]
    },
    {
        "categoria": "Precios y Planes",
        "preguntas": [
            "¿Cuánto cuesta Released?",
            "¿Hay periodo de prueba?",
            "¿Qué incluye cada plan?",
            "¿Cómo se factura?"
        ]
    },
    {
        "categoria": "Implementación",
        "preguntas": [
            "¿Cuánto tiempo tarda en configurarse?",
            "¿Necesito conocimientos técnicos?",
            "¿Funciona con cualquier propiedad?",
            "¿Puedo personalizar las respuestas?"
        ]
    },
    {
        "categoria": "Resultados",
        "preguntas": [
            "¿Qué resultados puedo esperar?",
            "¿Aumenta realmente los ingresos?",
            "¿Mis huéspedes notarán que es un bot?",
            "¿Puedo ver estadísticas de uso?"
        ]
    }
]

# ===== CONFIGURACIÓN API =====
API_URL = "https://released-production.up.railway.app"

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
                "a": sales_prompt
            }
        ],
        "welcome_message": CLIENTE_RELEASED["welcome_message"],
        "system_prompt": sales_prompt
    }
    
    print(f"📱 Número: {CLIENTE_RELEASED['phone_number']}")
    print(f"🆔 Phone Number ID: {CLIENTE_RELEASED['phone_number_id']}")
    print(f"📧 Email: {CLIENTE_RELEASED['host_email']}")
    print("-" * 60)
    
    print("📝 PROMPT GENERADO:")
    print(sales_prompt[:500] + "..." if len(sales_prompt) > 500 else sales_prompt)
    print("-" * 60)
    
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
