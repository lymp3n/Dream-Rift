"""Test setup and data creation."""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path.cwd()))

from backend.src.database.base import SessionLocal
from backend.src.models import Character, Player, Location
from backend.src.database.init_db import create_test_data

def test_database():
    """Test database connection and data."""
    print("Testing database...")
    db = SessionLocal()
    try:
        # Check for characters
        characters = db.query(Character).all()
        print(f"Found {len(characters)} characters")
        
        for char in characters:
            print(f"  - {char.name} (ID: {char.id}, Level: {char.level})")
        
        # Check for locations
        locations = db.query(Location).all()
        print(f"Found {len(locations)} locations")
        
        for loc in locations:
            print(f"  - {loc.name} (ID: {loc.id})")
        
        if len(characters) == 0:
            print("No characters found, creating test data...")
            create_test_data()
        
        print("Database test passed!")
        return True
    except Exception as e:
        print(f"Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    test_database()

