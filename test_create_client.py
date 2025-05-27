#!/usr/bin/env python3
"""
Script de prueba para gestionar clientes a través de la API.
Permite listar, crear y borrar clientes.
"""

import requests
import json

# ===== CONFIGURACIÓN - MODIFICA ESTOS VALORES =====

# URL de tu API (cambiar cuando esté en producción)
API_URL = "http://localhost:8082"  # Cambiar a "https://tu-dominio.com" en producción

# Datos del cliente para crear
CLIENTE = {
    "name": "Restaurante Demo",
    "phone_number": "+15556383785",  # Número completo con código de país
    "phone_number_id": "631261586727899",  # ID que te da Meta después de verificar el número
    "welcome_message": "¡Hola! Bienvenido al Restaurante Demo. ¿En qué puedo ayudarte?",
    "business_hours": ""
}

# FAQs del cliente (preguntas y respuestas)
FAQS = [
    {
        "q": "¿Cuál es vuestro horario?",
        "a": "Abrimos de lunes a viernes de 13:00 a 16:00 y de 20:00 a 23:30. Sábados y domingos de 13:00 a 16:30 y de 20:00 a 00:00."
    },
    {
        "q": "¿Hacéis reservas?",
        "a": "Sí, puedes reservar llamando al +34666111222 o a través de nuestra página web."
    },
    {
        "q": "¿Tenéis menú del día?",
        "a": "Sí, nuestro menú del día cuesta 14€ e incluye primer plato, segundo plato, postre o café y bebida. Disponible de lunes a viernes."
    },
    {
        "q": "¿Tenéis opciones vegetarianas?",
        "a": "Por supuesto, tenemos varias opciones vegetarianas y veganas en nuestra carta. También podemos adaptar algunos platos según tus preferencias."
    },
    {
        "q": "¿Dónde estáis ubicados?",
        "a": "Estamos en la Calle Mayor 123, en el centro de la ciudad. Cerca de la plaza principal."
    },
    {
        "q": "¿Tenéis servicio a domicilio?",
        "a": "Sí, realizamos entregas a domicilio en un radio de 5km. Pedido mínimo 20€. También estamos en las principales apps de delivery."
    },
    {
        "q": "¿Aceptáis tarjeta?",
        "a": "Sí, aceptamos pago con tarjeta, efectivo y también Bizum."
    },
    {
        "q": "¿Tenéis terraza?",
        "a": "Sí, tenemos una amplia terraza con capacidad para 30 personas. Está disponible todo el año."
    }
]

# ===== FIN DE CONFIGURACIÓN =====


