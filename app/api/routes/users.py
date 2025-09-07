from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database import crud
from app.models.user import (
    UserCreate, 
    UserResponse, 
    UsernameCheck, 
    UsernameAvailability, 
    GoogleLoginData, 
    LoginResponse,
    UserSearch,
    UserSearchResult
)
from typing import List
from jose import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from app.utils.google_auth import verify_google_token

# Load environment variables
load_dotenv()

router = APIRouter(prefix="/api/users", tags=["users"])

# JWT Configuration - move these to environment variables
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with unique username and UUID-based user_id"""
    # Check if username is available
    if not crud.check_username_availability(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Check if email already exists
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    created_user = crud.create_user(db, user)
    
    return UserResponse(
        user_id=created_user.user_id,
        username=created_user.username,
        email=created_user.email,
        status=created_user.status,
        created_at=created_user.created_at,
        google_connected=bool(created_user.google_id)
    )

@router.post("/check-username", response_model=UsernameAvailability)
async def check_username_availability_endpoint(
    username_data: UsernameCheck, 
    db: Session = Depends(get_db)
):
    """Check if username is available"""
    available = crud.check_username_availability(db, username_data.username)
    return UsernameAvailability(
        available=available,
        message="Username is available" if available else "Username already taken"
    )

@router.get("/check-username/{username}", response_model=UsernameAvailability)
async def check_username_get(username: str, db: Session = Depends(get_db)):
    """Check username availability via GET request"""
    available = crud.check_username_availability(db, username)
    return UsernameAvailability(
        available=available,
        message="Username is available" if available else "Username already taken"
    )

@router.post("/search", response_model=UserSearchResult)
async def search_users(search_data: UserSearch, db: Session = Depends(get_db)):
    """Search users by username substring"""
    users = crud.search_users(db, search_data.query, search_data.limit or 10)
    
    user_responses = [
        UserResponse(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            status=user.status,
            created_at=user.created_at,
            google_connected=bool(user.google_id)
        )
        for user in users
    ]
    
    return UserSearchResult(
        users=user_responses,
        total=len(user_responses)
    )

from app.utils.google_auth import verify_google_token

@router.post("/google-login", response_model=LoginResponse)
async def google_login(login_data: GoogleLoginData, db: Session = Depends(get_db)):
    """Handle Google OAuth login with real token verification"""
    
    # Verify Google token
    verification_result = verify_google_token(login_data.google_token)
    
    if not verification_result["status"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Google token"
        )
    
    user_info = verification_result["user_info"]
    
    # Check if user exists
    user = crud.get_user_by_google_id(db, user_info["google_id"])
    
    if not user:
        # Create new user with Google info
        username = login_data.username or user_info["email"].split("@")[0]
        
        # Ensure username is unique
        counter = 1
        original_username = username
        while not crud.check_username_availability(db, username):
            username = f"{original_username}{counter}"
            counter += 1
        
        new_user_data = UserCreate(
            username=username,
            email=user_info["email"],
            google_id=user_info["google_id"]
        )
        user = crud.create_user(db, new_user_data)
    
    # Generate JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_id}, 
        expires_delta=access_token_expires
    )
    
    user_response = UserResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        status="online",
        created_at=user.created_at,
        google_connected=True
    )
    
    return LoginResponse(
        user=user_response,
        access_token=access_token
    )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: str, db: Session = Depends(get_db)):
    """Get user by user_id"""
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        status=user.status,
        created_at=user.created_at,
        google_connected=bool(user.google_id)
    )
