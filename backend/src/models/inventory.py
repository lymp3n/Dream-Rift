"""Inventory models."""

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from backend.src.database.base import Base


class InventorySlot(Base):
    """Inventory slot model."""
    
    __tablename__ = "inventory_slots"
    
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    slot_index = Column(Integer, nullable=False)  # Position in inventory grid
    
    # Relationships
    character = relationship("Character", back_populates="inventory_slots")
    item = relationship("Item", back_populates="inventory_slots")


class EquipmentSlot(Base):
    """Equipment slot model."""
    
    __tablename__ = "equipment_slots"
    
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False, unique=True)
    
    # Equipment slots
    helmet_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    chest_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    belt_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    legs_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    boots_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    weapon_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    accessory1_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    accessory2_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    
    # Relationships
    character = relationship("Character", back_populates="equipment")

