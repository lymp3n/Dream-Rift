"""Market order model."""

from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLEnum, DateTime, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.src.database.base import Base
import enum


class OrderType(str, enum.Enum):
    """Order type enum."""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, enum.Enum):
    """Order status enum."""
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    PARTIAL = "partial"


class MarketOrder(Base):
    """Market order model."""
    
    __tablename__ = "market_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    
    order_type = Column(SQLEnum(OrderType), nullable=False)
    status = Column(SQLEnum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    
    price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    filled_quantity = Column(Integer, default=0, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    character = relationship("Character")
    item = relationship("Item")

