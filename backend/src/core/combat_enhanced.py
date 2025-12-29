"""Enhanced combat system with tactics, timing, and skill selection."""

import random
import time
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from backend.src.models import Character, Monster, Skill
from backend.src.core.combat import calculate_character_stats, calculate_max_hp, calculate_max_mp
from backend.src.core.tactics import TacticsManager, TacticType, generate_tactics_from_action
from backend.src.utils.formulas import (
    calculate_crit_damage,
    apply_physical_damage,
    apply_magical_damage,
)


class CombatTurn:
    """Represents a combat turn."""
    
    def __init__(self, actor_type: str, actor_id: int, time_limit: float):
        self.actor_type = actor_type  # "character" or "monster"
        self.actor_id = actor_id
        self.time_limit = time_limit
        self.start_time = datetime.now()
        self.action_taken = False
        self.action_type = None  # "attack", "skill", "block", "dodge"
        self.skill_id: Optional[int] = None
        self.result = None
    
    def is_expired(self) -> bool:
        """Check if turn time expired."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return elapsed >= self.time_limit
    
    def time_remaining(self) -> float:
        """Get remaining time in seconds."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return max(0, self.time_limit - elapsed)


class EnhancedCombatState:
    """Enhanced combat state with tactics and timing."""
    
    def __init__(self, character: Character, monster: Monster, db: Session):
        self.character = character
        self.monster = monster
        self.db = db
        
        # Calculate stats
        self.char_stats = calculate_character_stats(character, db)
        self.char_max_hp = calculate_max_hp(character.level, character.strength, character.endurance)
        self.char_max_mp = calculate_max_mp(character.level, character.intelligence, character.wisdom)
        
        # Current HP/MP (should be stored in Character model, but for now use max)
        # TODO: Add current_hp and current_mp to Character model
        self.char_hp = self.char_max_hp
        self.char_mp = self.char_max_mp
        self.monster_hp = monster.current_hp
        
        # Tactics
        self.tactics = TacticsManager()
        
        # Turn management
        self.turn_number = 0
        self.current_turn: Optional[CombatTurn] = None
        self.combat_log: List[Dict[str, Any]] = []
        
        # Timing configuration
        self.base_turn_time = 15.0  # Base turn time in seconds
        self.turn_time_reduction = 0.1  # 10% reduction per turn
        
        # Determine first turn
        self._determine_first_turn()
    
    def _determine_first_turn(self):
        """Determine who goes first based on speed."""
        char_speed = self.char_stats["speed"]
        monster_speed = self.monster.speed
        
        if char_speed >= monster_speed:
            self._start_character_turn()
        else:
            self._start_monster_turn()
    
    def _start_character_turn(self):
        """Start character's turn."""
        turn_time = self._calculate_turn_time()
        self.current_turn = CombatTurn("character", self.character.id, turn_time)
        self.turn_number += 1
    
    def _start_monster_turn(self):
        """Start monster's turn."""
        turn_time = self._calculate_turn_time()
        self.current_turn = CombatTurn("monster", self.monster.id, turn_time)
        self.turn_number += 1
    
    def _calculate_turn_time(self) -> float:
        """Calculate turn time with reduction."""
        reduction = self.turn_time_reduction * (self.turn_number - 1)
        return max(5.0, self.base_turn_time * (1 - reduction))  # Minimum 5 seconds
    
    def character_attack(self, skill_id: Optional[int] = None) -> Dict[str, Any]:
        """Character performs attack or skill."""
        if not self.current_turn or self.current_turn.actor_type != "character":
            return {"success": False, "error": "Not character's turn"}
        
        if self.current_turn.action_taken:
            return {"success": False, "error": "Action already taken this turn"}
        
        if self.current_turn.is_expired():
            return {"success": False, "error": "Turn time expired"}
        
        # Perform action
        if skill_id:
            result = self._use_skill(skill_id)
        else:
            result = self._basic_attack()
        
        # Check if action was successful
        if not result.get("success"):
            return result
        
        self.current_turn.action_taken = True
        self.current_turn.action_type = "skill" if skill_id else "attack"
        self.current_turn.result = result
        
        # Generate tactics
        if result.get("success"):
            tactics = generate_tactics_from_action(
                "attack",
                True,
                result.get("is_crit", False)
            )
            for tactic_type, amount in tactics.items():
                self.tactics.add_tactic(tactic_type, amount)
        
        return result
    
    def _basic_attack(self) -> Dict[str, Any]:
        """Perform basic attack."""
        damage_range = self.char_stats["physical_damage"]
        base_damage = random.randint(damage_range["min"], damage_range["max"])
        
        # Check for crit
        crit_chance = self.char_stats["crit_chance"]
        is_crit = random.random() * 100 < crit_chance
        
        if is_crit:
            damage = calculate_crit_damage(base_damage)
        else:
            damage = base_damage
        
        # Apply defense
        final_damage = apply_physical_damage(damage, self.monster.physical_defense)
        self.monster_hp = max(0, self.monster_hp - final_damage)
        
        # Update monster in DB
        self.monster.current_hp = self.monster_hp
        self.db.commit()
        
        return {
            "success": True,
            "action": "attack",
            "damage": final_damage,
            "is_crit": is_crit,
            "monster_hp": self.monster_hp,
            "monster_max_hp": self.monster.max_hp,
            "message": f"Вы нанесли {final_damage} урона{' (КРИТ!)' if is_crit else ''}"
        }
    
    def _use_skill(self, skill_id: int) -> Dict[str, Any]:
        """Use a skill."""
        skill = self.db.query(Skill).filter(Skill.id == skill_id).first()
        if not skill:
            return {"success": False, "error": "Skill not found"}
        
        # Check if skill is learned
        from backend.src.models import CharacterSkill
        char_skill = self.db.query(CharacterSkill).filter(
            CharacterSkill.character_id == self.character.id,
            CharacterSkill.skill_id == skill_id
        ).first()
        
        if not char_skill:
            return {"success": False, "error": "Skill not learned"}
        
        # Check MP cost
        mp_cost = skill.effects.get("mp_cost", 0)
        if self.char_mp < mp_cost:
            return {"success": False, "error": f"Not enough MP (need {mp_cost}, have {self.char_mp})"}
        
        # Check tactics cost (for warrior skills)
        tactics_cost = skill.effects.get("tactics_cost", {})
        for tactic_type_str, cost in tactics_cost.items():
            try:
                tactic_type = TacticType(tactic_type_str)
                if not self.tactics.use_tactic(tactic_type, cost):
                    return {"success": False, "error": f"Not enough {tactic_type_str} tactics (need {cost})"}
            except ValueError:
                return {"success": False, "error": f"Invalid tactic type: {tactic_type_str}"}
        
        # Use MP
        self.char_mp -= mp_cost
        
        # Apply skill effects
        result = self._apply_skill_effects(skill)
        
        # Check if skill consumes turn
        consumes_turn = skill.effects.get("consumes_turn", True)
        if not consumes_turn:
            # Skill doesn't consume turn, can act again
            self.current_turn.action_taken = False
        
        return result
    
    def _apply_skill_effects(self, skill: Skill) -> Dict[str, Any]:
        """Apply skill effects."""
        effects = skill.effects
        result = {
            "success": True,
            "action": "skill",
            "skill_name": skill.name,
            "message": f"Использован навык: {skill.name}"
        }
        
        # Damage
        if "damage" in effects:
            damage = effects["damage"]
            if "damage_multiplier" in effects:
                damage_range = self.char_stats["physical_damage"]
                base = (damage_range["min"] + damage_range["max"]) // 2
                damage = int(base * effects["damage_multiplier"])
            
            final_damage = apply_physical_damage(damage, self.monster.physical_defense)
            self.monster_hp = max(0, self.monster_hp - final_damage)
            self.monster.current_hp = self.monster_hp
            result["damage"] = final_damage
            result["monster_hp"] = self.monster_hp
        
        # Magical damage
        if "magical_damage" in effects:
            damage = effects["magical_damage"]
            final_damage = apply_magical_damage(damage, self.monster.magical_defense)
            self.monster_hp = max(0, self.monster_hp - final_damage)
            self.monster.current_hp = self.monster_hp
            result["magical_damage"] = final_damage
            result["monster_hp"] = self.monster_hp
        
        # Heal
        if "heal" in effects:
            heal_amount = effects["heal"]
            self.char_hp = min(self.char_max_hp, self.char_hp + heal_amount)
            result["heal"] = heal_amount
            result["character_hp"] = self.char_hp
        
        self.db.commit()
        return result
    
    def monster_attack(self) -> Dict[str, Any]:
        """Monster attacks."""
        if not self.current_turn or self.current_turn.actor_type != "monster":
            return {"error": "Not monster's turn"}
        
        # Calculate damage
        base_damage = random.randint(
            self.monster.physical_damage_min,
            self.monster.physical_damage_max
        )
        
        # Apply character defense
        final_damage = apply_physical_damage(base_damage, self.char_stats["physical_defense"])
        self.char_hp = max(0, self.char_hp - final_damage)
        
        self.current_turn.action_taken = True
        self.current_turn.action_type = "attack"
        
        return {
            "success": True,
            "damage": final_damage,
            "character_hp": self.char_hp,
            "character_max_hp": self.char_max_hp,
            "message": f"{self.monster.name} нанес {final_damage} урона"
        }
    
    def end_turn(self) -> Dict[str, Any]:
        """End current turn and start next."""
        if not self.current_turn:
            return {"error": "No active turn"}
        
        # Switch turns
        if self.current_turn.actor_type == "character":
            self._start_monster_turn()
        else:
            self._start_character_turn()
        
        return {
            "success": True,
            "next_turn": self.current_turn.actor_type,
            "turn_time": self.current_turn.time_limit
        }
    
    def get_combat_state(self) -> Dict[str, Any]:
        """Get current combat state."""
        time_remaining = 0
        if self.current_turn:
            time_remaining = self.current_turn.time_remaining()
        
        return {
            "turn_number": self.turn_number,
            "current_turn": self.current_turn.actor_type if self.current_turn else None,
            "time_remaining": time_remaining,
            "character_hp": self.char_hp,
            "character_max_hp": self.char_max_hp,
            "character_mp": self.char_mp,
            "character_max_mp": self.char_max_mp,
            "monster_hp": self.monster_hp,
            "monster_max_hp": self.monster.max_hp,
            "tactics": self.tactics.get_all_tactics(),
            "combat_log": self.combat_log[-10:]  # Last 10 entries
        }
    
    def is_combat_over(self) -> bool:
        """Check if combat is over."""
        return self.char_hp <= 0 or self.monster_hp <= 0
    
    def get_winner(self) -> Optional[str]:
        """Get combat winner."""
        if self.char_hp <= 0:
            return "monster"
        elif self.monster_hp <= 0:
            return "character"
        return None
