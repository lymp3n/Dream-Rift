"""Combat system."""

import random
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.src.models import Character, Monster
from backend.src.utils.formulas import (
    calculate_physical_damage,
    calculate_magical_damage,
    calculate_physical_defense,
    calculate_magical_defense,
    calculate_crit_chance,
    calculate_crit_damage,
    calculate_speed,
    apply_physical_damage,
    apply_magical_damage,
)


class CombatState:
    """Combat state."""
    
    def __init__(self, character: Character, monster: Monster):
        self.character = character
        self.monster = monster
        self.character_hp = self._calculate_character_hp()
        self.monster_hp = monster.current_hp
        self.turn = 0
        self.combat_log = []
    
    def _calculate_character_hp(self) -> int:
        """Calculate character max HP."""
        from backend.src.utils.formulas import calculate_max_hp
        return calculate_max_hp(
            self.character.level,
            self.character.strength,
            self.character.endurance
        )


def calculate_character_stats(character: Character, db: Session) -> Dict[str, Any]:
    """Calculate all character derived stats."""
    # Get equipment bonuses
    equipment = character.equipment
    weapon_bonus = 0
    armor_bonus = 0
    stat_bonuses = {
        "strength": 0,
        "agility": 0,
        "intelligence": 0,
        "endurance": 0,
        "wisdom": 0,
        "luck": 0,
    }
    
    if equipment:
        # Sum bonuses from all equipped items
        for slot_name in ["helmet_id", "chest_id", "belt_id", "legs_id", "boots_id", "weapon_id", "accessory1_id", "accessory2_id"]:
            item_id = getattr(equipment, slot_name, None)
            if item_id:
                from backend.src.models import Item
                item = db.query(Item).filter(Item.id == item_id).first()
                if item:
                    if item.stat_bonuses:
                        for stat, bonus in item.stat_bonuses.items():
                            stat_bonuses[stat] += bonus
                    weapon_bonus += item.physical_damage or 0
                    armor_bonus += item.physical_defense or 0
    
    # Calculate stats with bonuses
    total_strength = character.strength + stat_bonuses["strength"]
    total_agility = character.agility + stat_bonuses["agility"]
    total_intelligence = character.intelligence + stat_bonuses["intelligence"]
    total_endurance = character.endurance + stat_bonuses["endurance"]
    total_wisdom = character.wisdom + stat_bonuses["wisdom"]
    total_luck = character.luck + stat_bonuses["luck"]
    
    # Calculate derived stats
    phys_damage = calculate_physical_damage(total_strength, weapon_bonus)
    mag_damage = calculate_magical_damage(total_intelligence, 0)
    phys_def = calculate_physical_defense(total_endurance, armor_bonus)
    mag_def = calculate_magical_defense(total_wisdom, 0)
    crit_chance = calculate_crit_chance(total_agility, total_luck, 0)
    speed = calculate_speed(total_agility, 0)
    
    return {
        "physical_damage": phys_damage,
        "magical_damage": mag_damage,
        "physical_defense": phys_def,
        "magical_defense": mag_def,
        "crit_chance": crit_chance,
        "speed": speed,
        "max_hp": calculate_max_hp(character.level, total_strength, total_endurance),
        "max_mp": calculate_max_mp(character.level, total_intelligence, total_wisdom),
    }


def calculate_max_hp(level: int, strength: int, endurance: int) -> int:
    """Calculate max HP."""
    from backend.src.utils.formulas import calculate_max_hp as calc_hp
    return calc_hp(level, strength, endurance)


def calculate_max_mp(level: int, intelligence: int, wisdom: int) -> int:
    """Calculate max MP."""
    from backend.src.utils.formulas import calculate_max_mp as calc_mp
    return calc_mp(level, intelligence, wisdom)


def attack_monster(character: Character, monster: Monster, db: Session, use_skill: Optional[int] = None) -> Dict[str, Any]:
    """Character attacks monster."""
    char_stats = calculate_character_stats(character, db)
    
    # Determine damage type and amount
    if use_skill:
        # Skill attack (to be implemented)
        damage_type = "physical"  # Default
        base_damage = random.randint(char_stats["physical_damage"]["min"], char_stats["physical_damage"]["max"])
    else:
        # Basic attack
        damage_type = "physical"
        base_damage = random.randint(char_stats["physical_damage"]["min"], char_stats["physical_damage"]["max"])
    
    # Check for crit
    is_crit = random.random() * 100 < char_stats["crit_chance"]
    if is_crit:
        damage = calculate_crit_damage(base_damage)
        crit_text = " КРИТИЧЕСКИЙ УДАР!"
    else:
        damage = base_damage
        crit_text = ""
    
    # Apply defense
    final_damage = apply_physical_damage(damage, monster.physical_defense)
    monster.current_hp = max(0, monster.current_hp - final_damage)
    
    result = {
        "damage": final_damage,
        "is_crit": is_crit,
        "monster_hp": monster.current_hp,
        "monster_max_hp": monster.max_hp,
        "message": f"Вы нанесли {final_damage} урона{crit_text}",
    }
    
    db.commit()
    return result


def monster_attack(monster: Monster, character: Character, db: Session) -> Dict[str, Any]:
    """Monster attacks character."""
    char_stats = calculate_character_stats(character, db)
    
    # Calculate monster damage
    base_damage = random.randint(monster.physical_damage_min, monster.physical_damage_max)
    
    # Apply character defense
    final_damage = apply_physical_damage(base_damage, char_stats["physical_defense"])
    
    # Calculate character current HP (simplified - should be stored)
    from backend.src.utils.formulas import calculate_max_hp
    max_hp = calculate_max_hp(character.level, character.strength, character.endurance)
    # In real implementation, current_hp should be stored in Character model
    # For now, we'll assume it's at max
    current_hp = max(0, max_hp - final_damage)
    
    result = {
        "damage": final_damage,
        "character_hp": current_hp,
        "character_max_hp": max_hp,
        "message": f"{monster.name} нанес {final_damage} урона",
    }
    
    return result


def determine_turn_order(character: Character, monster: Monster, db: Session) -> str:
    """Determine who goes first based on speed."""
    char_stats = calculate_character_stats(character, db)
    char_speed = char_stats["speed"]
    monster_speed = monster.speed
    
    if char_speed >= monster_speed:
        return "character"
    return "monster"

