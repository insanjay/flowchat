from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MessageBase(BaseModel):
    content: str
    message_type: str = "text"  # text, file, link, image
    file_url: Optional[str] = None
    file_type: Optional[str] = None

class MessageCreate(MessageBase):
    chat_id: int
    sender_id: int

class Message(MessageBase):
    id: int
    chat_id: int
    sender_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True  # FIX: Updated from deprecated from_attributes
