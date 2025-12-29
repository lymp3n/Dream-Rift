"""Game formulas."""

from typing import Dict, Any


def calculate_max_hp(level: int, strength: int, endurance: int) -> int:
    """Calculate maximum HP.
    
    Formula: (30 + (Уровень * 10)) + (STR * 3) + (END * 5)
    """
    return int(30 + (level * 10) + (strength * 3) + (endurance * 5))


def calculate_max_mp(level: int, intelligence: int, wisdom: int) -> int:
    """Calculate maximum MP.
    
    Formula: (20 + (Уровень * 5)) + (INT * 4) + (WIS * 2)
    """
    return int(20 + (level * 5) + (intelligence * 4) + (wisdom * 2))


def calculate_physical_damage(strength: int, weapon_bonus: int = 0) -> Dict[str, int]:
    """Calculate physical damage range.
    
    Formula: (Сила * 2) + Бонус оружия ±15%
    Returns: {"min": int, "max": int}
    """
    base_damage = (strength * 2) + weapon_bonus
    min_damage = int(base_damage * 0.85)
    max_damage = int(base_damage * 1.15)
    return {"min": min_damage, "max": max_damage}


def calculate_magical_damage(intelligence: int, weapon_bonus: int = 0) -> Dict[str, int]:
    """Calculate magical damage range.
    
    Formula: (Интеллект * 1.8) + Бонус ±10%
    Returns: {"min": int, "max": int}
    """
    base_damage = (intelligence * 1.8) + weapon_bonus
    min_damage = int(base_damage * 0.9)
    max_damage = int(base_damage * 1.1)
    return {"min": min_damage, "max": max_damage}


def calculate_physical_defense(endurance: int, armor_bonus: int = 0) -> int:
    """Calculate physical defense.
    
    Formula: (Выносливость * 1.5) + Бонус брони
    Works as direct subtraction from incoming physical damage.
    """
    return int((endurance * 1.5) + armor_bonus)


def calculate_magical_defense(wisdom: int, armor_bonus: int = 0) -> float:
    """Calculate magical defense percentage.
    
    Formula: (Мудрость * 0.8) + Бонус
    Works as percentage reduction (e.g., 12 = 12% reduction).
    """
    return float((wisdom * 0.8) + armor_bonus)


def calculate_crit_chance(agility: int, luck: int, bonuses: int = 0) -> float:
    """Calculate critical hit chance.
    
    Formula: (Ловкость * 0.1) + (Удача * 0.05) + Бонусы
    Returns: Percentage (e.g., 5.0 = 5%)
    """
    return float((agility * 0.1) + (luck * 0.05) + bonuses)


def calculate_crit_damage(base_damage: int) -> int:
    """Calculate critical hit damage.
    
    Formula: обычный урон * 1.8
    """
    return int(base_damage * 1.8)


def calculate_speed(agility: int, bonuses: int = 0) -> int:
    """Calculate speed.
    
    Formula: (Ловкость * 0.7) + Бонусы
    Determines turn order in combat.
    """
    return int((agility * 0.7) + bonuses)


def apply_physical_damage(damage: int, defense: int) -> int:
    """Apply physical damage with defense.
    
    Physical defense works as direct subtraction.
    """
    return max(1, damage - defense)


def apply_magical_damage(damage: int, defense_percentage: float) -> int:
    """Apply magical damage with defense.
    
    Magical defense works as percentage reduction.
    """
    reduction = damage * (defense_percentage / 100.0)
    return max(1, int(damage - reduction))

