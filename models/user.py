
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

class UserInDB(BaseModel):
    id: str
    username: str
    email: EmailStr
    password_hash: str
    wallet_address: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    credits: int = 100  # Default credits for new users
    role: str = "user"  # Could be "user", "admin", etc.
    
class User(BaseModel):
    id: str
    username: str
    email: EmailStr
    wallet_address: Optional[str] = None
    created_at: datetime
    credits: int
    role: str
