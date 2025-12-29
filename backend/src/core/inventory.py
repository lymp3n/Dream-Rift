"""Inventory and equipment system."""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.src.models import Character, Item, InventorySlot, EquipmentSlot


def get_inventory(character: Character, db: Session) -> Dict[str, Any]:
    """Get character inventory."""
    slots = db.query(InventorySlot).filter(
        InventorySlot.character_id == character.id
    ).order_by(InventorySlot.slot_index).all()
    
    max_slots = 30  # 6x5 grid
    inventory_grid = [None] * max_slots
    
    for slot in slots:
        if 0 <= slot.slot_index < max_slots:
            inventory_grid[slot.slot_index] = {
                "id": slot.id,
                "item_id": slot.item_id,
                "item": {
                    "id": slot.item.id,
                    "name": slot.item.name,
                    "rarity": slot.item.rarity.value,
                    "item_type": slot.item.item_type.value,
                },
                "quantity": slot.quantity,
            }
    
    return {
        "slots": inventory_grid,
        "used_slots": len([s for s in inventory_grid if s is not None]),
        "max_slots": max_slots,
    }


def get_equipment(character: Character, db: Session) -> Dict[str, Any]:
    """Get character equipment."""
    equipment = character.equipment
    if not equipment:
        # Create empty equipment slot
        equipment = EquipmentSlot(character_id=character.id)
        db.add(equipment)
        db.commit()
        db.refresh(equipment)
    
    slots = {
        "helmet": equipment.helmet_id,
        "chest": equipment.chest_id,
        "belt": equipment.belt_id,
        "legs": equipment.legs_id,
        "boots": equipment.boots_id,
        "weapon": equipment.weapon_id,
        "accessory1": equipment.accessory1_id,
        "accessory2": equipment.accessory2_id,
    }
    
    # Get item details
    equipped_items = {}
    for slot_name, item_id in slots.items():
        if item_id:
            item = db.query(Item).filter(Item.id == item_id).first()
            if item:
                equipped_items[slot_name] = {
                    "id": item.id,
                    "name": item.name,
                    "rarity": item.rarity.value,
                    "stat_bonuses": item.stat_bonuses or {},
                }
        else:
            equipped_items[slot_name] = None
    
    return equipped_items


def equip_item(character: Character, item_id: int, db: Session) -> Dict[str, Any]:
    """Equip an item."""
    # Check if item is in inventory
    inventory_slot = db.query(InventorySlot).filter(
        InventorySlot.character_id == character.id,
        InventorySlot.item_id == item_id
    ).first()
    
    if not inventory_slot:
        return {
            "success": False,
            "reason": "Предмет не найден в инвентаре"
        }
    
    item = inventory_slot.item
    
    # Determine equipment slot based on item type
    slot_mapping = {
        "helmet": "helmet_id",
        "chest": "chest_id",
        "belt": "belt_id",
        "legs": "legs_id",
        "boots": "boots_id",
        "weapon": "weapon_id",
        "accessory": "accessory1_id",  # Default to accessory1
    }
    
    item_type = item.item_type.value
    if item_type not in slot_mapping:
        return {
            "success": False,
            "reason": f"Предмет типа '{item_type}' нельзя надеть"
        }
    
    # Get or create equipment slot
    equipment = character.equipment
    if not equipment:
        equipment = EquipmentSlot(character_id=character.id)
        db.add(equipment)
        db.commit()
        db.refresh(equipment)
    
    # Handle accessories specially
    if item_type == "accessory":
        if not equipment.accessory1_id:
            slot_name = "accessory1_id"
        elif not equipment.accessory2_id:
            slot_name = "accessory2_id"
        else:
            return {
                "success": False,
                "reason": "Оба слота аксессуаров заняты"
            }
    else:
        slot_name = slot_mapping[item_type]
    
    # Unequip existing item if any
    existing_item_id = getattr(equipment, slot_name)
    if existing_item_id:
        # Add existing item back to inventory
        unequip_item(character, slot_name, db)
    
    # Equip new item
    setattr(equipment, slot_name, item_id)
    
    # Remove from inventory
    inventory_slot.quantity -= 1
    if inventory_slot.quantity <= 0:
        db.delete(inventory_slot)
    
    db.commit()
    
    return {
        "success": True,
        "item": item.name,
        "slot": slot_name.replace("_id", ""),
        "message": f"Надето: {item.name}"
    }


def unequip_item(character: Character, slot_name: str, db: Session) -> Dict[str, Any]:
    """Unequip an item."""
    equipment = character.equipment
    if not equipment:
        return {
            "success": False,
            "reason": "Нет экипировки"
        }
    
    full_slot_name = f"{slot_name}_id" if not slot_name.endswith("_id") else slot_name
    item_id = getattr(equipment, full_slot_name, None)
    
    if not item_id:
        return {
            "success": False,
            "reason": "Слот пуст"
        }
    
    # Clear slot
    setattr(equipment, full_slot_name, None)
    
    # Add item back to inventory
    # Find empty slot
    max_slots = 30
    existing_slots = db.query(InventorySlot).filter(
        InventorySlot.character_id == character.id
    ).all()
    used_indices = {slot.slot_index for slot in existing_slots}
    
    slot_index = None
    for i in range(max_slots):
        if i not in used_indices:
            slot_index = i
            break
    
    if slot_index is None:
        db.rollback()
        return {
            "success": False,
            "reason": "Инвентарь переполнен"
        }
    
    # Create inventory slot
    new_slot = InventorySlot(
        character_id=character.id,
        item_id=item_id,
        quantity=1,
        slot_index=slot_index
    )
    db.add(new_slot)
    
    db.commit()
    
    item = db.query(Item).filter(Item.id == item_id).first()
    return {
        "success": True,
        "item": item.name if item else "Unknown",
        "message": f"Снято: {item.name if item else 'Unknown'}"
    }

