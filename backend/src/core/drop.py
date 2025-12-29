"""Drop system with Core/Shell mechanics."""

import random
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.src.models import Monster, DropTable, DropTableItem, Item, Character, InventorySlot


def calculate_drop_chance(base_chance: float, luck: int) -> float:
    """Calculate drop chance with luck modifier.
    
    LUK increases drop chance slightly (1 LUK = 0.01% bonus).
    """
    luck_bonus = luck * 0.0001  # 0.01% per LUK point
    return min(1.0, base_chance + luck_bonus)


def roll_drop(monster: Monster, character: Character, db: Session) -> List[Dict[str, Any]]:
    """Roll for drops from monster.
    
    Returns list of dropped items with quantities.
    """
    if not monster.drop_table:
        return []
    
    drops = []
    drop_table = monster.drop_table
    
    # Roll for each item in drop table
    for drop_item in drop_table.items:
        # Calculate actual drop chance with LUK
        actual_chance = calculate_drop_chance(float(drop_item.drop_chance), character.luck)
        
        # Roll
        if random.random() < actual_chance:
            quantity = random.randint(drop_item.min_quantity, drop_item.max_quantity)
            drops.append({
                "item_id": drop_item.item_id,
                "item": drop_item.item,
                "quantity": quantity,
                "is_core": drop_item.item.is_soul_bound if drop_item.item else False,
                "is_shell": drop_item.item.item_type.value == "shell" if drop_item.item else False,
            })
    
    return drops


def add_drops_to_inventory(character: Character, drops: List[Dict[str, Any]], db: Session) -> Dict[str, Any]:
    """Add dropped items to character inventory.
    
    Returns summary of what was added.
    """
    added_items = []
    cores_found = []
    shells_found = []
    
    for drop in drops:
        item = drop["item"]
        quantity = drop["quantity"]
        
        # Check if item is stackable
        if item.stack_size > 1:
            # Try to find existing stack
            existing_slot = db.query(InventorySlot).filter(
                InventorySlot.character_id == character.id,
                InventorySlot.item_id == item.id
            ).first()
            
            if existing_slot:
                # Add to existing stack
                existing_slot.quantity += quantity
                added_items.append({
                    "item": item.name,
                    "quantity": quantity,
                    "action": "stacked"
                })
            else:
                # Create new slot
                # Find first empty slot
                max_slots = 30  # 6x5 grid
                existing_slots = db.query(InventorySlot).filter(
                    InventorySlot.character_id == character.id
                ).all()
                used_indices = {slot.slot_index for slot in existing_slots}
                
                for i in range(max_slots):
                    if i not in used_indices:
                        new_slot = InventorySlot(
                            character_id=character.id,
                            item_id=item.id,
                            quantity=quantity,
                            slot_index=i
                        )
                        db.add(new_slot)
                        added_items.append({
                            "item": item.name,
                            "quantity": quantity,
                            "action": "new"
                        })
                        break
        else:
            # Non-stackable item - create separate slots
            max_slots = 30
            existing_slots = db.query(InventorySlot).filter(
                InventorySlot.character_id == character.id
            ).all()
            used_indices = {slot.slot_index for slot in existing_slots}
            
            for qty in range(quantity):
                for i in range(max_slots):
                    if i not in used_indices:
                        new_slot = InventorySlot(
                            character_id=character.id,
                            item_id=item.id,
                            quantity=1,
                            slot_index=i
                        )
                        db.add(new_slot)
                        used_indices.add(i)
                        break
        
        # Track cores and shells
        if drop["is_core"]:
            cores_found.append(item.name)
        elif drop["is_shell"]:
            shells_found.append({"name": item.name, "quantity": quantity})
    
    db.commit()
    
    return {
        "added_items": added_items,
        "cores_found": cores_found,
        "shells_found": shells_found,
        "message": _format_drop_message(cores_found, shells_found)
    }


def _format_drop_message(cores: List[str], shells: List[Dict[str, Any]]) -> str:
    """Format drop message."""
    messages = []
    
    if cores:
        messages.append(f"🎉 СЕРДЦЕВИНА ПОЛУЧЕНА: {', '.join(cores)}")
    
    if shells:
        shell_text = ", ".join([f"{s['name']} x{s['quantity']}" for s in shells])
        messages.append(f"Оболочки: {shell_text}")
    
    if not messages:
        return "Ничего не выпало."
    
    return "\n".join(messages)


def get_drop_info(monster: Monster) -> Dict[str, Any]:
    """Get information about possible drops from monster."""
    if not monster.drop_table:
        return {"cores": [], "shells": [], "other": []}
    
    cores = []
    shells = []
    other = []
    
    for drop_item in monster.drop_table.items:
        item = drop_item.item
        if not item:
            continue
        
        drop_info = {
            "name": item.name,
            "chance": float(drop_item.drop_chance) * 100,
            "quantity": f"{drop_item.min_quantity}-{drop_item.max_quantity}",
        }
        
        if item.is_soul_bound:
            cores.append(drop_info)
        elif item.item_type.value == "shell":
            shells.append(drop_info)
        else:
            other.append(drop_info)
    
    return {
        "cores": cores,
        "shells": shells,
        "other": other
    }

