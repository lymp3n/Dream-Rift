"""Combat schemas."""

from pydantic import BaseModel
from typing import Optional, Dict, Any


class AttackRequest(BaseModel):
    character_id: int
    monster_id: int
    skill_id: Optional[int] = None


class AttackResponse(BaseModel):
    damage: int
    is_crit: bool
    monster_hp: int
    monster_max_hp: int
    message: str


class MonsterAttackResponse(BaseModel):
    damage: int
    character_hp: int
    character_max_hp: int
    message: str

