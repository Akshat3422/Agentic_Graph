import time
from fastapi import FastAPI,Request
import uuid
from routes.user import user_router
from routes.auth_routes import router
from  routes.transactions_routes import transaction_router
from  routes.accounts_routes import account_router
from database import Base,engine,get_db
from chatbot.graph import final_graph,router as new_router

app=FastAPI()

@app.on_event("startup")
def startup():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print("DB init failed:", e)



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




app.include_router(user_router)
app.include_router(router)
app.include_router(account_router)
app.include_router(transaction_router)
app.include_router(router=new_router)

