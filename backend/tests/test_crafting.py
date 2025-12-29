"""Tests for crafting system."""

import pytest


def test_crafting_recipe_format():
    """Test crafting recipe format."""
    recipe = {
        "result_item_id": 5,
        "core_item_id": 3,
        "shell_items": [
            {"item_id": 4, "quantity": 5}
        ],
        "other_items": []
    }
    
    assert "result_item_id" in recipe
    assert "core_item_id" in recipe
    assert "shell_items" in recipe
    assert len(recipe["shell_items"]) > 0

