"""Skills API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.src.database.base import get_db
from backend.src.models import Character, Skill
from backend.src.core.skills import (
    can_learn_skill,
    learn_skill,
    get_learned_skills,
    get_selected_skills,
    select_skill,
    deselect_skill
)

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("/")
def list_skills(db: Session = Depends(get_db)):
    """List all skills."""
    skills = db.query(Skill).all()
    return [
        {
            "id": skill.id,
            "name": skill.name,
            "description": skill.description,
            "skill_type": skill.skill_type.value,
            "required_level": skill.required_level,
            "allowed_classes": skill.allowed_classes or [],
        }
        for skill in skills
    ]


@router.get("/{character_id}/learned")
def get_character_skills(character_id: int, db: Session = Depends(get_db)):
    """Get learned skills for character."""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return get_learned_skills(character, db)


@router.get("/{character_id}/selected")
def get_selected(character_id: int, db: Session = Depends(get_db)):
    """Get selected skills for quick access."""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return get_selected_skills(character, db)


@router.post("/learn")
def learn(character_id: int, skill_id: int, db: Session = Depends(get_db)):
    """Learn a skill."""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    result = learn_skill(character, skill, db)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("reason", "Failed to learn skill"))
    
    return result


@router.post("/select")
def select(character_id: int, skill_id: int, slot: int, db: Session = Depends(get_db)):
    """Select a skill for quick access."""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    result = select_skill(character, skill_id, slot, db)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("reason", "Failed to select skill"))
    
    return result


@router.post("/deselect")
def deselect(character_id: int, slot: int, db: Session = Depends(get_db)):
    """Deselect a skill from quick access."""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    result = deselect_skill(character, slot, db)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("reason", "Failed to deselect skill"))
    
    return result

