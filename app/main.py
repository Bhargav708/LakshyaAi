from fastapi import FastAPI
from app.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chat import router as chat_router
from app.routes.auth import router as auth_router
from app.routes.pdf_routes import router as pdf_router 
from app.routes.quiz_routes import router as quiz_router  # ✅ IMPORT FIX
from app.routes.history_router import router as history_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lakshya AI")
origins = [
    "http://localhost:8080",  # your frontend
    "http://127.0.0.1:8080",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔥 for dev (later restrict)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Routers
app.include_router(chat_router, prefix="/chat")
app.include_router(auth_router, prefix="/auth")
app.include_router(pdf_router, prefix="/pdf")
app.include_router(quiz_router,prefix="/quiz")
app.include_router(history_router)