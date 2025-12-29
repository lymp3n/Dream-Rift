"""Skill model."""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from backend.src.database.base import Base
import enum


class SkillType(str, enum.Enum):
    """Skill type enum."""
    ATTACK = "attack"
    DEFENSE = "defense"
    HEAL = "heal"
    BUFF = "buff"
    DEBUFF = "debuff"


class Skill(Base):
    """Skill model."""
    
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    description = Column(Text)
    skill_type = Column(SQLEnum(SkillType), nullable=False)
    
    # Requirements
    required_level = Column(Integer, default=1, nullable=False)
    required_strength = Column(Integer, default=0)
    required_agility = Column(Integer, default=0)
    required_intelligence = Column(Integer, default=0)
    required_endurance = Column(Integer, default=0)
    required_wisdom = Column(Integer, default=0)
    
    # Class restrictions (JSON array of allowed classes)
    allowed_classes = Column(JSON, default=[])  # ["bone_knight", "void_mage", ...] or [] for all
    
    # Skill effects (stored as JSON)
    effects = Column(JSON, default={})  # {"damage": 20, "heal": 10, "mp_cost": 15, ...}
    
    # Relationships
    character_skills = relationship("CharacterSkill", back_populates="skill")


class CharacterSkill(Base):
    """Character skill relationship."""
    
    __tablename__ = "character_skills"
    
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    is_selected = Column(Integer, default=0)  # 0 = not selected, 1-6 = slot number
    learned_at_level = Column(Integer, nullable=False)
    
    # Relationships
    character = relationship("Character", back_populates="skills")
    skill = relationship("Skill", back_populates="character_skills")

