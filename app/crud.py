import json
from app.model.chat1 import ChatHistory

def save_chat(db, user_id, question, answer, session_id, type="chat", metadata=None):
    record = ChatHistory(
        user_id=user_id,
        session_id=session_id,
        type=type,
        question=question,
        answer=answer,
        metadata=json.dumps(metadata) if metadata else None
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record