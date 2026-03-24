from sqlalchemy.orm import Session
from app.models import Chat

def save_chat(db: Session, user_id: int, q: str, r: str):
    chat = Chat(user_id=user_id, question=q, response=r)
    db.add(chat)
    db.commit()