"""Location API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.src.database.base import get_db
from backend.src.models import Character, Location
from backend.src.core.location import get_location_info, start_travel, get_available_locations

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("/")
def list_locations(db: Session = Depends(get_db)):
    """List all locations."""
    locations = db.query(Location).all()
    return [
        {
            "id": loc.id,
            "name": loc.name,
            "description": loc.description,
        }
        for loc in locations
    ]


@router.get("/{location_id}")
def get_location(location_id: int, db: Session = Depends(get_db)):
    """Get location information."""
    info = get_location_info(location_id, db)
    if not info:
        raise HTTPException(status_code=404, detail="Location not found")
    return info


@router.post("/travel")
def travel(character_id: int, target_location_id: int, db: Session = Depends(get_db)):
    """Travel to location."""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    result = start_travel(character, target_location_id, db)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("reason", "Failed to travel"))
    
    return result


@router.get("/{character_id}/available")
def get_available(character_id: int, db: Session = Depends(get_db)):
    """Get available locations for travel."""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return get_available_locations(character, db)

