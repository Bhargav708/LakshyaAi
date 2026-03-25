from fastapi import FastAPI
from app.database import engine, Base

from app.routes.chat import router as chat_router
from app.routes.auth import router as auth_router   # ✅ IMPORT FIX

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lakshya AI")

# ✅ Routers
app.include_router(chat_router, prefix="/api")
app.include_router(auth_router, prefix="/auth")