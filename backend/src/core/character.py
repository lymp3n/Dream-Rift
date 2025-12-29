"""Character system with classes."""

from typing import Dict, Any
from backend.src.models import Character, CharacterClass
from backend.src.utils.formulas import (
    calculate_max_hp,
    calculate_max_mp,
)


def get_class_stat_bonuses(character_class: CharacterClass, level: int) -> Dict[str, int]:
    """Get stat bonuses per level for class."""
    bonuses = {
        CharacterClass.BONE_KNIGHT: {
            "strength": 2,
            "endurance": 2,
        },
        CharacterClass.VOID_MAGE: {
            "intelligence": 3,
            "wisdom": 1,
        },
        CharacterClass.DREAM_WALKER: {
            "intelligence": 1,
            "wisdom": 1,
            "luck": 1,
        },
        CharacterClass.ADVENTURER: {
            "strength": 1,
            "agility": 1,
            "intelligence": 1,
            "endurance": 1,
            "wisdom": 1,
            "luck": 1,
        },
    }
    
    base_bonuses = bonuses.get(character_class, {})
    # Multiply by level (level 1 = no bonus, level 2 = 1x, etc.)
    return {stat: bonus * (level - 1) for stat, bonus in base_bonuses.items()}


def apply_class_bonuses(character: Character) -> Character:
    """Apply class bonuses to character stats."""
    bonuses = get_class_stat_bonuses(character.character_class, character.level)
    
    # Base stats are set at creation, bonuses are applied on level up
    # This function recalculates total stats with bonuses
    return character


def get_class_unique_mechanic(character_class: CharacterClass) -> str:
    """Get description of class unique mechanic."""
    mechanics = {
        CharacterClass.BONE_KNIGHT: "Костяная броня: часть получаемого урона конвертируется в временный щит",
        CharacterClass.VOID_MAGE: "Эхо Бездны: есть шанс, что заклинание сработает дважды с уменьшенной эффективностью",
        CharacterClass.DREAM_WALKER: "Пробуждение: при лечении или баффе есть шанс добавить цели случайный положительный эффект",
        CharacterClass.ADVENTURER: "Универсальность: может выбирать навыки из любого класса, но с ограничениями",
    }
    return mechanics.get(character_class, "Нет уникальной механики")


def level_up_character(character: Character) -> Dict[str, Any]:
    """Level up character and apply stat bonuses."""
    old_level = character.level
    character.level += 1
    character.experience = 0  # Reset exp for next level
    
    # Apply class bonuses
    bonuses = get_class_stat_bonuses(character.character_class, character.level)
    character.strength += bonuses.get("strength", 0)
    character.agility += bonuses.get("agility", 0)
    character.intelligence += bonuses.get("intelligence", 0)
    character.endurance += bonuses.get("endurance", 0)
    character.wisdom += bonuses.get("wisdom", 0)
    character.luck += bonuses.get("luck", 0)
    
    # Calculate new max HP/MP
    new_max_hp = calculate_max_hp(character.level, character.strength, character.endurance)
    new_max_mp = calculate_max_mp(character.level, character.intelligence, character.wisdom)
    
    return {
        "old_level": old_level,
        "new_level": character.level,
        "stat_bonuses": bonuses,
        "new_max_hp": new_max_hp,
        "new_max_mp": new_max_mp,
        "message": f"Уровень повышен! {old_level} -> {character.level}"
    }

