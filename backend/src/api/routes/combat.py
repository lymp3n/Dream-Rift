"""Combat API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.src.database.base import get_db
from backend.src.models import Character, Monster
from backend.src.api.schemas.combat import AttackRequest, AttackResponse, MonsterAttackResponse
from backend.src.core.combat import attack_monster, monster_attack, determine_turn_order

router = APIRouter(prefix="/combat", tags=["combat"])


@router.post("/attack", response_model=AttackResponse)
def attack(attack_req: AttackRequest, db: Session = Depends(get_db)):
    """Character attacks monster."""
    character = db.query(Character).filter(Character.id == attack_req.character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    monster = db.query(Monster).filter(Monster.id == attack_req.monster_id).first()
    if not monster:
        raise HTTPException(status_code=404, detail="Monster not found")
    
    if monster.current_hp <= 0:
        raise HTTPException(status_code=400, detail="Monster is already dead")
    
    result = attack_monster(character, monster, db, attack_req.skill_id)
    return result


@router.post("/monster-attack", response_model=MonsterAttackResponse)
def monster_attacks(character_id: int, monster_id: int, db: Session = Depends(get_db)):
    """Monster attacks character."""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    monster = db.query(Monster).filter(Monster.id == monster_id).first()
    if not monster:
        raise HTTPException(status_code=404, detail="Monster not found")
    
    result = monster_attack(monster, character, db)
    return result


@router.get("/turn-order")
def get_turn_order(character_id: int, monster_id: int, db: Session = Depends(get_db)):
    """Determine turn order."""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    monster = db.query(Monster).filter(Monster.id == monster_id).first()
    if not monster:
        raise HTTPException(status_code=404, detail="Monster not found")
    
    first = determine_turn_order(character, monster, db)
    return {"first": first}

