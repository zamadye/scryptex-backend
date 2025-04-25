
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class ChatMessage(BaseModel):
    content: str
    sender: str  # "user" or "bot"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatThread(BaseModel):
    id: str
    user_id: Optional[str] = None  # Anonymous chat if null
    messages: List[ChatMessage] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = False

class ChatMessageCreate(BaseModel):
    content: str
    thread_id: Optional[str] = None  # Create new thread if null
