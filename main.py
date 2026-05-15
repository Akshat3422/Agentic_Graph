import os
import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
import uuid
from database import Base, engine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _resolve_public_dir() -> str | None:
    # Try multiple common locations for the public directory in Vercel/Local environments
    candidates = [
        os.path.join(BASE_DIR, "public"),
        os.path.join(BASE_DIR, "api", "public"),
        os.path.join(os.getcwd(), "public"),
        os.path.join(os.path.dirname(BASE_DIR), "public"),
        "/var/task/public",
        "/var/task/api/public",
    ]
    for path in candidates:
        if os.path.isdir(path):
            return path
    return None


PUBLIC_DIR = _resolve_public_dir()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print("DB init failed:", e)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health():
    required = (
        "DATABASE_URL",
        "SECRET_KEY",
        "ALGORITHM",
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "GROQ_API_KEY",
        "GMAIL_ID",
        "PASSWORD",
    )
    missing = [key for key in required if not os.getenv(key)]
    public_files = []
    if PUBLIC_DIR:
        try:
            public_files = os.listdir(PUBLIC_DIR)
        except OSError:
            pass
    return {
        "status": "ok" if not missing else "degraded",
        "missing_env_vars": missing,
        "public_dir": PUBLIC_DIR,
        "public_files": public_files,
    }


def _public_file(name: str, media_type: str) -> FileResponse:
    if not PUBLIC_DIR:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Static directory not found",
                "cwd": os.getcwd(),
                "base_dir": BASE_DIR,
                "tried_paths": [
                    os.path.join(BASE_DIR, "public"),
                    os.path.join(os.getcwd(), "public"),
                    "/var/task/public",
                ],
            },
        )
    path = os.path.join(PUBLIC_DIR, name)
    if not os.path.isfile(path):
        raise HTTPException(
            status_code=404,
            detail={
                "error": f"File '{name}' not found",
                "path": path,
                "public_dir": PUBLIC_DIR,
                "contents": os.listdir(PUBLIC_DIR) if os.path.isdir(PUBLIC_DIR) else [],
            },
        )
    return FileResponse(path, media_type=media_type)


@app.get("/")
async def serve_index():
    return _public_file("index.html", "text/html")


@app.get("/app.js")
async def serve_app_js():
    return _public_file("app.js", "application/javascript")


@app.get("/styles.css")
async def serve_styles():
    return _public_file("styles.css", "text/css")


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request.state.request_id = str(uuid.uuid4())
    response = await call_next(request)
    return response


_startup_error = None

try:
    from routes.user import user_router
    from routes.auth_routes import router
    from routes.transactions_routes import transaction_router
    from routes.accounts_routes import account_router

    app.include_router(user_router)
    app.include_router(router)
    app.include_router(account_router)
    app.include_router(transaction_router)

    try:
        from chatbot.graph import router as chatbot_router
        app.include_router(router=chatbot_router)
    except Exception as e:
        print("Chatbot router failed to load:", e)
except Exception as e:
    _startup_error = traceback.format_exc()
    print("API routers failed to load:", e)

    @app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def startup_failure(full_path: str = ""):
        if full_path in ("", "health"):
            return health()
        return JSONResponse(
            status_code=500,
            content={
                "error": "API failed to start",
                "detail": _startup_error,
                "hint": "Check Vercel env vars and redeploy.",
            },
        )
