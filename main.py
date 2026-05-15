import os
import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
import uuid
from database import Base, engine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")


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
    return {
        "status": "ok" if not missing else "degraded",
        "missing_env_vars": missing,
    }



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

    if os.path.isdir(PUBLIC_DIR):

        @app.get("/")
        async def serve_index():
            return FileResponse(os.path.join(PUBLIC_DIR, "index.html"))

        @app.get("/app.js")
        async def serve_app_js():
            return FileResponse(
                os.path.join(PUBLIC_DIR, "app.js"),
                media_type="application/javascript",
            )

        @app.get("/styles.css")
        async def serve_styles():
            return FileResponse(
                os.path.join(PUBLIC_DIR, "styles.css"),
                media_type="text/css",
            )

except Exception as e:
    _startup_error = traceback.format_exc()
    print("API routers failed to load:", e)

    @app.get("/{full_path:path}")
    async def startup_failure(full_path: str = ""):
        if full_path == "health":
            return health()
        return JSONResponse(
            status_code=500,
            content={
                "error": "API failed to start",
                "detail": _startup_error,
                "hint": "Add all env vars in Vercel → Settings → Environment Variables, then redeploy.",
            },
        )

