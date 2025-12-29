"""Drop table models."""

from sqlalchemy import Column, Integer, String, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from backend.src.database.base import Base


class DropTable(Base):
    """Drop table model."""
    
    __tablename__ = "drop_tables"
    
    id = Column(Integer, primary_key=True, index=True)
    monster_id = Column(Integer, ForeignKey("monsters.id"), nullable=False, unique=True)
    name = Column(String, nullable=False)
    
    # Relationships
    monster = relationship("Monster", back_populates="drop_table")
    items = relationship("DropTableItem", back_populates="drop_table", cascade="all, delete-orphan")


class DropTableItem(Base):
    """Drop table item model."""
    
    __tablename__ = "drop_table_items"
    
    id = Column(Integer, primary_key=True, index=True)
    drop_table_id = Column(Integer, ForeignKey("drop_tables.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    
    # Drop chance (0.0 to 1.0, e.g., 0.001 = 0.1%)
    drop_chance = Column(Numeric(5, 4), nullable=False)
    
    # Min and max quantity
    min_quantity = Column(Integer, default=1, nullable=False)
    max_quantity = Column(Integer, default=1, nullable=False)
    
    # Relationships
    drop_table = relationship("DropTable", back_populates="items")
    item = relationship("Item", back_populates="drop_table_items")

