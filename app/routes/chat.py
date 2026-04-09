from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.utils.session import create_session_id
from app.utils.deps import get_current_user
from app.database import SessionLocal
from app.model.chat1 import ChatHistory
from app.crud import save_chat
from app.services.ai_service import chat_with_memory

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ChatRequest(BaseModel):
    question: str
    session_id: str | None = None


@router.post("/ask")
def ask(req: ChatRequest, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):

    session_id = req.session_id or create_session_id()

    history = db.query(ChatHistory).filter(
        ChatHistory.user_id == user_id,
        ChatHistory.session_id == session_id
    ).order_by(ChatHistory.created_at).all()

    answer = chat_with_memory(req.question, history)
    response_text = answer.content

    save_chat(db, user_id, req.question, response_text, session_id, "chat")

    return {
        "success": True,
        "session_id": session_id,
        "data": {"answer": response_text}
    }
@router.get("/history")
def get_history(
    session_id: str,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chats = db.query(ChatHistory).filter(
        ChatHistory.user_id == user_id,
        ChatHistory.session_id == session_id
    ).order_by(ChatHistory.created_at).all()

    return chats
@router.get("/history/{session_id}")
def get_history_by_session(
    session_id: str,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chats = db.query(ChatHistory).filter(
        ChatHistory.user_id == user_id,
        ChatHistory.session_id == session_id
    ).order_by(ChatHistory.created_at.asc()).all()

    return chats