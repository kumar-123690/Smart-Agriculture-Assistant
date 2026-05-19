import uvicorn
import os
from backend.main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"
    print(f"Starting Uvicorn server on {host}:{port}...")
    uvicorn.run(app, host=host, port=port)
