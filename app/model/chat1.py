from sqlalchemy import Column, Integer, Text, DateTime, Index, String
from datetime import datetime
from app.database import Base
import uuid

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)

    # ✅ FIXED HERE
    session_id = Column(String(255), default=lambda: str(uuid.uuid4()), index=True)

    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)

    type = Column(Text, default="chat")  # chat / pdf / quiz

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("idx_user_session", "user_id", "session_id"),
    )