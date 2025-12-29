"""Skills system."""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.src.models import Skill, CharacterSkill, Character, CharacterClass


def can_learn_skill(character: Character, skill: Skill) -> Dict[str, Any]:
    """Check if character can learn a skill."""
    # Check level requirement
    if character.level < skill.required_level:
        return {
            "can_learn": False,
            "reason": f"Требуется уровень {skill.required_level}"
        }
    
    # Check stat requirements
    if character.strength < skill.required_strength:
        return {
            "can_learn": False,
            "reason": f"Требуется STR {skill.required_strength}"
        }
    if character.agility < skill.required_agility:
        return {
            "can_learn": False,
            "reason": f"Требуется AGI {skill.required_agility}"
        }
    if character.intelligence < skill.required_intelligence:
        return {
            "can_learn": False,
            "reason": f"Требуется INT {skill.required_intelligence}"
        }
    if character.endurance < skill.required_endurance:
        return {
            "can_learn": False,
            "reason": f"Требуется END {skill.required_endurance}"
        }
    if character.wisdom < skill.required_wisdom:
        return {
            "can_learn": False,
            "reason": f"Требуется WIS {skill.required_wisdom}"
        }
    
    # Check class restrictions
    if skill.allowed_classes:
        if character.character_class.value not in skill.allowed_classes:
            return {
                "can_learn": False,
                "reason": f"Навык доступен только для классов: {', '.join(skill.allowed_classes)}"
            }
    
    return {
        "can_learn": True,
        "message": "Можно изучить"
    }


def learn_skill(character: Character, skill: Skill, db: Session) -> Dict[str, Any]:
    """Learn a skill."""
    check = can_learn_skill(character, skill)
    if not check["can_learn"]:
        return check
    
    # Check if already learned
    existing = db.query(CharacterSkill).filter(
        CharacterSkill.character_id == character.id,
        CharacterSkill.skill_id == skill.id
    ).first()
    
    if existing:
        return {
            "success": False,
            "reason": "Навык уже изучен"
        }
    
    # Learn skill
    char_skill = CharacterSkill(
        character_id=character.id,
        skill_id=skill.id,
        is_selected=0,  # Not selected by default
        learned_at_level=character.level
    )
    db.add(char_skill)
    db.commit()
    
    return {
        "success": True,
        "message": f"Навык '{skill.name}' изучен"
    }


def get_learned_skills(character: Character, db: Session) -> List[Dict[str, Any]]:
    """Get all learned skills for character."""
    char_skills = db.query(CharacterSkill).filter(
        CharacterSkill.character_id == character.id
    ).all()
    
    return [
        {
            "id": cs.skill.id,
            "name": cs.skill.name,
            "description": cs.skill.description,
            "skill_type": cs.skill.skill_type.value,
            "is_selected": cs.is_selected,
            "selected_slot": cs.is_selected if cs.is_selected > 0 else None,
            "effects": cs.skill.effects,
        }
        for cs in char_skills
    ]


def get_selected_skills(character: Character, db: Session) -> List[Dict[str, Any]]:
    """Get selected skills (for quick access bar)."""
    char_skills = db.query(CharacterSkill).filter(
        CharacterSkill.character_id == character.id,
        CharacterSkill.is_selected > 0
    ).order_by(CharacterSkill.is_selected).all()
    
    return [
        {
            "id": cs.skill.id,
            "name": cs.skill.name,
            "slot": cs.is_selected,
            "effects": cs.skill.effects,
        }
        for cs in char_skills
    ]


def select_skill(character: Character, skill_id: int, slot: int, db: Session) -> Dict[str, Any]:
    """Select a skill for quick access bar (slots 1-6)."""
    if slot < 1 or slot > 6:
        return {
            "success": False,
            "reason": "Слот должен быть от 1 до 6"
        }
    
    # Check if skill is learned
    char_skill = db.query(CharacterSkill).filter(
        CharacterSkill.character_id == character.id,
        CharacterSkill.skill_id == skill_id
    ).first()
    
    if not char_skill:
        return {
            "success": False,
            "reason": "Навык не изучен"
        }
    
    # Clear slot if another skill is there
    existing = db.query(CharacterSkill).filter(
        CharacterSkill.character_id == character.id,
        CharacterSkill.is_selected == slot
    ).first()
    if existing:
        existing.is_selected = 0
    
    # Set skill to slot
    char_skill.is_selected = slot
    db.commit()
    
    return {
        "success": True,
        "message": f"Навык установлен в слот {slot}"
    }


def deselect_skill(character: Character, slot: int, db: Session) -> Dict[str, Any]:
    """Deselect a skill from quick access bar."""
    char_skill = db.query(CharacterSkill).filter(
        CharacterSkill.character_id == character.id,
        CharacterSkill.is_selected == slot
    ).first()
    
    if not char_skill:
        return {
            "success": False,
            "reason": "Слот пуст"
        }
    
    char_skill.is_selected = 0
    db.commit()
    
    return {
        "success": True,
        "message": f"Слот {slot} очищен"
    }

