"""Item schemas."""

from pydantic import BaseModel
from typing import Optional, Dict, Any


class ItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    rarity: str
    item_type: str
    stat_bonuses: Dict[str, Any]
    physical_damage: int
    magical_damage: int
    physical_defense: int
    magical_defense: int
    
    class Config:
        from_attributes = True

