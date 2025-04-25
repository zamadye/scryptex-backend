
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class TwitterPost(BaseModel):
    id: str
    user_id: str
    project_id: Optional[str] = None
    content: str
    hashtags: List[str] = []
    mentions: List[str] = []
    scheduled_for: Optional[datetime] = None
    status: str = "draft"  # draft, posted, failed
    tweet_id: Optional[str] = None  # Twitter's post ID after posting
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TwitterThread(BaseModel):
    id: str
    user_id: str
    project_id: Optional[str] = None
    posts: List[TwitterPost] = []
    status: str = "draft"  # draft, posted, failed
    scheduled_for: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TwitterAccount(BaseModel):
    user_id: str
    twitter_handle: str
    is_connected: bool = False
    connected_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
