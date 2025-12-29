"""Main CLI interface."""

import sys
from rich.console import Console
from frontend.cli.api_client import APIClient
from frontend.cli.commands import CommandHandler
from frontend.cli.navigation import Navigation, parse_command, handle_location_commands, handle_menu_commands
from frontend.cli.panels import GamePanel
from frontend.cli.display import clear_screen

console = Console()


def main():
    """Main game loop."""
    # Initialize
    api = APIClient()
    character_id = 1  # Default character ID - should be passed as argument or selected
    
    try:
        # Test connection
        api._get("/health")
    except Exception as e:
        console.print(f"[red]Не удалось подключиться к API: {e}[/]")
        console.print("[yellow]Убедитесь, что бэкенд запущен на http://127.0.0.1:8000[/]")
        return
    
    handler = CommandHandler(api, character_id)
    nav = Navigation()
    panel = GamePanel()
    
    # Main game loop
    current_screen = "location"
    
    while True:
        try:
            if current_screen == "location":
                # Get current location
                character = api.get_character(character_id)
                location_id = character.get('location_id')
                
                if location_id:
                    location = api.get_location(location_id)
                    panel.render_location_screen(location, character)
                else:
                    # Character not in location, show available
                    locations = api.get_available_locations(character_id)
                    console.print("[bold]Доступные локации:[/]")
                    for loc in locations:
                        console.print(f"  [{loc['id']}] {loc['name']}")
                
                # Get command
                command_str = nav.get_input("\n> ")
                cmd, args = parse_command(command_str)
                
                if cmd == "меню" or cmd == "menu" or cmd == "m":
                    current_screen = "menu"
                elif cmd == "выход" or cmd == "exit" or cmd == "quit":
                    break
                else:
                    handle_location_commands(cmd, args, handler, location if location_id else {})
            
            elif current_screen == "menu":
                handler.show_menu()
                command_str = nav.get_input("\n> ")
                cmd, args = parse_command(command_str)
                
                result = handle_menu_commands(cmd, args, handler)
                if result == "exit":
                    break
                elif result:
                    current_screen = result
                else:
                    current_screen = "location"
            
            else:
                current_screen = "location"
        
        except KeyboardInterrupt:
            console.print("\n[yellow]Выход из игры...[/]")
            break
        except Exception as e:
            console.print(f"[red]Ошибка: {e}[/]")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()

