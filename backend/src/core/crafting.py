"""Crafting system for legendary items."""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.src.models import Character, Item, InventorySlot


def check_crafting_recipe(character: Character, recipe: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """Check if character has required ingredients for recipe.
    
    Recipe format:
    {
        "result_item_id": int,
        "core_item_id": int,  # Required: 1x Core (Soul-Bound)
        "shell_items": [{"item_id": int, "quantity": int}],  # Required: Nx Shells
        "other_items": [{"item_id": int, "quantity": int}]  # Optional other materials
    }
    """
    # Get character inventory
    inventory = db.query(InventorySlot).filter(
        InventorySlot.character_id == character.id
    ).all()
    
    # Check for Core (must be exactly 1, and character must own it)
    core_required = recipe.get("core_item_id")
    if core_required:
        core_found = False
        for slot in inventory:
            if slot.item_id == core_required:
                core_item = db.query(Item).filter(Item.id == core_required).first()
                if core_item and core_item.is_soul_bound:
                    if slot.quantity >= 1:
                        core_found = True
                        break
        
        if not core_found:
            return {
                "can_craft": False,
                "reason": "Отсутствует требуемая Сердцевина (Soul-Bound)"
            }
    
    # Check for Shell items
    shell_requirements = recipe.get("shell_items", [])
    missing_shells = []
    for shell_req in shell_requirements:
        required_id = shell_req["item_id"]
        required_qty = shell_req["quantity"]
        
        found_qty = 0
        for slot in inventory:
            if slot.item_id == required_id:
                found_qty += slot.quantity
        
        if found_qty < required_qty:
            shell_item = db.query(Item).filter(Item.id == required_id).first()
            missing_shells.append({
                "item": shell_item.name if shell_item else f"Item {required_id}",
                "required": required_qty,
                "have": found_qty
            })
    
    if missing_shells:
        return {
            "can_craft": False,
            "reason": "Недостаточно Оболочек",
            "missing": missing_shells
        }
    
    # Check for other items (optional)
    other_requirements = recipe.get("other_items", [])
    missing_other = []
    for other_req in other_requirements:
        required_id = other_req["item_id"]
        required_qty = other_req["quantity"]
        
        found_qty = 0
        for slot in inventory:
            if slot.item_id == required_id:
                found_qty += slot.quantity
        
        if found_qty < required_qty:
            other_item = db.query(Item).filter(Item.id == required_id).first()
            missing_other.append({
                "item": other_item.name if other_item else f"Item {required_id}",
                "required": required_qty,
                "have": found_qty
            })
    
    if missing_other:
        return {
            "can_craft": False,
            "reason": "Недостаточно материалов",
            "missing": missing_other
        }
    
    return {
        "can_craft": True,
        "message": "Все ингредиенты в наличии"
    }


def craft_item(character: Character, recipe: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """Craft item from recipe.
    
    Removes ingredients and adds result to inventory.
    """
    # Check if can craft
    check_result = check_crafting_recipe(character, recipe, db)
    if not check_result["can_craft"]:
        return check_result
    
    inventory = db.query(InventorySlot).filter(
        InventorySlot.character_id == character.id
    ).all()
    
    # Remove Core (1x)
    core_id = recipe.get("core_item_id")
    if core_id:
        for slot in inventory:
            if slot.item_id == core_id:
                slot.quantity -= 1
                if slot.quantity <= 0:
                    db.delete(slot)
                break
    
    # Remove Shell items
    shell_requirements = recipe.get("shell_items", [])
    for shell_req in shell_requirements:
        required_id = shell_req["item_id"]
        required_qty = shell_req["quantity"]
        
        remaining = required_qty
        for slot in inventory:
            if slot.item_id == required_id and remaining > 0:
                if slot.quantity <= remaining:
                    remaining -= slot.quantity
                    db.delete(slot)
                else:
                    slot.quantity -= remaining
                    remaining = 0
    
    # Remove other items
    other_requirements = recipe.get("other_items", [])
    for other_req in other_requirements:
        required_id = other_req["item_id"]
        required_qty = other_req["quantity"]
        
        remaining = required_qty
        for slot in inventory:
            if slot.item_id == required_id and remaining > 0:
                if slot.quantity <= remaining:
                    remaining -= slot.quantity
                    db.delete(slot)
                else:
                    slot.quantity -= remaining
                    remaining = 0
    
    # Add result item to inventory
    result_item_id = recipe["result_item_id"]
    result_item = db.query(Item).filter(Item.id == result_item_id).first()
    
    if not result_item:
        db.rollback()
        return {
            "success": False,
            "reason": "Результат крафта не найден"
        }
    
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
    
    # Create new inventory slot
    new_slot = InventorySlot(
        character_id=character.id,
        item_id=result_item_id,
        quantity=1,
        slot_index=slot_index
    )
    db.add(new_slot)
    
    db.commit()
    
    return {
        "success": True,
        "item": result_item.name,
        "message": f"Успешно создан: {result_item.name}"
    }

