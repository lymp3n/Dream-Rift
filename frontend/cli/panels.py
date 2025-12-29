"""UI panels for mobile-like interface."""

from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from typing import Dict, Any, List, Optional
from frontend.cli.display import print_status_bar, print_location, print_monsters

console = Console()


class GamePanel:
    """Main game panel."""
    
    def __init__(self):
        self.current_location: Optional[Dict[str, Any]] = None
        self.character_stats: Optional[Dict[str, Any]] = None
    
    def render_location_screen(self, location: Dict[str, Any], character: Dict[str, Any]):
        """Render main location screen."""
        self.current_location = location
        
        # Status bar
        hp = character.get('max_hp', 100)
        mp = character.get('max_mp', 50)
        print_status_bar(hp, hp, mp, mp, 0, 30)  # Simplified
        
        # Location description
        print_location(location)
        
        # Monsters
        if 'monsters' in location:
            print_monsters(location['monsters'])
        
        # Navigation
        console.print("\n[bold]Навигация:[/]")
        if 'connected_locations' in location:
            for loc_id in location['connected_locations']:
                console.print(f"  [cyan]➡️ Перейти в локацию {loc_id}[/]")


def show_character_panel(character: Dict[str, Any], stats: Optional[Dict[str, Any]] = None):
    """Show character panel (slide-in from right)."""
    from frontend.cli.display import print_character_info
    console.clear()
    print_character_info(character, stats)
    console.print("\n[dim]Нажмите Enter для возврата...[/]")


def show_inventory_panel(inventory: Dict[str, Any]):
    """Show inventory panel (popup)."""
    from frontend.cli.display import print_inventory
    console.clear()
    print_inventory(inventory)
    console.print("\n[dim]Нажмите Enter для возврата...[/]")


def show_skills_panel(skills: List[Dict[str, Any]], selected: bool = False):
    """Show skills panel (slide-in from left)."""
    from frontend.cli.display import print_skills
    console.clear()
    print_skills(skills, selected)
    console.print("\n[dim]Нажмите Enter для возврата...[/]")


def show_menu():
    """Show main menu."""
    menu_items = [
        ("1", "Персонаж", "character"),
        ("2", "Инвентарь", "inventory"),
        ("3", "Навыки", "skills"),
        ("4", "Рынок", "market"),
        ("5", "Крафт", "crafting"),
        ("0", "Выход", "exit"),
    ]
    
    console.print("\n[bold]Меню:[/]")
    for key, label, _ in menu_items:
        console.print(f"  [{key}] {label}")

