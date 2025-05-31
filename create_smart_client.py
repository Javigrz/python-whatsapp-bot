#!/usr/bin/env python3
"""
Script para crear clientes inteligentes con personalidades específicas y manejo avanzado de conversaciones.

Uso:
    python create_smart_client.py --type restaurant
    python create_smart_client.py --type hotel
    python create_smart_client.py --type ecommerce
    python create_smart_client.py --type custom --config config.json
"""

import requests
import json
import argparse
import sys
from typing import Dict, List

# Configuración del servidor
BASE_URL = "https://released-production.up.railway.app"

# Plantillas de personalidades para diferentes tipos de negocio
PERSONALITY_TEMPLATES = {
    "restaurant": {
        "name": "Restaurante Demo",
        "phone_number": "+34600000001", 
        "phone_number_id": "PLACEHOLDER_PHONE_ID_1",
        "personality": {
            "role": "asistente virtual del restaurante",
            "tone": "amable, profesional y apetitoso",
            "specialties": [
                "información sobre el menú y precios",
                "reservas y disponibilidad", 
                "recomendaciones gastronómicas",
                "información sobre alérgenos",
                "horarios de apertura"
            ],
            "greeting": "¡Hola! Soy el asistente virtual de {restaurant_name}. ¿En qué puedo ayudarte hoy?",
            "closing": "¡Gracias por contactar con {restaurant_name}! Esperamos verte pronto.",
            "powered_by": True
        },
        "knowledge_base": [
            {
                "q": "¿Cuál es vuestro horario?",
                "a": "Estamos abiertos de lunes a domingo de 13:00 a 16:00 y de 20:00 a 24:00. Los lunes cerramos por descanso."
            },
            {
                "q": "¿Tenéis menú del día?",
                "a": "Sí, nuestro menú del día cuesta 15€ e incluye primer plato, segundo plato, postre y bebida. Cambia cada día con productos frescos de temporada."
            },
            {
                "q": "¿Hacéis reservas?",
                "a": "Por supuesto. Puedes hacer reservas llamando al teléfono del restaurante o a través de nuestra web. Te recomendamos reservar especialmente para cenas y fines de semana."
            },
            {
                "q": "¿Tenéis opciones veganas?",
                "a": "Sí, tenemos varios platos veganos en nuestra carta. También podemos adaptar algunos platos según tus necesidades dietéticas. Solo avísanos al hacer la reserva."
            },
            {
                "q": "¿Dónde estáis ubicados?",
                "a": "Estamos en el centro de la ciudad, en la Calle Mayor 123. Tenemos parking público cerca y estamos bien conectados por transporte público."
            }
        ]
    },
    
    "hotel": {
        "name": "Hotel Demo",
        "phone_number": "+34600000002",
        "phone_number_id": "PLACEHOLDER_PHONE_ID_2", 
        "personality": {
            "role": "concierge virtual del hotel",
            "tone": "elegante, servicial y profesional",
            "specialties": [
                "reservas y disponibilidad",
                "servicios del hotel",
                "información turística local",
                "check-in y check-out",
                "servicios de habitación"
            ],
            "greeting": "¡Bienvenido! Soy el concierge virtual de {hotel_name}. ¿Cómo puedo asistirle hoy?",
            "closing": "Ha sido un placer asistirle. ¡Esperamos que disfrute su estancia en {hotel_name}!",
            "powered_by": True
        },
        "knowledge_base": [
            {
                "q": "¿Qué servicios incluye el hotel?",
                "a": "Ofrecemos WiFi gratuito, desayuno buffet, gimnasio 24h, spa, piscina, parking y servicio de habitaciones. También tenemos restaurante con cocina internacional."
            },
            {
                "q": "¿A qué hora es el check-in y check-out?",
                "a": "El check-in es a partir de las 15:00 y el check-out hasta las 12:00. Ofrecemos servicio de guardaequipajes gratuito si llegáis antes o necesitáis salir más tarde."
            },
            {
                "q": "¿Tenéis parking?",
                "a": "Sí, tenemos parking privado con 50 plazas. El coste es de 15€ por noche. También hay parking público a 2 minutos caminando."
            },
            {
                "q": "¿Qué sitios de interés hay cerca?",
                "a": "Estamos en el centro histórico, a 5 minutos caminando de la catedral y el museo principal. El puerto y las playas están a 10 minutos en coche."
            },
            {
                "q": "¿Admitís mascotas?",
                "a": "Sí, admitimos mascotas pequeñas (hasta 10kg) con un suplemento de 20€ por noche. Es necesario informar en la reserva."
            }
        ]
    },
    
    "ecommerce": {
        "name": "Tienda Online Demo",
        "phone_number": "+34600000003",
        "phone_number_id": "PLACEHOLDER_PHONE_ID_3",
        "personality": {
            "role": "asistente de ventas online",
            "tone": "entusiasta, útil y orientado a la conversión",
            "specialties": [
                "información de productos",
                "estado de pedidos",
                "política de devoluciones",
                "ofertas y descuentos",
                "asesoramiento de compra"
            ],
            "greeting": "¡Hola! Soy tu asistente de compras de {store_name}. ¿Buscas algo en particular hoy?",
            "closing": "¡Gracias por elegir {store_name}! Si necesitas algo más, aquí estaré.",
            "powered_by": True
        },
        "knowledge_base": [
            {
                "q": "¿Cuánto tarda el envío?",
                "a": "Los envíos estándar tardan 24-48h en península. Envío gratuito en pedidos superiores a 50€. También ofrecemos envío express en 24h por 5€ adicionales."
            },
            {
                "q": "¿Cuál es vuestra política de devoluciones?",
                "a": "Tienes 30 días para devolver cualquier producto sin abrir. Los gastos de devolución son gratuitos. Solo necesitas el número de pedido para iniciar el proceso."
            },
            {
                "q": "¿Tenéis alguna oferta especial?",
                "a": "¡Sí! Esta semana tenemos un 20% de descuento en toda la colección de temporada con el código TEMP20. También envío gratuito sin mínimo de compra."
            },
            {
                "q": "¿Cómo puedo rastrear mi pedido?",
                "a": "Te enviaremos un email con el número de seguimiento una vez que se envíe tu pedido. También puedes consultar el estado en tu área de cliente de nuestra web."
            },
            {
                "q": "¿Qué métodos de pago aceptáis?",
                "a": "Aceptamos tarjeta de crédito/débito, PayPal, Bizum y transferencia bancaria. Todos los pagos son 100% seguros con cifrado SSL."
            }
        ]
    }
}

