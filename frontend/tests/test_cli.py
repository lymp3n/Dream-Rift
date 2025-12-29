"""Tests for CLI interface."""

import pytest
from frontend.cli.navigation import parse_command


def test_parse_command():
    """Test command parsing."""
    cmd, args = parse_command("attack 1")
    assert cmd == "attack"
    assert args == ["1"]
    
    cmd, args = parse_command("travel 5")
    assert cmd == "travel"
    assert args == ["5"]
    
    cmd, args = parse_command("menu")
    assert cmd == "menu"
    assert args == []

