"""Location and travel system."""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from backend.src.models import Location, Character, Monster


def get_location_info(location_id: int, db: Session) -> Dict[str, Any]:
    """Get information about a location."""
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        return None
    
    # Get monsters at location
    monsters = db.query(Monster).filter(Monster.location_id == location_id).all()
    
    return {
        "id": location.id,
        "name": location.name,
        "description": location.description,
        "travel_time": location.travel_time,
        "connected_locations": location.connected_locations or [],
        "monsters": [
            {
                "id": m.id,
                "name": m.name,
                "level": m.level,
                "current_hp": m.current_hp,
                "max_hp": m.max_hp,
            }
            for m in monsters
        ]
    }


def can_travel(character: Character, target_location_id: int, db: Session) -> Dict[str, Any]:
    """Check if character can travel to location."""
    if not character.location_id:
        return {
            "can_travel": True,
            "reason": "Персонаж не в локации"
        }
    
    current_location = db.query(Location).filter(Location.id == character.location_id).first()
    if not current_location:
        return {
            "can_travel": False,
            "reason": "Текущая локация не найдена"
        }
    
    target_location = db.query(Location).filter(Location.id == target_location_id).first()
    if not target_location:
        return {
            "can_travel": False,
            "reason": "Целевая локация не найдена"
        }
    
    # Check if locations are connected
    connected = target_location.connected_locations or []
    if character.location_id not in connected and target_location_id not in (current_location.connected_locations or []):
        return {
            "can_travel": False,
            "reason": "Локации не связаны"
        }
    
    return {
        "can_travel": True,
        "travel_time": target_location.travel_time,
        "message": f"Путешествие займет {target_location.travel_time} секунд"
    }


def start_travel(character: Character, target_location_id: int, db: Session) -> Dict[str, Any]:
    """Start travel to location."""
    check = can_travel(character, target_location_id, db)
    if not check["can_travel"]:
        return check
    
    target_location = db.query(Location).filter(Location.id == target_location_id).first()
    
    # In real implementation, we'd store travel_start_time
    # For now, just update location immediately (travel will be handled client-side with timer)
    character.location_id = target_location_id
    db.commit()
    
    return {
        "success": True,
        "location_id": target_location_id,
        "location_name": target_location.name,
        "travel_time": target_location.travel_time,
        "message": f"Вы перемещаетесь в {target_location.name}..."
    }


def get_available_locations(character: Character, db: Session) -> List[Dict[str, Any]]:
    """Get locations available for travel from character's current location."""
    if not character.location_id:
        # Character not in any location, return all
        locations = db.query(Location).all()
        return [
            {
                "id": loc.id,
                "name": loc.name,
                "description": loc.description,
            }
            for loc in locations
        ]
    
    current_location = db.query(Location).filter(Location.id == character.location_id).first()
    if not current_location:
        return []
    
    connected_ids = current_location.connected_locations or []
    if not connected_ids:
        return []
    
    locations = db.query(Location).filter(Location.id.in_(connected_ids)).all()
    
    return [
        {
            "id": loc.id,
            "name": loc.name,
            "description": loc.description,
            "travel_time": loc.travel_time,
        }
        for loc in locations
    ]