def create_instructions(config: Dict) -> str:
    """Crea las instrucciones para el assistant basadas en la configuración"""
    personality = config["personality"]
    knowledge = config["knowledge_base"]
    
    instructions = f"""Eres un {personality['role']} con un tono {personality['tone']}.

ESPECIALIDADES:
{chr(10).join(f"- {spec}" for spec in personality['specialties'])}

SALUDO INICIAL: {personality['greeting']}

BASE DE CONOCIMIENTO:
{chr(10).join(f"P: {item['q']}{chr(10)}R: {item['a']}{chr(10)}" for item in knowledge)}

REGLAS DE CONVERSACIÓN:
1. Mantén siempre un tono {personality['tone']}.
2. Si te preguntan algo que no está en tu base de conocimiento, indica amablemente que consultarás la información y responderás lo antes posible.
3. Si detectas que el cliente quiere hacer una reserva/pedido, proporciona información de contacto directo.
4. Usa emojis ocasionalmente para hacer la conversación más amigable.
5. Personaliza las respuestas usando el nombre del negocio cuando sea apropiado.
6. Si la conversación se alarga, ofrece ayuda adicional o contacto directo.
"""

    if personality.get("powered_by"):
        instructions += "\n7. Al final de conversaciones largas, puedes mencionar discretamente 'Powered by Released'."
    
    instructions += f"\n\nCIERRE: {personality['closing']}"
    
    return instructions

