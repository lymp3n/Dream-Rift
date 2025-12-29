"""Navigation between screens."""

from typing import Dict, Any, Optional, Callable
from rich.console import Console
try:
    from prompt_toolkit import prompt
    from prompt_toolkit.shortcuts import yes_no_dialog
except ImportError:
    # Fallback if prompt_toolkit not available
    def prompt(text=""):
        return input(text)
    
    def yes_no_dialog(title="", text=""):
        class Dialog:
            def run(self):
                response = input(f"{text} (y/n): ").lower()
                return response == 'y'
        return Dialog()

console = Console()


class Navigation:
    """Handle navigation between screens."""
    
    def __init__(self):
        self.current_screen = "location"
        self.screen_stack = []
    
    def push_screen(self, screen_name: str):
        """Push screen to stack."""
        self.screen_stack.append(self.current_screen)
        self.current_screen = screen_name
    
    def pop_screen(self) -> Optional[str]:
        """Pop screen from stack."""
        if self.screen_stack:
            self.current_screen = self.screen_stack.pop()
            return self.current_screen
        return None
    
    def get_input(self, prompt_text: str = "> ") -> str:
        """Get user input."""
        return prompt(prompt_text)
    
    def confirm(self, message: str) -> bool:
        """Confirm action."""
        return yes_no_dialog(title="Подтверждение", text=message).run()
    
    def wait_for_enter(self, message: str = "Нажмите Enter для продолжения..."):
        """Wait for Enter key."""
        input(message)


def parse_command(command: str) -> tuple[str, list[str]]:
    """Parse command string."""
    parts = command.strip().split()
    if not parts:
        return "", []
    
    cmd = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []
    return cmd, args


def handle_location_commands(command: str, args: list[str], handler, location: Dict[str, Any]) -> bool:
    """Handle commands in location screen."""
    if command == "атаковать" or command == "attack" or command == "a":
        if args:
            try:
                monster_id = int(args[0])
                handler.attack(monster_id)
                return True
            except ValueError:
                console.print("[red]Неверный ID моба[/]")
                return False
        else:
            console.print("[red]Укажите ID моба[/]")
            return False
    
    elif command == "перейти" or command == "travel" or command == "t":
        if args:
            try:
                location_id = int(args[0])
                handler.travel(location_id)
                return True
            except ValueError:
                console.print("[red]Неверный ID локации[/]")
                return False
        else:
            console.print("[red]Укажите ID локации[/]")
            return False
    
    elif command == "меню" or command == "menu" or command == "m":
        handler.show_menu()
        return True
    
    return False


def handle_menu_commands(command: str, args: list[str], handler) -> Optional[str]:
    """Handle commands in menu."""
    if command == "1" or command == "персонаж" or command == "character":
        handler.show_character()
        return "location"
    
    elif command == "2" or command == "инвентарь" or command == "inventory":
        handler.show_inventory()
        return "location"
    
    elif command == "3" or command == "навыки" or command == "skills":
        handler.show_skills()
        return "location"
    
    elif command == "0" or command == "выход" or command == "exit":
        return "exit"
    
    return None

