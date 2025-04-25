
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class CreditTopUpRequest(BaseModel):
    user_id: str
    amount: float
    currency: str = "USDT"  # Always store as USDT
    payment_method: str  # "crypto" or "fiat"
    wallet_address: Optional[str] = None  # For crypto payments
    transaction_hash: Optional[str] = None  # For crypto payments
    status: str = "pending"  # pending, approved, rejected
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CreditLog(BaseModel):
    user_id: str
    action: str  # "use", "topup", "referral", "system"
    amount: float
    description: str
    related_entity: Optional[str] = None  # project_id, farming_id, etc.
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CreditBalance(BaseModel):
    user_id: str
    balance: float = 0.0
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    lifetime_earned: float = 0.0
    lifetime_spent: float = 0.0
