#!/usr/bin/env python3
"""
Script de inicio alternativo para Railway
"""
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        workers=1  # Railway funciona mejor con 1 worker
    )
