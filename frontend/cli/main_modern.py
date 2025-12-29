"""Modern main CLI interface with chat."""

import sys
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from frontend.cli.api_client import APIClient
from frontend.cli.ui_modern import ModernUI, ChatMessage
from frontend.cli.commands import CommandHandler
from frontend.cli.navigation import Navigation, parse_command
import time

console = Console()


def main():
    """Main game loop with modern UI."""
    # Initialize
    api = APIClient()
    character_id = 1  # Default character ID
    
    try:
        # Test connection
        api._get("/health")
    except Exception as e:
        console.print(f"[red]Не удалось подключиться к API: {e}[/]")
        console.print("[yellow]Убедитесь, что бэкенд запущен на http://127.0.0.1:8000[/]")
        return
    
    handler = CommandHandler(api, character_id)
    nav = Navigation()
    ui = ModernUI()
    
    # Add welcome message
    ui.add_chat_message("Система", "Добро пожаловать в Dreamforge: Эхо Бездны!", "system")
    
    # Main game loop
    current_screen = "location"
    in_combat = False
    combat_state = None
    
    try:
        while True:
            # Get character data
            try:
                character = api.get_character(character_id)
                character_stats = api.get_character_stats(character_id)
            except Exception as e:
                if "404" in str(e) or "not found" in str(e).lower():
                    ui.add_chat_message("Система", 
                        f"Персонаж с ID {character_id} не найден. Создайте персонажа через API или используйте test_setup.py", 
                        "error")
                    console.print(f"[red]Персонаж не найден. Запустите: python test_setup.py[/]")
                else:
                    ui.add_chat_message("Система", f"Ошибка загрузки: {e}", "error")
                # Wait a bit before retrying
                import time
                time.sleep(2)
                continue
            
            # Render UI
            char_data = character_stats.get('character', character)
            stats_data = character_stats.get('stats', {})
            status = ui.render_status_bar({
                'max_hp': character_stats.get('max_hp', 100),
                'max_mp': character_stats.get('max_mp', 50),
                'current_hp': character_stats.get('max_hp', 100),  # Simplified - should be stored
                'current_mp': character_stats.get('max_mp', 50),  # Simplified - should be stored
                'inventory_used': 0
            })
            
            try:
                if in_combat and combat_state:
                    # Combat screen
                    try:
                        skills = api.get_selected_skills(character_id)
                    except:
                        skills = []
                    # Update combat state from API
                    try:
                        monster_id = combat_state.get('monster_id')
                        if monster_id:
                            combat_state = api._get(f"/api/combat-enhanced/state?character_id={character_id}&monster_id={monster_id}")
                    except:
                        pass
                    content = ui.render_combat_screen(combat_state, skills)
                elif current_screen == "location":
                    # Location screen
                    location_id = character.get('location_id')
                    if location_id:
                        try:
                            location = api.get_location(location_id)
                            content = ui.render_location_screen(location, character)
                        except Exception as e:
                            content = f"[red]Ошибка загрузки локации: {e}[/]"
                    else:
                        content = "[yellow]Персонаж не в локации. Используйте travel для перемещения.[/]"
                else:
                    content = "[dim]Загрузка...[/]"
            except Exception as e:
                content = f"[red]Ошибка рендеринга: {e}[/]"
            
            chat = ui.render_chat()
            
            # Render full screen
            screen_content = ui.render_full_screen(status, content, chat)
            
            # Clear and render
            console.clear()
            console.print(screen_content)
            
            # Get command
            command_str = nav.get_input("\n[bold cyan]> [/]")
            
            if not command_str:
                continue
            
            cmd, args = parse_command(command_str)
            
            # Handle chat commands
            if cmd.startswith("/"):
                if cmd == "/chat" or cmd == "/c":
                    ui.toggle_chat()
                    continue
                elif cmd == "/clear":
                    ui.chat_messages = []
                    ui.add_chat_message("Система", "Чат очищен", "system")
                    continue
                elif cmd == "/help" or cmd == "/h":
                    ui.add_chat_message("Система", 
                        "Команды: /chat - открыть чат, /clear - очистить, /help - помощь", 
                        "system")
                    continue
            
            # Handle combat commands
            if in_combat:
                monster_id = combat_state.get('monster_id')
                if not monster_id:
                    ui.add_chat_message("Система", "Ошибка: ID моба не найден", "error")
                    in_combat = False
                    continue
                
                if cmd in ["1", "атака", "attack", "a"]:
                    # Basic attack
                    try:
                        result = api.combat_action(character_id, monster_id, "attack")
                        if result.get('success'):
                            action_result = result.get('action_result', {})
                            ui.add_chat_message("Бой", action_result.get('message', 'Атака выполнена'), "combat")
                            
                            # Check for monster action
                            if 'monster_action' in action_result:
                                monster_msg = action_result['monster_action'].get('message', '')
                                ui.add_chat_message("Бой", monster_msg, "combat")
                            
                            # Update combat state
                            combat_state = api._get(f"/api/combat-enhanced/state?character_id={character_id}&monster_id={monster_id}")
                            if combat_state.get('combat_over') or action_result.get('combat_over'):
                                in_combat = False
                                winner = action_result.get('winner', 'unknown')
                                ui.add_chat_message("Система", f"Бой завершен! Победитель: {winner}", "system")
                        else:
                            ui.add_chat_message("Система", result.get('error', 'Ошибка атаки'), "error")
                    except Exception as e:
                        ui.add_chat_message("Система", f"Ошибка: {e}", "error")
                
                elif cmd.isdigit():
                    skill_num = int(cmd)
                    if skill_num == 0:
                        in_combat = False
                        ui.add_chat_message("Система", "Бой прерван", "system")
                    elif skill_num > 1:
                        try:
                            skills = api.get_selected_skills(character_id)
                            if 0 <= skill_num - 2 < len(skills):
                                skill = skills[skill_num - 2]
                                result = api.combat_action(character_id, monster_id, "skill", skill['id'])
                                if result.get('success'):
                                    action_result = result.get('action_result', {})
                                    ui.add_chat_message("Бой", action_result.get('message', 'Навык использован'), "combat")
                                    
                                    # Check for monster action
                                    if 'monster_action' in action_result:
                                        monster_msg = action_result['monster_action'].get('message', '')
                                        ui.add_chat_message("Бой", monster_msg, "combat")
                                    
                                    # Update combat state
                                    combat_state = api._get(f"/api/combat-enhanced/state?character_id={character_id}&monster_id={monster_id}")
                                    if combat_state.get('combat_over') or action_result.get('combat_over'):
                                        in_combat = False
                                        winner = action_result.get('winner', 'unknown')
                                        ui.add_chat_message("Система", f"Бой завершен! Победитель: {winner}", "system")
                                else:
                                    ui.add_chat_message("Система", result.get('error', 'Ошибка использования навыка'), "error")
                            else:
                                ui.add_chat_message("Система", f"Неверный номер навыка (доступно: {len(skills)})", "error")
                        except Exception as e:
                            ui.add_chat_message("Система", f"Ошибка: {e}", "error")
            
            # Handle location commands
            elif current_screen == "location":
                if cmd in ["атаковать", "attack", "a"] and args:
                    try:
                        # Get monster ID from args or from location
                        if args:
                            monster_id = int(args[0])
                        else:
                            # Try to get first monster from location
                            location_id = character.get('location_id')
                            if location_id:
                                location = api.get_location(location_id)
                                monsters = location.get('monsters', [])
                                if monsters:
                                    monster_id = monsters[0].get('id')
                                else:
                                    ui.add_chat_message("Система", "В локации нет мобов", "error")
                                    continue
                            else:
                                ui.add_chat_message("Система", "Персонаж не в локации", "error")
                                continue
                        
                        # Start combat
                        combat_start = api.start_combat(character_id, monster_id)
                        in_combat = True
                        combat_state = combat_start.get('combat_state', {})
                        combat_state['monster_id'] = monster_id
                        ui.add_chat_message("Система", f"Бой начат с мобом ID {monster_id}!", "combat")
                    except Exception as e:
                        ui.add_chat_message("Система", f"Ошибка начала боя: {e}", "error")
                
                elif cmd in ["перейти", "travel", "t"] and args:
                    try:
                        location_id = int(args[0])
                        handler.travel(location_id)
                        ui.add_chat_message("Система", f"Перемещение в локацию {location_id}", "system")
                    except Exception as e:
                        ui.add_chat_message("Система", f"Ошибка: {e}", "error")
                
                elif cmd in ["меню", "menu", "m"]:
                    current_screen = "menu"
            
            # Handle menu commands
            elif current_screen == "menu":
                if cmd == "1" or cmd == "персонаж":
                    handler.show_character()
                    current_screen = "location"
                elif cmd == "2" or cmd == "инвентарь":
                    handler.show_inventory()
                    current_screen = "location"
                elif cmd == "3" or cmd == "навыки":
                    handler.show_skills()
                    current_screen = "location"
                elif cmd == "0" or cmd == "выход":
                    break
                else:
                    current_screen = "location"
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Выход из игры...[/]")
    except Exception as e:
        console.print(f"[red]Ошибка: {e}[/]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

