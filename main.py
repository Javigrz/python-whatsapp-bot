from src.main import app

if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("src.main:app", host="0.0.0.0", port=port, reload=False)