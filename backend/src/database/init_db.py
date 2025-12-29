"""Initialize database."""

from backend.src.database.base import Base, engine, SessionLocal
# Import all models to register them
from backend.src.models import (
    Player, Character, Item, InventorySlot, EquipmentSlot,
    MarketOrder, Location, Monster, Skill, CharacterSkill,
    DropTable, DropTableItem, ItemRarity, ItemType, CharacterClass, SkillType
)
import json
from pathlib import Path


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")
    
    # Create test data
    create_test_data()


def create_test_data():
    """Create test data for development."""
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(Character).first():
            print("Test data already exists, skipping...")
            return
        
        print("Creating test data...")
        
        # Create test player
        # Simple hash for testing (in production use proper hashing)
        import hashlib
        password_hash = hashlib.sha256("test123".encode()).hexdigest()
        
        test_player = Player(
            username="test_player",
            email="test@example.com",
            password_hash=password_hash,
            is_active=True
        )
        db.add(test_player)
        db.flush()
        
        # Create test location
        test_location = Location(
            name="Гнилостные Топи",
            description="Воздух густ от запаха гнили и болотного газа.",
            connected_locations=[2],
            travel_time=5
        )
        db.add(test_location)
        db.flush()
        
        # Create test character
        test_character = Character(
            player_id=test_player.id,
            name="Тестовый Герой",
            level=1,
            experience=0,
            strength=10,
            agility=10,
            intelligence=10,
            endurance=10,
            wisdom=10,
            luck=10,
            character_class=CharacterClass.ADVENTURER,
            location_id=test_location.id
        )
        db.add(test_character)
        db.flush()
        
        # Create test items
        test_items = [
            Item(
                name="Ржавый меч",
                description="Старый, заржавевший меч.",
                rarity=ItemRarity.COMMON,
                item_type=ItemType.WEAPON,
                physical_damage=3,
                is_tradable=True,
                stack_size=1
            ),
            Item(
                name="Кожаная броня",
                description="Простая кожаная броня.",
                rarity=ItemRarity.COMMON,
                item_type=ItemType.CHEST,
                physical_defense=2,
                is_tradable=True,
                stack_size=1
            ),
        ]
        for item in test_items:
            db.add(item)
        db.flush()
        
        # Create test monster
        test_monster = Monster(
            name="Гниющий тролль",
            level=3,
            location_id=test_location.id,
            max_hp=80,
            current_hp=80,
            strength=12,
            agility=8,
            intelligence=5,
            endurance=10,
            wisdom=6,
            physical_damage_min=8,
            physical_damage_max=15,
            physical_defense=5,
            magical_defense=3,
            speed=9,
            special_abilities=["poison"]
        )
        db.add(test_monster)
        db.flush()
        
        # Create test skills
        test_skills = [
            Skill(
                name="Базовый удар",
                description="Обычная физическая атака.",
                skill_type=SkillType.ATTACK,
                required_level=1,
                effects={"damage_multiplier": 1.0, "mp_cost": 0, "consumes_turn": True}
            ),
            Skill(
                name="Быстрая атака",
                description="Быстрая атака, не расходующая ход.",
                skill_type=SkillType.ATTACK,
                required_level=3,
                required_strength=10,
                required_agility=12,
                allowed_classes=["bone_knight", "adventurer"],
                effects={
                    "damage_multiplier": 0.8,
                    "mp_cost": 3,
                    "tactics_cost": {"attack": 1},
                    "consumes_turn": False
                }
            ),
        ]
        for skill in test_skills:
            db.add(skill)
        db.flush()
        
        # Learn first skill
        char_skill = CharacterSkill(
            character_id=test_character.id,
            skill_id=test_skills[0].id,
            is_selected=1,
            learned_at_level=1
        )
        db.add(char_skill)
        
        db.commit()
        print("Test data created successfully!")
        print(f"  Player ID: {test_player.id}")
        print(f"  Character ID: {test_character.id}")
        print(f"  Location ID: {test_location.id}")
        
    except Exception as e:
        print(f"Error creating test data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
