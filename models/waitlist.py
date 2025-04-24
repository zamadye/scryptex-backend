from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class WaitlistUser(BaseModel):
    email: EmailStr
    username: str
    referral_code: Optional[str] = None
    referred_by: Optional[str] = None
    referral_count: int = 0
    reward_pending_tex: int = 0
    created_at: datetime = datetime.utcnow()
