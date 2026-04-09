# ============================================
# pdf_analyzer.py
# ============================================

from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import os

from app.database import SessionLocal
from app.model.chat1 import ChatHistory
from app.utils.deps import get_current_user
from app.utils.session import create_session_id
from app.crud import save_chat

# 🔥 IMPORT YOUR RAG FUNCTIONS
from app.agents.rag_agent import load_pdf, get_rag_context, ask_pdf

router = APIRouter()

# ============================================
# DB DEP
# ============================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================
# REQUEST MODEL (FIXED 422 ERROR)
# ============================================
class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None   # ✅ FIX

# ============================================
# 📄 UPLOAD PDF
# ============================================
@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user)
):
    os.makedirs("uploads", exist_ok=True)

    path = f"uploads/{user_id}_{file.filename}"

    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)

    # 🔥 CALL YOUR RAG LOADER
    load_pdf(str(user_id), path)

    return {
        "success": True,
        "message": "PDF uploaded and processed ✅"
    }

# ============================================
# 💬 CHAT WITH PDF
# ============================================
@router.post("/chat")
def chat_pdf(
    req: ChatRequest,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print("REQ:", req.dict())  # ✅ DEBUG

    # ✅ SESSION FIX
    session_id = req.session_id or create_session_id()

    # ============================================
    # FETCH LAST 5 CHAT HISTORY FROM DB
    # ============================================
    history = db.query(ChatHistory).filter(
        ChatHistory.user_id == user_id,
        ChatHistory.session_id == session_id
    ).order_by(ChatHistory.created_at.desc()).limit(5).all()

    history_text = ""
    for h in reversed(history):
        history_text += f"User: {h.question}\nAssistant: {h.answer}\n"

    # ============================================
    # 🔥 GET CONTEXT USING YOUR RAG
    # ============================================
    context = get_rag_context(str(user_id), req.question)

    if not context:
        return {
            "success": False,
            "response": "⚠️ Upload PDF first"
        }

    # ============================================
    # 🔥 USE YOUR ask_pdf() FUNCTION
    # ============================================
    answer = ask_pdf(str(user_id), req.question)

    # ============================================
    # SAVE CHAT TO DB
    # ============================================
    save_chat(
        db,
        user_id,
        req.question,
        answer,
        session_id,
        "pdf"
    )

    return {
        "success": True,
        "session_id": session_id,
        "data": {"answer": answer}
    }