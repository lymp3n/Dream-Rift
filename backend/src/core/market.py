"""Market system with order matching."""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from backend.src.models import MarketOrder, OrderType, OrderStatus, Character, Item, InventorySlot


def create_order(
    character: Character,
    item_id: int,
    order_type: OrderType,
    price: float,
    quantity: int,
    db: Session
) -> Dict[str, Any]:
    """Create a market order."""
    
    # Validate item exists
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return {
            "success": False,
            "reason": "Предмет не найден"
        }
    
    # For sell orders, check inventory
    if order_type == OrderType.SELL:
        inventory_qty = db.query(InventorySlot).filter(
            and_(
                InventorySlot.character_id == character.id,
                InventorySlot.item_id == item_id
            )
        ).with_entities(
            db.func.sum(InventorySlot.quantity)
        ).scalar() or 0
        
        if inventory_qty < quantity:
            return {
                "success": False,
                "reason": f"Недостаточно предметов в инвентаре (есть: {inventory_qty}, требуется: {quantity})"
            }
        
        # Check if item is tradable
        if not item.is_tradable:
            return {
                "success": False,
                "reason": "Предмет нельзя продать (Soul-Bound)"
            }
    
    # Create order
    order = MarketOrder(
        character_id=character.id,
        item_id=item_id,
        order_type=order_type,
        status=OrderStatus.PENDING,
        price=price,
        quantity=quantity,
        filled_quantity=0
    )
    db.add(order)
    db.commit()
    
    # Try to match immediately
    match_result = try_match_order(order.id, db)
    
    return {
        "success": True,
        "order_id": order.id,
        "matched": match_result["matched"],
        "message": f"Ордер создан. {'Сразу сопоставлен!' if match_result['matched'] else 'Ожидает сопоставления.'}"
    }


def try_match_order(order_id: int, db: Session) -> Dict[str, Any]:
    """Try to match an order with existing orders."""
    order = db.query(MarketOrder).filter(MarketOrder.id == order_id).first()
    if not order or order.status != OrderStatus.PENDING:
        return {"matched": False}
    
    # Find matching orders (opposite type, same item, compatible price)
    if order.order_type == OrderType.BUY:
        # Looking for SELL orders with price <= buy order price
        matching_orders = db.query(MarketOrder).filter(
            and_(
                MarketOrder.order_type == OrderType.SELL,
                MarketOrder.item_id == order.item_id,
                MarketOrder.status == OrderStatus.PENDING,
                MarketOrder.price <= order.price,
                MarketOrder.character_id != order.character_id  # Can't match with self
            )
        ).order_by(MarketOrder.price.asc()).all()  # Cheapest first
    else:
        # Looking for BUY orders with price >= sell order price
        matching_orders = db.query(MarketOrder).filter(
            and_(
                MarketOrder.order_type == OrderType.BUY,
                MarketOrder.item_id == order.item_id,
                MarketOrder.status == OrderStatus.PENDING,
                MarketOrder.price >= order.price,
                MarketOrder.character_id != order.character_id
            )
        ).order_by(MarketOrder.price.desc()).all()  # Most expensive first
    
    remaining_qty = order.quantity - order.filled_quantity
    matched = False
    
    for match_order in matching_orders:
        if remaining_qty <= 0:
            break
        
        match_remaining = match_order.quantity - match_order.filled_quantity
        if match_remaining <= 0:
            continue
        
        # Determine trade quantity
        trade_qty = min(remaining_qty, match_remaining)
        trade_price = match_order.price  # Use the matched order's price
        
        # Execute trade
        execute_trade(order, match_order, trade_qty, trade_price, db)
        matched = True
        
        remaining_qty -= trade_qty
    
    # Update order status
    if order.filled_quantity >= order.quantity:
        order.status = OrderStatus.FILLED
    elif order.filled_quantity > 0:
        order.status = OrderStatus.PARTIAL
    
    db.commit()
    
    return {"matched": matched}


def execute_trade(
    buy_order: MarketOrder,
    sell_order: MarketOrder,
    quantity: int,
    price: float,
    db: Session
):
    """Execute a trade between two orders."""
    # This is simplified - in real implementation, we'd need to:
    # 1. Transfer items from seller to buyer
    # 2. Transfer gold from buyer to seller
    # 3. Update order filled quantities
    # 4. Handle partial fills
    
    # For now, just update filled quantities
    buy_order.filled_quantity += quantity
    sell_order.filled_quantity += quantity
    
    # Update statuses
    if buy_order.filled_quantity >= buy_order.quantity:
        buy_order.status = OrderStatus.FILLED
    if sell_order.filled_quantity >= sell_order.quantity:
        sell_order.status = OrderStatus.FILLED


def get_market_orders(
    item_id: Optional[int] = None,
    order_type: Optional[OrderType] = None,
    status: Optional[OrderStatus] = None,
    db: Session = None
) -> List[Dict[str, Any]]:
    """Get market orders with filters."""
    query = db.query(MarketOrder)
    
    if item_id:
        query = query.filter(MarketOrder.item_id == item_id)
    if order_type:
        query = query.filter(MarketOrder.order_type == order_type)
    if status:
        query = query.filter(MarketOrder.status == status)
    
    orders = query.order_by(MarketOrder.created_at.desc()).all()
    
    return [
        {
            "id": order.id,
            "character_id": order.character_id,
            "item_id": order.item_id,
            "order_type": order.order_type.value,
            "status": order.status.value,
            "price": float(order.price),
            "quantity": order.quantity,
            "filled_quantity": order.filled_quantity,
            "created_at": order.created_at.isoformat() if order.created_at else None,
        }
        for order in orders
    ]


def cancel_order(order_id: int, character_id: int, db: Session) -> Dict[str, Any]:
    """Cancel a market order."""
    order = db.query(MarketOrder).filter(
        and_(
            MarketOrder.id == order_id,
            MarketOrder.character_id == character_id
        )
    ).first()
    
    if not order:
        return {
            "success": False,
            "reason": "Ордер не найден"
        }
    
    if order.status != OrderStatus.PENDING:
        return {
            "success": False,
            "reason": "Можно отменить только ожидающие ордера"
        }
    
    order.status = OrderStatus.CANCELLED
    db.commit()
    
    return {
        "success": True,
        "message": "Ордер отменен"
    }

