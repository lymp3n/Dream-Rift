"""Character model."""

from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from backend.src.database.base import Base
import enum


class CharacterClass(str, enum.Enum):
    """Character class enum."""
    BONE_KNIGHT = "bone_knight"
    VOID_MAGE = "void_mage"
    DREAM_WALKER = "dream_walker"
    ADVENTURER = "adventurer"


class Character(Base):
    """Character model."""
    
    __tablename__ = "characters"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    name = Column(String, nullable=False, index=True)
    level = Column(Integer, default=1, nullable=False)
    experience = Column(Integer, default=0, nullable=False)
    
    # Base stats
    strength = Column(Integer, default=10, nullable=False)
    agility = Column(Integer, default=10, nullable=False)
    intelligence = Column(Integer, default=10, nullable=False)
    endurance = Column(Integer, default=10, nullable=False)
    wisdom = Column(Integer, default=10, nullable=False)
    luck = Column(Integer, default=10, nullable=False)
    
    # Class
    character_class = Column(SQLEnum(CharacterClass), nullable=False, default=CharacterClass.ADVENTURER)
    
    # Current location
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    
    # Relationships
    player = relationship("Player", back_populates="characters")
    location = relationship("Location", foreign_keys=[location_id])
    inventory_slots = relationship("InventorySlot", back_populates="character", cascade="all, delete-orphan")
    equipment = relationship("EquipmentSlot", back_populates="character", cascade="all, delete-orphan", uselist=False)
    skills = relationship("CharacterSkill", back_populates="character", cascade="all, delete-orphan")

