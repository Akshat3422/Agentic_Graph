import os
import sys
import traceback
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Create a fallback app immediately so we can at least return 500s
app = FastAPI()

# Add a basic health check that doesn't depend on the rest of the code
@app.get("/api/health")
def health():
    return {"status": "api_index_is_alive"}

try:
    # Setup paths
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)

    # Try to import the main app
    from main import app as main_app
    app = main_app

except Exception:
    _error = traceback.format_exc()
    
    @app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def catch_all(full_path: str = ""):
        # Check for missing env vars as a likely cause
        missing = [
            key for key in (
                "DATABASE_URL",
                "SECRET_KEY",
                "GROQ_API_KEY",
            ) if not os.getenv(key)
        ]
        return JSONResponse(
            status_code=500,
            content={
                "error": "Application failed to start during import",
                "missing_env_vars": missing,
                "detail": _error,
                "hint": "Ensure all Environment Variables are set in Vercel Project Settings."
            }
        )
