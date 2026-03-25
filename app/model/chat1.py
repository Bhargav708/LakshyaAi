from sqlalchemy import Column, Integer, Text, DateTime, Index
from datetime import datetime
from app.database import Base

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)

    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # 🔥 Optional: future use (like quiz / summary / normal chat)
    type = Column(Text, default="chat")

    __table_args__ = (
        Index("idx_user_time", "user_id", "created_at"),
    )