"""Item model."""

from sqlalchemy import Column, Integer, String, Enum as SQLEnum, JSON, Boolean
from sqlalchemy.orm import relationship
from backend.src.database.base import Base
import enum


class ItemRarity(str, enum.Enum):
    """Item rarity enum."""
    COMMON = "common"  # White
    UNCOMMON = "uncommon"  # Green
    RARE = "rare"  # Blue
    EPIC = "epic"  # Purple
    LEGENDARY = "legendary"  # Orange


class ItemType(str, enum.Enum):
    """Item type enum."""
    WEAPON = "weapon"
    HELMET = "helmet"
    CHEST = "chest"
    BELT = "belt"
    LEGS = "legs"
    BOOTS = "boots"
    ACCESSORY = "accessory"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    CORE = "core"  # Сердцевина
    SHELL = "shell"  # Оболочка


class Item(Base):
    """Item model."""
    
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String)
    rarity = Column(SQLEnum(ItemRarity), nullable=False, default=ItemRarity.COMMON)
    item_type = Column(SQLEnum(ItemType), nullable=False)
    
    # Stats bonuses (stored as JSON for flexibility)
    stat_bonuses = Column(JSON, default={})  # {"strength": 5, "agility": 2, ...}
    
    # Combat stats
    physical_damage = Column(Integer, default=0)
    magical_damage = Column(Integer, default=0)
    physical_defense = Column(Integer, default=0)
    magical_defense = Column(Integer, default=0)
    crit_chance_bonus = Column(Integer, default=0)  # Percentage
    speed_bonus = Column(Integer, default=0)
    
    # Special properties
    is_soul_bound = Column(Boolean, default=False)  # For Core items
    is_tradable = Column(Boolean, default=True)  # For Shell items, False for Core
    stack_size = Column(Integer, default=1)  # Max stack size
    
    # Relationships
    inventory_slots = relationship("InventorySlot", back_populates="item")
    drop_table_items = relationship("DropTableItem", back_populates="item")

