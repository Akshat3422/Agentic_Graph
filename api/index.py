import os
import sys
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    from main import app  # noqa: F401
except Exception:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    _error = traceback.format_exc()
    app = FastAPI()

    @app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def startup_error(full_path: str = ""):
        missing = [
            key
            for key in (
                "SECRET_KEY",
                "ALGORITHM",
                "ACCESS_TOKEN_EXPIRE_MINUTES",
                "DATABASE_URL",
                "GROQ_API_KEY",
            )
            if not os.getenv(key)
        ]
        return JSONResponse(
            status_code=500,
            content={
                "error": "Application failed to start",
                "missing_env_vars": missing,
                "detail": _error,
            },
        )
