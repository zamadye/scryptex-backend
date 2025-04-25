
from typing import Optional, List
from pydantic import BaseModel, Field

class ChainInfo(BaseModel):
    name: str = Field(..., description="Chain name")
    rpc_url: str = Field(..., description="RPC URL")
    chain_id: int = Field(..., description="Chain ID")
    symbol: str = Field(..., description="Native token symbol")
    explorer_url: Optional[str] = Field(None, description="Block explorer URL")

class FarmingTask(BaseModel):
    name: str
    type: str  # swap, mint, bridge, etc.
    is_required: bool = True
    estimated_gas: float = 0.0
    status: str = "pending"  # pending, success, failed

class FarmingAnalyzeRequest(BaseModel):
    project_name: str
    chain: str
    wallet_address: Optional[str] = None

class FarmingStartRequest(BaseModel):
    project_id: str
    wallet_address: str
    tasks: List[str] = []

class FarmingProject(BaseModel):
    id: str
    name: str
    chain: str
    tasks: List[FarmingTask] = []
    last_farmed: Optional[str] = None
    status: str = "active"  # active, completed
