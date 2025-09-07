from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    google_id: Optional[str] = None

class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    status: str = "offline"
    created_at: datetime
    google_connected: bool = False

class UsernameCheck(BaseModel):
    username: str
    
class UsernameAvailability(BaseModel):
    available: bool
    message: str

class GoogleLoginData(BaseModel):
    google_token: str
    username: Optional[str] = None

class LoginResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"

class UserSearch(BaseModel):
    query: str
    limit: Optional[int] = 10

class UserSearchResult(BaseModel):
    users: list[UserResponse]
    total: int