def create_client(config: Dict) -> Dict:
    """Crea un cliente usando la API"""
    
    # Preparar datos para la API
    client_data = {
        "name": config["name"],
        "phone_number": config["phone_number"],
        "phone_number_id": config["phone_number_id"],
        "instructions": create_instructions(config),
        "welcome_message": config["personality"]["greeting"].format(
            restaurant_name=config["name"],
            hotel_name=config["name"], 
            store_name=config["name"]
        )
    }
    
    print(f"🚀 Creando cliente: {config['name']}")
    print(f"📱 Teléfono: {config['phone_number']}")
    print(f"🤖 Personalidad: {config['personality']['role']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/clients",
            json=client_data,
            timeout=30
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Cliente creado exitosamente!")
            print(f"   ID: {result.get('id')}")
            print(f"   Assistant ID: {result.get('assistant_id')}")
            return result
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {str(e)}")
        return None

def load_custom_config(file_path: str) -> Dict:
    """Carga configuración personalizada desde archivo JSON"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error en JSON: {str(e)}")
        sys.exit(1)

def update_phone_config(config: Dict, phone_number: str, phone_id: str) -> Dict:
    """Actualiza la configuración con números de teléfono reales"""
    config["phone_number"] = phone_number
    config["phone_number_id"] = phone_id
    return config

def main():
    parser = argparse.ArgumentParser(description="Crear cliente inteligente de WhatsApp")
    parser.add_argument("--type", choices=["restaurant", "hotel", "ecommerce", "custom"], 
                       required=True, help="Tipo de negocio")
    parser.add_argument("--config", help="Archivo JSON para configuración personalizada")
    parser.add_argument("--phone", help="Número de teléfono real (+34600123456)")
    parser.add_argument("--phone-id", help="Phone Number ID de Meta")
    parser.add_argument("--name", help="Nombre personalizado del negocio")
    
    args = parser.parse_args()
    
    # Cargar configuración
    if args.type == "custom":
        if not args.config:
            print("❌ Se requiere --config para tipo 'custom'")
            sys.exit(1)
        config = load_custom_config(args.config)
    else:
        config = PERSONALITY_TEMPLATES[args.type].copy()
    
    # Actualizar con parámetros de línea de comandos
    if args.phone and args.phone_id:
        config = update_phone_config(config, args.phone, args.phone_id)
    elif args.phone or args.phone_id:
        print("❌ Se requieren ambos --phone y --phone-id si especificas uno")
        sys.exit(1)
    
    if args.name:
        config["name"] = args.name
    
    # Verificar que no se usen placeholders
    if "PLACEHOLDER" in config["phone_number_id"]:
        print("⚠️  IMPORTANTE: Usando Phone Number ID de placeholder")
        print("   Asegúrate de actualizar con valores reales de Meta Business")
        print("   Usa: --phone +34600123456 --phone-id 1234567890")
        
        confirm = input("¿Continuar con valores placeholder? (y/N): ")
        if confirm.lower() != 'y':
            sys.exit(0)
    
    # Crear cliente
    result = create_client(config)
    
    if result:
        print("\n🎉 ¡Cliente creado exitosamente!")
        print("\n📋 Próximos pasos:")
        print("1. Configura el webhook en Meta Business apuntando a:")
        print(f"   {BASE_URL}/webhook")
        print("2. Envía un mensaje de prueba al número de WhatsApp")
        print("3. El bot responderá automáticamente usando la personalidad configurada")
        
        if "PLACEHOLDER" in config["phone_number_id"]:
            print("\n⚠️  IMPORTANTE: Actualiza los placeholders con valores reales de Meta")

def create_example_config():
    """Crea un archivo de ejemplo de configuración personalizada"""
    example = {
        "name": "Mi Negocio Personalizado",
        "phone_number": "+34600000000",
        "phone_number_id": "TU_PHONE_NUMBER_ID_AQUI",
        "personality": {
            "role": "asistente virtual especializado",
            "tone": "profesional y cercano",
            "specialties": [
                "información sobre productos/servicios",
                "atención al cliente",
                "resolución de dudas"
            ],
            "greeting": "¡Hola! Soy el asistente de {business_name}. ¿En qué puedo ayudarte?",
            "closing": "Gracias por contactar con nosotros. ¡Que tengas un excelente día!",
            "powered_by": True
        },
        "knowledge_base": [
            {
                "q": "¿Qué servicios ofrecéis?",
                "a": "Ofrecemos servicios personalizados de alta calidad adaptados a las necesidades de cada cliente."
            },
            {
                "q": "¿Cuáles son vuestros horarios?",
                "a": "Estamos disponibles de lunes a viernes de 9:00 a 18:00. Fuera de este horario puedes dejarnos un mensaje."
            }
        ]
    }
    
    with open("config_example.json", "w", encoding="utf-8") as f:
        json.dump(example, f, indent=2, ensure_ascii=False)
    
    print("📄 Archivo config_example.json creado como plantilla")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("🤖 Creador de Clientes Inteligentes de WhatsApp")
        print("\nEjemplos de uso:")
        print("  python create_smart_client.py --type restaurant --name 'Restaurante Pepe' --phone +34600123456 --phone-id 1234567890")
        print("  python create_smart_client.py --type hotel")
        print("  python create_smart_client.py --type ecommerce")
        print("  python create_smart_client.py --type custom --config mi_config.json")
        print("\nPara crear un archivo de configuración de ejemplo:")
        print("  python -c \"from create_smart_client import create_example_config; create_example_config()\"")
        sys.exit(0)
    
    main()
