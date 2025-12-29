"""Quick test script."""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("Testing imports...")
try:
    from backend.src.database.base import Base, engine
    print("✓ Database base imported")
    
    from backend.src.models import Character, Player, Location
    print("✓ Models imported")
    
    from backend.src.database.init_db import init_db, create_test_data
    print("✓ Init DB imported")
    
    print("\nInitializing database...")
    init_db()
    
    print("\nCreating test data...")
    create_test_data()
    
    print("\n✓ All tests passed!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

