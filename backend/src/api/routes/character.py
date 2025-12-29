"""Character API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.src.database.base import get_db
from backend.src.models import Character, CharacterClass
from backend.src.api.schemas.character import CharacterCreate, CharacterResponse, CharacterStatsResponse
from backend.src.core.character import get_class_stat_bonuses
from backend.src.core.combat import calculate_character_stats

router = APIRouter(prefix="/characters", tags=["characters"])


@router.post("/", response_model=CharacterResponse)
def create_character(character: CharacterCreate, db: Session = Depends(get_db)):
    """Create a new character."""
    try:
        char_class = CharacterClass(character.character_class)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid character class")
    
    db_character = Character(
        player_id=character.player_id,
        name=character.name,
        character_class=char_class,
        level=1,
        experience=0,
        strength=10,
        agility=10,
        intelligence=10,
        endurance=10,
        wisdom=10,
        luck=10,
    )
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character


@router.get("/{character_id}", response_model=CharacterResponse)
def get_character(character_id: int, db: Session = Depends(get_db)):
    """Get character by ID."""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character


@router.get("/{character_id}/stats", response_model=CharacterStatsResponse)
def get_character_stats(character_id: int, db: Session = Depends(get_db)):
    """Get character with calculated stats."""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    stats = calculate_character_stats(character, db)
    from backend.src.utils.formulas import calculate_max_hp, calculate_max_mp
    
    max_hp = calculate_max_hp(character.level, character.strength, character.endurance)
    max_mp = calculate_max_mp(character.level, character.intelligence, character.wisdom)
    
    return CharacterStatsResponse(
        character=character,
        stats=stats,
        max_hp=max_hp,
        max_mp=max_mp
    )

