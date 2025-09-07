from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database.schemas import User
from app.models.user import UserCreate
from fastapi import HTTPException
from typing import List, Optional
import uuid
from datetime import datetime

def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user with UUID-based user_id"""
    db_user = User(
        username=user.username,
        email=user.email,
        google_id=user.google_id,
        status="online",
        created_at=datetime.utcnow(),
        last_seen=datetime.utcnow(),
        google_connected=bool(user.google_id)
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username or email already exists")

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """Get user by user_id"""
    return db.query(User).filter(User.user_id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def check_username_availability(db: Session, username: str) -> bool:
    """Check if username is available (not taken)"""
    user = get_user_by_username(db, username)
    return user is None

def search_users(db: Session, query: str, limit: int = 10) -> List[User]:
    """Search users by username substring"""
    return db.query(User).filter(
        User.username.ilike(f"%{query}%")
    ).limit(limit).all()

def update_user_status(db: Session, user_id: str, status: str) -> Optional[User]:
    """Update user online/offline status"""
    user = get_user_by_id(db, user_id)
    if user:
        user.status = status
        user.last_seen = datetime.utcnow()
        db.commit()
        db.refresh(user)
    return user

def get_user_by_google_id(db: Session, google_id: str) -> Optional[User]:
    """Get user by Google ID for Google login"""
    return db.query(User).filter(User.google_id == google_id).first()
