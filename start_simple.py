#!/usr/bin/env python3
"""
Script de inicio simple para Railway - Sin dependencias extras
"""
import os
import sys

def main():
    try:
        # Obtener puerto
        port = int(os.getenv("PORT", "8000"))
        print(f"[INFO] Puerto configurado: {port}")
        
        # Importar uvicorn - esto debe estar en requirements.txt
        import uvicorn
        print("[INFO] uvicorn importado correctamente")
        
        # Intentar importar la aplicación principal, si falla usar la mínima
        try:
            print("[INFO] Intentando importar aplicación principal...")
            from src.main import app
            print("[INFO] Aplicación principal importada correctamente")
        except Exception as e:
            print(f"[WARNING] Error con aplicación principal: {e}")
            print("[INFO] Usando aplicación mínima...")
            from src.main_minimal import app
            print("[INFO] Aplicación mínima importada correctamente")
        
        # Iniciar servidor
        print(f"[INFO] Iniciando servidor en 0.0.0.0:{port}")
        uvicorn.run(
            app,  # Usar la instancia directamente
            host="0.0.0.0",
            port=port,
            reload=False,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"[ERROR] Falta una dependencia: {e}")
        print("[ERROR] Verifica que requirements.txt esté correcto")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Error crítico: {e}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