def listar_clientes():
    """Listar todos los clientes existentes"""
    print("\n📋 Listando clientes existentes...")
    
    try:
        response = requests.get(f"{API_URL}/clients")
        if response.status_code == 200:
            clientes = response.json()
            print(f"\nTotal de clientes: {len(clientes)}")
            print("-" * 80)
            for cliente in clientes:
                estado = "✅ Activo" if cliente['active'] else "❌ Inactivo"
                print(f"ID: {cliente['id']} | {cliente['name']} | {cliente['phone_number']} | {estado}")
            print("-" * 80)
            return clientes
        else:
            print(f"❌ Error al listar clientes: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []


def crear_cliente():
    """Crear un cliente a través de la API"""
    
    # Preparar los datos
    data = {
        "name": CLIENTE["name"],
        "phone_number": CLIENTE["phone_number"],
        "phone_number_id": CLIENTE["phone_number_id"],
        "faqs": FAQS,
        "welcome_message": CLIENTE.get("welcome_message"),
        "business_hours": CLIENTE.get("business_hours")
    }
    
    # Hacer la petición
    url = f"{API_URL}/clients"
    
    print(f"\n🚀 Creando cliente: {CLIENTE['name']}")
    print(f"📞 Teléfono: {CLIENTE['phone_number']}")
    print(f"🆔 Phone Number ID: {CLIENTE['phone_number_id']}")
    print(f"❓ FAQs: {len(FAQS)} preguntas")
    print("-" * 50)
    
    try:
        response = requests.post(
            url,
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            print("✅ ¡Cliente creado exitosamente!")
            print("-" * 50)
            print(f"ID del cliente: {result['id']}")
            print(f"Assistant ID: {result['assistant_id']}")
            print(f"Estado: {'Activo' if result['active'] else 'Inactivo'}")
            print("-" * 50)
            
        else:
            print(f"❌ Error al crear cliente: {response.status_code}")
            print(f"Mensaje: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar con la API")
        print(f"   Verifica que la API esté corriendo en {API_URL}")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")


def borrar_cliente(cliente_id, permanente=False):
    """Borrar un cliente a través de la API"""
    
    url = f"{API_URL}/clients/{cliente_id}"
    if permanente:
        url += "?hard_delete=true"
    
    try:
        response = requests.delete(url)
        
        if response.status_code == 200:
            resultado = response.json()
            print(f"✅ {resultado['message']}")
        elif response.status_code == 404:
            print(f"❌ No se encontró el cliente con ID {cliente_id}")
        else:
            print(f"❌ Error al borrar cliente: {response.status_code}")
            print(f"Mensaje: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar con la API")
        print(f"   Verifica que la API esté corriendo en {API_URL}")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")


def borrar_todos_clientes():
    """Borrar TODOS los clientes permanentemente"""
    
    url = f"{API_URL}/clients?confirm=true"
    
    try:
        response = requests.delete(url)
        
        if response.status_code == 200:
            resultado = response.json()
            print(f"✅ {resultado['message']}")
        else:
            print(f"❌ Error al borrar clientes: {response.status_code}")
            print(f"Mensaje: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar con la API")
        print(f"   Verifica que la API esté corriendo en {API_URL}")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")


def menu_principal():
    """Menú principal del script"""
    while True:
        print("\n" + "=" * 80)
        print("GESTIÓN DE CLIENTES - WHATSAPP BOT")
        print("=" * 80)
        print("\n¿Qué deseas hacer?")
        print("1. Listar clientes")
        print("2. Crear nuevo cliente")
        print("3. Desactivar cliente (soft delete)")
        print("4. Borrar cliente permanentemente")
        print("5. BORRAR TODOS los clientes")
        print("6. Salir")
        
        opcion = input("\nSelecciona una opción (1-6): ").strip()
        
        if opcion == "1":
            listar_clientes()
            
        elif opcion == "2":
            clientes = listar_clientes()
            if clientes:
                print(f"\n¿Deseas crear el cliente '{CLIENTE['name']}'? (s/n): ", end="")
                respuesta = input().strip().lower()
                if respuesta == 's':
                    crear_cliente()
            else:
                crear_cliente()
                
        elif opcion == "3":
            clientes = listar_clientes()
            if clientes:
                print("\n¿Qué cliente deseas DESACTIVAR?")
                cliente_id = input("Ingresa el ID del cliente (o 'c' para cancelar): ").strip()
                
                if cliente_id.lower() != 'c' and cliente_id.isdigit():
                    # Buscar el cliente para confirmar
                    cliente_encontrado = None
                    for c in clientes:
                        if str(c['id']) == cliente_id:
                            cliente_encontrado = c
                            break
                    
                    if cliente_encontrado:
                        print(f"\n⚠️  Estás a punto de DESACTIVAR:")
                        print(f"   ID: {cliente_encontrado['id']}")
                        print(f"   Nombre: {cliente_encontrado['name']}")
                        print(f"   Teléfono: {cliente_encontrado['phone_number']}")
                        
                        confirmacion = input("\n¿Estás seguro? (s/n): ").strip().lower()
                        if confirmacion == 's':
                            borrar_cliente(cliente_id, permanente=False)
                        else:
                            print("❌ Operación cancelada")
                    else:
                        print(f"❌ No se encontró un cliente con ID {cliente_id}")
                else:
                    print("❌ Operación cancelada")
            else:
                print("No hay clientes para desactivar")
                
        elif opcion == "4":
            clientes = listar_clientes()
            if clientes:
                print("\n¿Qué cliente deseas BORRAR PERMANENTEMENTE?")
                cliente_id = input("Ingresa el ID del cliente (o 'c' para cancelar): ").strip()
                
                if cliente_id.lower() != 'c' and cliente_id.isdigit():
                    # Buscar el cliente para confirmar
                    cliente_encontrado = None
                    for c in clientes:
                        if str(c['id']) == cliente_id:
                            cliente_encontrado = c
                            break
                    
                    if cliente_encontrado:
                        print(f"\n🚨 ADVERTENCIA: Esta acción es IRREVERSIBLE 🚨")
                        print(f"   ID: {cliente_encontrado['id']}")
                        print(f"   Nombre: {cliente_encontrado['name']}")
                        print(f"   Teléfono: {cliente_encontrado['phone_number']}")
                        print(f"   Assistant ID: {cliente_encontrado['assistant_id']}")
                        
                        confirmacion = input("\n¿Estás ABSOLUTAMENTE seguro? Escribe 'BORRAR' para confirmar: ").strip()
                        if confirmacion == 'BORRAR':
                            borrar_cliente(cliente_id, permanente=True)
                        else:
                            print("❌ Operación cancelada")
                    else:
                        print(f"❌ No se encontró un cliente con ID {cliente_id}")
                else:
                    print("❌ Operación cancelada")
            else:
                print("No hay clientes para borrar")
                
        elif opcion == "5":
            clientes = listar_clientes()
            if clientes:
                print("\n🚨🚨🚨 ADVERTENCIA CRÍTICA 🚨🚨🚨")
                print(f"Estás a punto de BORRAR PERMANENTEMENTE {len(clientes)} clientes")
                print("Esta acción es COMPLETAMENTE IRREVERSIBLE")
                print("\nClientes que serán eliminados:")
                for c in clientes:
                    print(f"  - {c['name']} (ID: {c['id']})")
                
                confirmacion = input("\n¿Estás ABSOLUTAMENTE seguro? Escribe 'BORRAR TODO' para confirmar: ").strip()
                if confirmacion == 'BORRAR TODO':
                    segunda_confirmacion = input("Segunda confirmación. Escribe 'SI' para proceder: ").strip()
                    if segunda_confirmacion == 'SI':
                        borrar_todos_clientes()
                    else:
                        print("❌ Operación cancelada")
                else:
                    print("❌ Operación cancelada")
            else:
                print("No hay clientes para borrar")
                
        elif opcion == "6":
            print("\n👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción no válida. Por favor selecciona 1-6.")
        
        input("\nPresiona Enter para continuar...")


if __name__ == "__main__":
    menu_principal()


# PHONE_NUMBER_ID="631261586727899"
# OPENAI_ASSISTANT_ID="asst_YBQJCXsLVp2IkB8UaYvgJshL"
# curl -X DELETE "http://localhost:8082/clients?confirm=true"