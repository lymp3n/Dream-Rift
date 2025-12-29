"""Task definitions for agents."""

TASKS = {
    "architect": {
        "description": "Create project structure, database schema, component diagrams, and configure dependencies",
        "files": [
            "backend/src/core/__init__.py",
            "backend/src/models/__init__.py",
            "backend/src/api/__init__.py",
            "backend/src/database/__init__.py",
            "backend/src/utils/__init__.py",
            "frontend/cli/__init__.py",
        ],
        "configs": [
            "backend/requirements.txt",
            "frontend/requirements.txt",
            "backend/alembic.ini",
        ]
    },
    "backend": {
        "description": "Implement all core systems: combat, drop (Core/Shell), crafting, market, classes, skills, locations",
        "systems": [
            "combat",
            "drop",
            "crafting",
            "market",
            "character",
            "skills",
            "location",
            "inventory"
        ]
    },
    "gamedesign": {
        "description": "Calculate balance, formulas, drop probabilities, and create all configuration JSON files",
        "configs": [
            "balance.json",
            "items.json",
            "monsters.json",
            "locations.json",
            "skills.json",
            "drop_tables.json",
            "crafting_recipes.json",
            "classes.json"
        ]
    },
    "frontend": {
        "description": "Create CLI interface simulating mobile UI with panels, menus, navigation",
        "components": [
            "main",
            "commands",
            "display",
            "panels",
            "navigation",
            "api_client"
        ]
    },
    "tester": {
        "description": "Write unit and integration tests for all mechanics",
        "tests": [
            "test_combat",
            "test_drop",
            "test_crafting",
            "test_market",
            "test_character",
            "test_skills",
            "test_api",
            "test_cli"
        ]
    },
    "documenter": {
        "description": "Create complete documentation: architecture, API, gameplay, formulas, README",
        "docs": [
            "architecture.md",
            "api.md",
            "gameplay.md",
            "formulas.md",
            "database_schema.md"
        ]
    }
}

