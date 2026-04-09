from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes.chat import router as chat_router
from app.routes.auth import router as auth_router
from app.routes.pdf_routes import router as pdf_router
from app.routes.quiz_routes import router as quiz_router
from app.routes.history_router import router as history_router

app = FastAPI(title="Lakshya AI")

# Allowed origins
origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:5173",
    "https://lakshya-ai.netlify.app",
]

# Add CORS middleware BEFORE routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Routers
app.include_router(chat_router, prefix="/chat")
app.include_router(auth_router, prefix="/auth")
app.include_router(pdf_router, prefix="/pdf")
app.include_router(quiz_router, prefix="/quiz")
app.include_router(history_router)

# Health check endpoints
@app.get("/")
def root():
    return {"message": "Lakshya AI Backend is running"}

@app.get("/health")
def health():
    return {"status": "ok"}
