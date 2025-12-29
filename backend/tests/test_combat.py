"""Tests for combat system."""

import pytest
from backend.src.core.combat import (
    calculate_max_hp,
    calculate_max_mp,
    calculate_physical_damage,
    calculate_magical_damage,
    calculate_physical_defense,
    calculate_magical_defense,
    calculate_crit_chance,
    calculate_crit_damage,
    apply_physical_damage,
    apply_magical_damage,
)


def test_calculate_max_hp():
    """Test HP calculation."""
    # Level 1, STR 10, END 10
    hp = calculate_max_hp(1, 10, 10)
    assert hp == 30 + 10 + 30 + 50  # 120
    
    # Level 10, STR 20, END 15
    hp = calculate_max_hp(10, 20, 15)
    assert hp == 30 + 100 + 60 + 75  # 265


def test_calculate_max_mp():
    """Test MP calculation."""
    # Level 1, INT 10, WIS 10
    mp = calculate_max_mp(1, 10, 10)
    assert mp == 20 + 5 + 40 + 20  # 85
    
    # Level 10, INT 20, WIS 15
    mp = calculate_max_mp(10, 20, 15)
    assert mp == 20 + 50 + 80 + 30  # 180


def test_calculate_physical_damage():
    """Test physical damage calculation."""
    damage = calculate_physical_damage(10, 0)
    assert damage["min"] > 0
    assert damage["max"] > damage["min"]
    assert damage["min"] <= int(20 * 0.85)
    assert damage["max"] >= int(20 * 1.15)


def test_calculate_magical_damage():
    """Test magical damage calculation."""
    damage = calculate_magical_damage(10, 0)
    assert damage["min"] > 0
    assert damage["max"] > damage["min"]
    assert damage["min"] <= int(18 * 0.9)
    assert damage["max"] >= int(18 * 1.1)


def test_calculate_physical_defense():
    """Test physical defense calculation."""
    defense = calculate_physical_defense(10, 0)
    assert defense == int(10 * 1.5)  # 15


def test_calculate_magical_defense():
    """Test magical defense calculation."""
    defense = calculate_magical_defense(10, 0)
    assert defense == float(10 * 0.8)  # 8.0


def test_calculate_crit_chance():
    """Test crit chance calculation."""
    crit = calculate_crit_chance(10, 10, 0)
    assert crit == float(10 * 0.1 + 10 * 0.05)  # 1.5%


def test_calculate_crit_damage():
    """Test crit damage calculation."""
    base = 100
    crit = calculate_crit_damage(base)
    assert crit == int(100 * 1.8)  # 180


def test_apply_physical_damage():
    """Test physical damage application."""
    damage = 50
    defense = 15
    result = apply_physical_damage(damage, defense)
    assert result == 35
    
    # Minimum 1 damage
    result = apply_physical_damage(10, 20)
    assert result == 1


def test_apply_magical_damage():
    """Test magical damage application."""
    damage = 50
    defense = 12  # 12% reduction
    result = apply_magical_damage(damage, defense)
    assert result == int(50 * (1 - 0.12))  # 44
    
    # Minimum 1 damage
    result = apply_magical_damage(10, 100)
    assert result == 1

