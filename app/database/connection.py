from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker  # FIX: Updated import
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./messages.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class MessageDB(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    message_type = Column(String, default="text")
    file_url = Column(String, nullable=True)
    file_type = Column(String, nullable=True)
    chat_id = Column(Integer)
    sender_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

def create_tables():
    Base.metadata.create_all(bind=engine)
