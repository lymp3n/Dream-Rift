"""Crafting API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.src.database.base import get_db
from backend.src.models import Character
from backend.src.core.crafting import check_crafting_recipe, craft_item
from typing import Dict, Any

router = APIRouter(prefix="/crafting", tags=["crafting"])


@router.post("/check")
def check_recipe(character_id: int, recipe: Dict[str, Any], db: Session = Depends(get_db)):
    """Check if character can craft item from recipe."""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return check_crafting_recipe(character, recipe, db)


@router.post("/craft")
def craft(character_id: int, recipe: Dict[str, Any], db: Session = Depends(get_db)):
    """Craft item from recipe."""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    result = craft_item(character, recipe, db)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("reason", "Failed to craft"))
    
    return result

