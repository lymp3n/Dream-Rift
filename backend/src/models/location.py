"""Location model."""

from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
from backend.src.database.base import Base


class Location(Base):
    """Location model."""
    
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    description = Column(Text, nullable=False)
    
    # Connected locations (stored as JSON array of location IDs)
    connected_locations = Column(JSON, default=[])  # [1, 2, 3]
    
    # Travel time in seconds
    travel_time = Column(Integer, default=5, nullable=False)
    
    # Relationships
    monsters = relationship("Monster", back_populates="location")
    characters = relationship("Character", foreign_keys="Character.location_id", overlaps="location")

