"""Enhanced combat API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.src.database.base import get_db
from backend.src.models import Character, Monster
from backend.src.core.combat_enhanced import EnhancedCombatState
from typing import Optional

router = APIRouter(prefix="/combat-enhanced", tags=["combat-enhanced"])

# Store active combat states (in production, use Redis or DB)
active_combats: dict = {}


def get_combat_state(character_id: int, monster_id: int) -> Optional[EnhancedCombatState]:
    """Get or create combat state."""
    key = f"{character_id}_{monster_id}"
    return active_combats.get(key)


def set_combat_state(character_id: int, monster_id: int, state: EnhancedCombatState):
    """Store combat state."""
    key = f"{character_id}_{monster_id}"
    active_combats[key] = state


@router.post("/start")
def start_combat(character_id: int, monster_id: int, db: Session = Depends(get_db)):
    """Start combat."""
    # Check if combat already exists
    existing = get_combat_state(character_id, monster_id)
    if existing:
        return {
            "success": True,
            "combat_state": existing.get_combat_state(),
            "message": "Combat already in progress"
        }
    
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    monster = db.query(Monster).filter(Monster.id == monster_id).first()
    if not monster:
        raise HTTPException(status_code=404, detail="Monster not found")
    
    # Check if monster is in same location as character
    if character.location_id != monster.location_id:
        raise HTTPException(status_code=400, detail="Monster is not in the same location as character")
    
    # Reset monster HP if needed
    if monster.current_hp <= 0:
        monster.current_hp = monster.max_hp
        db.commit()
        db.refresh(monster)
    
    # Create combat state
    combat_state = EnhancedCombatState(character, monster, db)
    set_combat_state(character_id, monster_id, combat_state)
    
    state = combat_state.get_combat_state()
    state['monster_id'] = monster_id  # Add monster_id to state
    
    return {
        "success": True,
        "combat_state": state
    }


@router.post("/action")
def perform_action(
    character_id: int,
    monster_id: int,
    action_type: str,  # "attack", "skill", "block", "dodge"
    skill_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Perform combat action."""
    combat_state = get_combat_state(character_id, monster_id)
    if not combat_state:
        raise HTTPException(status_code=404, detail="Combat not found. Start combat first.")
    
    if combat_state.is_combat_over():
        winner = combat_state.get_winner()
        return {
            "combat_over": True,
            "winner": winner,
            "message": "Бой завершен!"
        }
    
    result = {}
    
    if action_type == "attack":
        result = combat_state.character_attack()
    elif action_type == "skill" and skill_id:
        result = combat_state.character_attack(skill_id)
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    # Check if action failed
    if not result.get("success"):
        return {
            "success": False,
            "error": result.get("error", "Action failed"),
            "combat_state": combat_state.get_combat_state()
        }
    
    # Check if combat is over
    if combat_state.is_combat_over():
        winner = combat_state.get_winner()
        result["combat_over"] = True
        result["winner"] = winner
        
        # Clean up
        key = f"{character_id}_{monster_id}"
        if key in active_combats:
            del active_combats[key]
    else:
        # Only end turn if action consumes turn
        if combat_state.current_turn and combat_state.current_turn.action_taken:
            # End character turn and start monster turn
            combat_state.end_turn()
            
            # Monster attacks
            if combat_state.current_turn and combat_state.current_turn.actor_type == "monster":
                monster_result = combat_state.monster_attack()
                result["monster_action"] = monster_result
                
                # End monster turn and start character turn
                combat_state.end_turn()
    
    return {
        "success": True,
        "action_result": result,
        "combat_state": combat_state.get_combat_state()
    }


@router.get("/state")
def get_state(character_id: int, monster_id: int):
    """Get current combat state."""
    combat_state = get_combat_state(character_id, monster_id)
    if not combat_state:
        raise HTTPException(status_code=404, detail="Combat not found")
    
    return combat_state.get_combat_state()


@router.post("/end-turn")
def end_turn(character_id: int, monster_id: int):
    """Manually end turn."""
    combat_state = get_combat_state(character_id, monster_id)
    if not combat_state:
        raise HTTPException(status_code=404, detail="Combat not found")
    
    result = combat_state.end_turn()
    
    # If monster's turn, auto-attack
    if combat_state.current_turn and combat_state.current_turn.actor_type == "monster":
        monster_result = combat_state.monster_attack()
        result["monster_action"] = monster_result
        combat_state.end_turn()
    
    return {
        "success": True,
        "result": result,
        "combat_state": combat_state.get_combat_state()
    }

