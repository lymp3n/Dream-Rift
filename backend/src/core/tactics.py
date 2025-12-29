"""Tactics system for combat."""

from enum import Enum
from typing import Dict, Any


class TacticType(str, Enum):
    """Tactic types."""
    ATTACK = "attack"  # Тактика атаки (получается после успешной незаблокированной атаки)
    BLOCK = "block"  # Тактика блока (получается после успешного блока)
    CRITICAL_ATTACK = "critical_attack"  # Тактика критической атаки (получается после крита)
    COUNTER = "counter"  # Тактика контратаки (получается после успешного блока)
    DODGE = "dodge"  # Тактика уклонения (получается после уклонения)
    COMBO = "combo"  # Тактика комбо (получается после серии успешных атак)
    DEFENSIVE_STANCE = "defensive_stance"  # Оборонительная стойка (активная защита)
    AGGRESSIVE_STANCE = "aggressive_stance"  # Агрессивная стойка (увеличенный урон)


class TacticsManager:
    """Manages character tactics."""
    
    def __init__(self):
        self.tactics = {
            TacticType.ATTACK: 0,
            TacticType.BLOCK: 0,
            TacticType.CRITICAL_ATTACK: 0,
            TacticType.COUNTER: 0,
            TacticType.DODGE: 0,
            TacticType.COMBO: 0,
            TacticType.DEFENSIVE_STANCE: 0,
            TacticType.AGGRESSIVE_STANCE: 0,
        }
        self.max_tactics = 10  # Максимальное количество тактик каждого типа
    
    def add_tactic(self, tactic_type: TacticType, amount: int = 1):
        """Add tactics."""
        current = self.tactics.get(tactic_type, 0)
        self.tactics[tactic_type] = min(self.max_tactics, current + amount)
    
    def use_tactic(self, tactic_type: TacticType, amount: int = 1) -> bool:
        """Use tactics. Returns True if successful."""
        current = self.tactics.get(tactic_type, 0)
        if current >= amount:
            self.tactics[tactic_type] = current - amount
            return True
        return False
    
    def get_tactics(self, tactic_type: TacticType) -> int:
        """Get amount of specific tactic."""
        return self.tactics.get(tactic_type, 0)
    
    def get_all_tactics(self) -> Dict[str, int]:
        """Get all tactics."""
        return {t.value: self.tactics.get(t, 0) for t in TacticType}
    
    def reset(self):
        """Reset all tactics."""
        for tactic_type in TacticType:
            self.tactics[tactic_type] = 0


def generate_tactics_from_action(action_type: str, success: bool, is_crit: bool = False) -> Dict[TacticType, int]:
    """Generate tactics based on combat action."""
    tactics = {}
    
    if action_type == "attack" and success:
        tactics[TacticType.ATTACK] = 1
        if is_crit:
            tactics[TacticType.CRITICAL_ATTACK] = 1
            tactics[TacticType.COMBO] = 1  # Крит дает комбо тактику
    
    elif action_type == "block" and success:
        tactics[TacticType.BLOCK] = 1
        tactics[TacticType.COUNTER] = 1  # Успешный блок дает контратаку
    
    elif action_type == "dodge" and success:
        tactics[TacticType.DODGE] = 1
    
    return tactics

