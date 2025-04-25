
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class TwitterPostCreate(BaseModel):
    project_id: str
    topic: str
    tone: str = "informative"  # informative, enthusiastic, critical

class TwitterThreadCreate(BaseModel):
    project_id: str
    topics: List[str]

class TwitterAccountConnect(BaseModel):
    twitter_handle: str
