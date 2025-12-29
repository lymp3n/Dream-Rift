"""Monster model."""

from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.src.database.base import Base


class Monster(Base):
    """Monster model."""
    
    __tablename__ = "monsters"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    level = Column(Integer, nullable=False, default=1)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    
    # Base stats
    max_hp = Column(Integer, nullable=False)
    current_hp = Column(Integer, nullable=False)
    strength = Column(Integer, default=10, nullable=False)
    agility = Column(Integer, default=10, nullable=False)
    intelligence = Column(Integer, default=10, nullable=False)
    endurance = Column(Integer, default=10, nullable=False)
    wisdom = Column(Integer, default=10, nullable=False)
    
    # Combat stats (calculated or set)
    physical_damage_min = Column(Integer, default=0)
    physical_damage_max = Column(Integer, default=0)
    magical_damage_min = Column(Integer, default=0)
    magical_damage_max = Column(Integer, default=0)
    physical_defense = Column(Integer, default=0)
    magical_defense = Column(Integer, default=0)  # Percentage
    speed = Column(Integer, default=10)
    
    # Special abilities (stored as JSON)
    special_abilities = Column(JSON, default=[])  # ["poison", "stun", ...]
    
    # Relationships
    location = relationship("Location", back_populates="monsters")
    drop_table = relationship("DropTable", back_populates="monster", uselist=False)

