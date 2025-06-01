#!/usr/bin/env python3
"""
Script para diagnosticar la conexión a la base de datos de Railway
"""
import os
import psycopg2
from urllib.parse import urlparse

def test_connection():
    """Probar diferentes configuraciones de conexión"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ No hay DATABASE_URL configurada")
        return
    
    print(f"🔗 Testing connection to: {database_url[:50]}...")
    
    # Parsear la URL
    parsed = urlparse(database_url)
    
    connection_configs = [
        # Configuración 1: URL directa
        {"url": database_url, "description": "URL directa"},
        
        # Configuración 2: Sin SSL
        {"url": database_url + ("&" if "?" in database_url else "?") + "sslmode=disable", 
         "description": "Sin SSL"},
         
        # Configuración 3: SSL preferido
        {"url": database_url + ("&" if "?" in database_url else "?") + "sslmode=prefer", 
         "description": "SSL preferido"},
         
        # Configuración 4: Parámetros individuales
        {
            "params": {
                "host": parsed.hostname,
                "port": parsed.port,
                "database": parsed.path[1:],  # quitar el '/' inicial
                "user": parsed.username,
                "password": parsed.password,
                "sslmode": "disable"
            },
            "description": "Parámetros individuales"
        }
    ]
    
    for config in connection_configs:
        try:
            print(f"\n🧪 Probando: {config['description']}")
            
            if 'url' in config:
                conn = psycopg2.connect(config['url'])
            else:
                conn = psycopg2.connect(**config['params'])
                
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ Conexión exitosa! PostgreSQL version: {version[0][:50]}...")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}...")
    
    return False

if __name__ == "__main__":
    print("🚀 Iniciando test de conexión a base de datos")
    success = test_connection()
    
    if not success:
        print("\n❌ Todas las configuraciones fallaron")
    else:
        print("\n✅ Al menos una configuración funcionó")
