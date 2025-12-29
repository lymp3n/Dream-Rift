"""Character schemas."""

from pydantic import BaseModel
from typing import Optional, Dict, Any


class CharacterCreate(BaseModel):
    name: str
    character_class: str
    player_id: int


class CharacterResponse(BaseModel):
    id: int
    name: str
    level: int
    experience: int
    strength: int
    agility: int
    intelligence: int
    endurance: int
    wisdom: int
    luck: int
    character_class: str
    location_id: Optional[int]
    
    class Config:
        from_attributes = True


class CharacterStatsResponse(BaseModel):
    character: CharacterResponse
    stats: Dict[str, Any]
    max_hp: int
    max_mp: int

