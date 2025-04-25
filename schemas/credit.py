
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class CreditStatusResponse(BaseModel):
    balance: float
    lifetime_earned: float
    lifetime_spent: float
    recent_logs: List[dict]

class CreditUseRequest(BaseModel):
    amount: float
    action: str
    related_entity: Optional[str] = None

class CreditTopupRequest(BaseModel):
    amount: float
    payment_method: str  # "crypto" or "fiat"
    wallet_address: Optional[str] = None
