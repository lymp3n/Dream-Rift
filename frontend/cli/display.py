"""Display utilities using rich."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from typing import Dict, Any, List, Optional

console = Console()


def print_status_bar(hp: int, max_hp: int, mp: int, max_mp: int, inventory_used: int, inventory_max: int):
    """Print status bar (top of screen)."""
    hp_text = f"HP: {hp}/{max_hp}"
    mp_text = f"MP: {mp}/{max_mp}"
    inv_text = f"Инвент.: {inventory_used}/{inventory_max}"
    
    status_line = f"{hp_text}  {mp_text}  {inv_text}"
    console.print(f"[bold red]{hp_text}[/]  [bold blue]{mp_text}[/]  [dim]{inv_text}[/]", end="")
    console.print(" " * 20 + "[bold]Меню[/]", justify="right")


def print_location(location: Dict[str, Any]):
    """Print location description."""
    console.print()
    console.print(Panel(
        f"[bold]{location['name']}[/]\n\n{location['description']}",
        title="Локация",
        border_style="cyan"
    ))


def print_monsters(monsters: List[Dict[str, Any]]):
    """Print list of monsters."""
    if not monsters:
        console.print("[dim]Нет обитателей[/]")
        return
    
    console.print("\n[bold]Обитатели:[/]")
    for monster in monsters:
        hp_percent = (monster['current_hp'] / monster['max_hp']) * 100
        hp_color = "green" if hp_percent > 50 else "yellow" if hp_percent > 25 else "red"
        
        console.print(f"  [bold]{monster['name']}[/] [dim](Ур. {monster['level']})[/] "
                     f"[{hp_color}]HP: {monster['current_hp']}/{monster['max_hp']}[/] "
                     f"[cyan][⚔️Атаковать][/]")


def print_character_info(character: Dict[str, Any], stats: Optional[Dict[str, Any]] = None):
    """Print character information."""
    table = Table(title="Персонаж", show_header=True, header_style="bold magenta")
    table.add_column("Характеристика", style="cyan")
    table.add_column("Значение", style="green")
    
    table.add_row("Имя", character['name'])
    table.add_row("Уровень", str(character['level']))
    table.add_row("Класс", character['character_class'])
    
    table.add_row("", "")  # Separator
    table.add_row("[bold]Базовые характеристики[/]", "")
    table.add_row("Сила (STR)", str(character['strength']))
    table.add_row("Ловкость (AGI)", str(character['agility']))
    table.add_row("Интеллект (INT)", str(character['intelligence']))
    table.add_row("Выносливость (END)", str(character['endurance']))
    table.add_row("Мудрость (WIS)", str(character['wisdom']))
    table.add_row("Удача (LUK)", str(character['luck']))
    
    if stats:
        table.add_row("", "")  # Separator
        table.add_row("[bold]Производные характеристики[/]", "")
        if 'physical_damage' in stats:
            phys_dmg = stats['physical_damage']
            table.add_row("Физ. Урон", f"{phys_dmg['min']}-{phys_dmg['max']}")
        if 'magical_damage' in stats:
            mag_dmg = stats['magical_damage']
            table.add_row("Маг. Урон", f"{mag_dmg['min']}-{mag_dmg['max']}")
        if 'physical_defense' in stats:
            table.add_row("Физ. Защита", str(stats['physical_defense']))
        if 'magical_defense' in stats:
            table.add_row("Маг. Защита", f"{stats['magical_defense']:.1f}%")
        if 'crit_chance' in stats:
            table.add_row("Шанс Крита", f"{stats['crit_chance']:.1f}%")
        if 'speed' in stats:
            table.add_row("Скорость", str(stats['speed']))
    
    console.print(table)


def print_inventory(inventory: Dict[str, Any]):
    """Print inventory grid."""
    slots = inventory.get('slots', [])
    used = inventory.get('used_slots', 0)
    max_slots = inventory.get('max_slots', 30)
    
    console.print(f"\n[bold]Инвентарь ({used}/{max_slots}):[/]")
    
    # Print as 6x5 grid
    for row in range(5):
        row_items = []
        for col in range(6):
            idx = row * 6 + col
            if idx < len(slots) and slots[idx]:
                item = slots[idx]['item']
                qty = slots[idx]['quantity']
                rarity_colors = {
                    "common": "white",
                    "uncommon": "green",
                    "rare": "blue",
                    "epic": "magenta",
                    "legendary": "yellow"
                }
                color = rarity_colors.get(item['rarity'], "white")
                display = f"[{color}]{item['name'][:8]}[/]"
                if qty > 1:
                    display += f" x{qty}"
                row_items.append(display)
            else:
                row_items.append("[dim][ ][/]")
        
        console.print("  ".join(row_items))


def print_skills(skills: List[Dict[str, Any]], selected: bool = False):
    """Print skills list."""
    if not skills:
        console.print("[dim]Нет навыков[/]")
        return
    
    table = Table(title="Выбранные навыки" if selected else "Библиотека навыков")
    table.add_column("Слот", style="cyan")
    table.add_column("Название", style="green")
    table.add_column("Описание", style="white")
    
    for skill in skills:
        slot = skill.get('slot') or skill.get('selected_slot') or "-"
        table.add_row(
            str(slot),
            skill['name'],
            skill.get('description', '')[:50] + "..." if len(skill.get('description', '')) > 50 else skill.get('description', '')
        )
    
    console.print(table)


def print_combat_result(result: Dict[str, Any]):
    """Print combat result."""
    message = result.get('message', '')
    is_crit = result.get('is_crit', False)
    
    if is_crit:
        console.print(f"[bold yellow]{message}[/]")
    else:
        console.print(f"[green]{message}[/]")


def print_travel_progress(location_name: str, travel_time: int):
    """Print travel progress with timer."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"Вы движетесь в {location_name}...", total=travel_time)
        import time
        for i in range(travel_time):
            time.sleep(1)
            progress.update(task, advance=1)
    
    console.print(f"[green]Вы прибыли в {location_name}![/]")


def clear_screen():
    """Clear screen."""
    console.clear()

