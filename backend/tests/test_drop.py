"""Tests for drop system."""

import pytest
from backend.src.core.drop import calculate_drop_chance


def test_calculate_drop_chance():
    """Test drop chance calculation with LUK."""
    base_chance = 0.001  # 0.1%
    
    # No LUK
    chance = calculate_drop_chance(base_chance, 0)
    assert chance == 0.001
    
    # 10 LUK
    chance = calculate_drop_chance(base_chance, 10)
    assert chance == 0.001 + (10 * 0.0001)  # 0.002
    
    # 100 LUK
    chance = calculate_drop_chance(base_chance, 100)
    assert chance == 0.001 + (100 * 0.0001)  # 0.011
    
    # Cap at 1.0
    chance = calculate_drop_chance(0.99, 1000)
    assert chance <= 1.0

