
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional

class FeedbackCreate(BaseModel):
    type: str = Field(..., description="Type of feedback (bug, feature, other)")
    message: str = Field(..., description="Feedback message")
    email: Optional[EmailStr] = Field(None, description="User email for follow-up")
    user_id: Optional[str] = Field(None, description="User ID if logged in")

class FeedbackInDB(FeedbackCreate):
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = False
