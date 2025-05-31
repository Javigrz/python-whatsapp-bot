#!/usr/bin/env python3
"""
Railway Boot Script - DIAGNÓSTICO COMPLETO
"""
import os
import sys

print("--- DIAGNOSTIC BOOT.PY ---")
print(f"Python executable: {sys.executable}")
print(f"Current working directory: {os.getcwd()}")
print("Listing current directory contents:")

try:
    # Intentar cambiar al directorio /app si no estamos ya allí
    if os.getcwd() != '/app':
        print(f"Changing from {os.getcwd()} to /app...")
        os.chdir("/app")
        print("✅ Changed to /app directory.")
    
    # Listar contenido del directorio actual
    current_dir = os.getcwd()
    print(f"Current directory after change: {current_dir}")
    
    dir_contents = os.listdir(".")
    print(f"Directory contents ({len(dir_contents)} items):")
    for item in sorted(dir_contents):
        item_path = os.path.join(".", item)
        if os.path.isfile(item_path):
            size = os.path.getsize(item_path)
            print(f"  FILE: {item} ({size} bytes)")
        elif os.path.isdir(item_path):
            print(f"  DIR:  {item}/")
        else:
            print(f"  ???:  {item}")
    
    # Verificar específicamente boot.py
    if 'boot.py' in dir_contents:
        print("✅ boot.py IS PRESENT in current directory")
        boot_path = os.path.join(".", "boot.py")
        boot_size = os.path.getsize(boot_path)
        print(f"   boot.py size: {boot_size} bytes")
        print(f"   boot.py is readable: {os.access(boot_path, os.R_OK)}")
        print(f"   boot.py is executable: {os.access(boot_path, os.X_OK)}")
    else:
        print("❌ boot.py IS MISSING in current directory")
        print("   This explains why Railway can't find it!")
    
    # Verificar otros archivos importantes
    important_files = ['requirements.txt', 'Dockerfile', 'Procfile', 'main.py', 'src/main.py']
    print("\nChecking for other important files:")
    for file in important_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file}")

except Exception as e:
    print(f"❌ Error during diagnostic: {e}")
    import traceback
    traceback.print_exc()

print("--- END DIAGNOSTIC BOOT.PY ---")

# Salir después del diagnóstico
print("Exiting diagnostic script...")
sys.exit(0)
