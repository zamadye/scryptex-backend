
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: str
    wallet_address: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenData(BaseModel):
    username: str
    user_id: str

class Token(BaseModel):
    access_token: str
    token_type: str

class CreditLog(BaseModel):
    user_id: str
    action: str  # "use", "topup", "daily", "referral"
    amount: int
    description: str
    timestamp: str

class ReferralInfo(BaseModel):
    code: str
    referred_count: int = 0
    total_earned: int = 0
