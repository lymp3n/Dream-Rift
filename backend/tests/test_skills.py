"""Tests for skills system."""

import pytest


def test_skill_requirements():
    """Test skill requirement structure."""
    skill_data = {
        "required_level": 5,
        "required_strength": 15,
        "required_agility": 0,
        "required_intelligence": 0,
        "required_endurance": 0,
        "required_wisdom": 0,
        "allowed_classes": ["bone_knight"]
    }
    
    assert skill_data["required_level"] == 5
    assert skill_data["required_strength"] == 15
    assert "allowed_classes" in skill_data

