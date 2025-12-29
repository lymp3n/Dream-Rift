"""Inventory API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.src.database.base import get_db
from backend.src.models import Character
from backend.src.core.inventory import get_inventory, get_equipment, equip_item, unequip_item

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/{character_id}")
def get_character_inventory(character_id: int, db: Session = Depends(get_db)):
    """Get character inventory."""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return get_inventory(character, db)


@router.get("/{character_id}/equipment")
def get_character_equipment(character_id: int, db: Session = Depends(get_db)):
    """Get character equipment."""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return get_equipment(character, db)


@router.post("/equip")
def equip(character_id: int, item_id: int, db: Session = Depends(get_db)):
    """Equip an item."""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    result = equip_item(character, item_id, db)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("reason", "Failed to equip"))
    
    return result


@router.post("/unequip")
def unequip(character_id: int, slot_name: str, db: Session = Depends(get_db)):
    """Unequip an item."""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    result = unequip_item(character, slot_name, db)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("reason", "Failed to unequip"))
    
    return result

