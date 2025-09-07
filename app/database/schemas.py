from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    # UUID primary key stored as string for SQLite compatibility
    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # User identity fields
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    
    # Google authentication support
    google_id = Column(String(100), unique=True, nullable=True, index=True)
    
    # User status and timestamps
    status = Column(String(20), default='offline', nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    last_seen = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=True)
    
    # Google connection status
    google_connected = Column(Boolean, default=False, nullable=False)

# Add your Message and Chat models below following similar patterns
