import uuid
from sqlalchemy.orm import Session
from app.model.chat1 import ChatHistory

def save_history(db: Session, user_id: int, question: str, answer: str, type: str = "chat", session_id: str = None):

    if not session_id:
        session_id = str(uuid.uuid4())  # create new session

    history = ChatHistory(
        user_id=user_id,
        session_id=session_id,
        question=question,
        answer=answer,
        type=type
    )

    db.add(history)
    db.commit()
    db.refresh(history)

    return history