"""Market schemas."""

from pydantic import BaseModel
from typing import Optional


class MarketOrderCreate(BaseModel):
    character_id: int
    item_id: int
    order_type: str  # "buy" or "sell"
    price: float
    quantity: int


class MarketOrderResponse(BaseModel):
    id: int
    character_id: int
    item_id: int
    order_type: str
    status: str
    price: float
    quantity: int
    filled_quantity: int
    created_at: Optional[str]
    
    class Config:
        from_attributes = True

