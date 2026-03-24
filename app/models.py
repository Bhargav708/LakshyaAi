from sqlalchemy import Column, Integer, Text, DateTime
from datetime import datetime
from app.database import Base

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    question = Column(Text)
    response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)