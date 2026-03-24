from fastapi import FastAPI
from app.database import engine, Base
from app.routes.chat import router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lakshya AI - LangGraph")

app.include_router(router, prefix="/api")