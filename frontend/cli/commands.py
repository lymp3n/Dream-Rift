"""Command handlers."""

from typing import Dict, Any, Optional
from rich.console import Console
from frontend.cli.api_client import APIClient
from frontend.cli.display import print_combat_result, print_travel_progress
from frontend.cli.panels import show_character_panel, show_inventory_panel, show_skills_panel, show_menu

console = Console()


class CommandHandler:
    """Handle game commands."""
    
    def __init__(self, api: APIClient, character_id: int):
        self.api = api
        self.character_id = character_id
    
    def attack(self, monster_id: int, skill_id: Optional[int] = None) -> Dict[str, Any]:
        """Attack monster."""
        try:
            action_type = "skill" if skill_id else "attack"
            result = self.api.combat_action(self.character_id, monster_id, action_type, skill_id)
            if result.get('action_result'):
                print_combat_result(result['action_result'])
            return result
        except Exception as e:
            console.print(f"[red]Ошибка: {e}[/]")
            return {}
    
    def travel(self, target_location_id: int) -> Dict[str, Any]:
        """Travel to location."""
        try:
            # Get location info first
            location_info = self.api.get_location(target_location_id)
            travel_time = location_info.get('travel_time', 5)
            
            # Show travel progress
            print_travel_progress(location_info['name'], travel_time)
            
            # Execute travel
            result = self.api.travel(self.character_id, target_location_id)
            return result
        except Exception as e:
            console.print(f"[red]Ошибка: {e}[/]")
            return {}
    
    def show_character(self):
        """Show character panel."""
        try:
            character = self.api.get_character(self.character_id)
            stats_data = self.api.get_character_stats(self.character_id)
            stats = stats_data.get('stats', {})
            show_character_panel(character, stats)
            input()  # Wait for Enter
        except Exception as e:
            console.print(f"[red]Ошибка: {e}[/]")
    
    def show_inventory(self):
        """Show inventory panel."""
        try:
            inventory = self.api.get_inventory(self.character_id)
            show_inventory_panel(inventory)
            input()  # Wait for Enter
        except Exception as e:
            console.print(f"[red]Ошибка: {e}[/]")
    
    def show_skills(self, selected: bool = False):
        """Show skills panel."""
        try:
            if selected:
                skills = self.api.get_selected_skills(self.character_id)
            else:
                skills = self.api.get_learned_skills(self.character_id)
            show_skills_panel(skills, selected)
            input()  # Wait for Enter
        except Exception as e:
            console.print(f"[red]Ошибка: {e}[/]")
    
    def show_menu(self):
        """Show main menu."""
        show_menu()

