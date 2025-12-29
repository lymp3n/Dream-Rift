"""Market API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.src.database.base import get_db
from backend.src.models import Character, OrderType, OrderStatus
from backend.src.api.schemas.market import MarketOrderCreate, MarketOrderResponse
from backend.src.core.market import create_order, get_market_orders, cancel_order

router = APIRouter(prefix="/market", tags=["market"])


@router.post("/orders", response_model=MarketOrderResponse)
def create_market_order(order: MarketOrderCreate, db: Session = Depends(get_db)):
    """Create a market order."""
    try:
        order_type = OrderType(order.order_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid order type")
    
    character = db.query(Character).filter(Character.id == order.character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    result = create_order(character, order.item_id, order_type, order.price, order.quantity, db)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("reason", "Failed to create order"))
    
    # Get created order
    from backend.src.models import MarketOrder
    created_order = db.query(MarketOrder).filter(MarketOrder.id == result["order_id"]).first()
    return created_order


@router.get("/orders")
def get_orders(item_id: int = None, order_type: str = None, status: str = None, db: Session = Depends(get_db)):
    """Get market orders with filters."""
    order_type_enum = None
    if order_type:
        try:
            order_type_enum = OrderType(order_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid order type")
    
    status_enum = None
    if status:
        try:
            status_enum = OrderStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
    
    return get_market_orders(item_id, order_type_enum, status_enum, db)


@router.delete("/orders/{order_id}")
def cancel_market_order(order_id: int, character_id: int, db: Session = Depends(get_db)):
    """Cancel a market order."""
    result = cancel_order(order_id, character_id, db)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("reason", "Failed to cancel order"))
    return result

