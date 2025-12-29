"""Tests for character system."""

import pytest
from backend.src.models import CharacterClass
from backend.src.core.character import get_class_stat_bonuses


def test_class_stat_bonuses():
    """Test class stat bonuses."""
    # Bone Knight
    bonuses = get_class_stat_bonuses(CharacterClass.BONE_KNIGHT, 2)
    assert bonuses["strength"] == 2  # (2-1) * 2
    assert bonuses["endurance"] == 2
    
    # Void Mage
    bonuses = get_class_stat_bonuses(CharacterClass.VOID_MAGE, 3)
    assert bonuses["intelligence"] == 6  # (3-1) * 3
    assert bonuses["wisdom"] == 2
    
    # Dream Walker
    bonuses = get_class_stat_bonuses(CharacterClass.DREAM_WALKER, 2)
    assert bonuses["intelligence"] == 1
    assert bonuses["wisdom"] == 1
    assert bonuses["luck"] == 1
    
    # Adventurer
    bonuses = get_class_stat_bonuses(CharacterClass.ADVENTURER, 2)
    assert bonuses["strength"] == 1
    assert bonuses["agility"] == 1
    assert bonuses["intelligence"] == 1
    assert bonuses["endurance"] == 1
    assert bonuses["wisdom"] == 1
    assert bonuses["luck"] == 1

