import os
import sys

# Add root to path so we can import main.py and other modules
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Basic health check to verify the entry point is reachable
from fastapi import FastAPI
app = FastAPI()

@app.get("/api/ping")
def ping():
    return {"status": "pong", "root": ROOT}

# Import the actual app
try:
    from main import app as main_app
    app = main_app
except Exception as e:
    import traceback
    _error = traceback.format_exc()
    @app.get("/{full_path:path}")
    async def error(full_path: str):
        return {"error": "failed to import main", "detail": _error}
