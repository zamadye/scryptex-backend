
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class FarmingTask(BaseModel):
    name: str
    type: str  # "mint", "swap", "bridge", etc.
    required: bool = True
    gas_cost_estimate: float = 0.0
    status: str = "pending"  # pending, running, completed, failed
    details: Optional[str] = None
    tx_hash: Optional[str] = None
    
class FarmingProject(BaseModel):
    id: str
    user_id: str
    project_name: str
    chain: str
    wallet_address: str
    tasks: List[FarmingTask] = []
    status: str = "pending"  # pending, running, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    recurring: bool = False
    recurring_schedule: Optional[str] = None  # cron expression

class FarmingLog(BaseModel):
    project_id: str
    user_id: str
    message: str
    level: str = "info"  # info, warning, error, success
    created_at: datetime = Field(default_factory=datetime.utcnow)
