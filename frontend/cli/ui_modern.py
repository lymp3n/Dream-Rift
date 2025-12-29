"""Modern UI with chat support."""

from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from typing import List, Dict, Any, Optional
import time
from datetime import datetime

console = Console()


class ChatMessage:
    """Chat message."""
    
    def __init__(self, sender: str, message: str, message_type: str = "normal"):
        self.sender = sender
        self.message = message
        self.message_type = message_type  # normal, system, combat, error
        self.timestamp = datetime.now()
    
    def __str__(self):
        time_str = self.timestamp.strftime("%H:%M")
        if self.message_type == "system":
            return f"[dim]{time_str}[/] [yellow]Система:[/] {self.message}"
        elif self.message_type == "combat":
            return f"[dim]{time_str}[/] [red]Бой:[/] {self.message}"
        elif self.message_type == "error":
            return f"[dim]{time_str}[/] [bold red]Ошибка:[/] {self.message}"
        else:
            return f"[dim]{time_str}[/] [cyan]{self.sender}:[/] {self.message}"


class ModernUI:
    """Modern UI with chat."""
    
    def __init__(self):
        self.chat_messages: List[ChatMessage] = []
        self.chat_visible_lines = 3  # Visible chat lines in collapsed state
        self.chat_expanded = False
        self.layout = None
        self._setup_layout()
    
    def _setup_layout(self):
        """Setup UI layout."""
        self.layout = Layout()
        
        # Main layout: top (status), middle (content), bottom (chat)
        self.layout.split_column(
            Layout(name="status", size=3),
            Layout(name="content", ratio=1),
            Layout(name="chat", size=self.chat_visible_lines + 2)
        )
        
        # Content can be split for side panels
        self.layout["content"].split_row(
            Layout(name="main", ratio=2),
            Layout(name="sidebar", size=30, visible=False)
        )
    
    def add_chat_message(self, sender: str, message: str, message_type: str = "normal"):
        """Add message to chat."""
        msg = ChatMessage(sender, message, message_type)
        self.chat_messages.append(msg)
        
        # Keep only last 100 messages
        if len(self.chat_messages) > 100:
            self.chat_messages = self.chat_messages[-100:]
    
    def toggle_chat(self):
        """Toggle chat expansion."""
        self.chat_expanded = not self.chat_expanded
        if self.chat_expanded:
            self.layout["chat"].size = None  # Full height
            self.layout["content"].visible = False
        else:
            self.layout["chat"].size = self.chat_visible_lines + 2
            self.layout["content"].visible = True
    
    def render_status_bar(self, character: Dict[str, Any]) -> str:
        """Render status bar."""
        hp = character.get('max_hp', 100)
        mp = character.get('max_mp', 50)
        current_hp = character.get('current_hp', hp)
        current_mp = character.get('current_mp', mp)
        
        hp_percent = (current_hp / hp) * 100 if hp > 0 else 0
        mp_percent = (current_mp / mp) * 100 if mp > 0 else 0
        
        # HP bar
        hp_bar = self._create_progress_bar(hp_percent, "red")
        hp_text = f"[bold red]HP:[/] {current_hp}/{hp} {hp_bar}"
        
        # MP bar
        mp_bar = self._create_progress_bar(mp_percent, "blue")
        mp_text = f"[bold blue]MP:[/] {current_mp}/{mp} {mp_bar}"
        
        # Inventory
        inv_text = f"[dim]Инвент.: {character.get('inventory_used', 0)}/30[/]"
        
        # Format status bar to fit screen
        status = f"{hp_text}  {mp_text}  {inv_text}"
        return status
    
    def _create_progress_bar(self, percent: float, color: str, width: int = 20) -> str:
        """Create text progress bar."""
        filled = int(width * percent / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{color}]{bar}[/]"
    
    def render_chat(self) -> str:
        """Render chat panel."""
        if not self.chat_messages:
            return "[dim]Чат пуст. Используйте /chat для открытия[/]"
        
        # Get visible messages
        if self.chat_expanded:
            visible = self.chat_messages[-30:]  # Last 30 when expanded
        else:
            visible = self.chat_messages[-self.chat_visible_lines:]  # Last N when collapsed
        
        lines = [str(msg) for msg in visible]
        chat_text = "\n".join(lines)
        
        if not self.chat_expanded and len(self.chat_messages) > self.chat_visible_lines:
            chat_text += f"\n[dim]... и еще {len(self.chat_messages) - self.chat_visible_lines} сообщений. /chat для открытия[/]"
        
        return chat_text
    
    def render_combat_screen(self, combat_state: Dict[str, Any], skills: List[Dict[str, Any]] = None) -> str:
        """Render combat screen."""
        content = []
        
        # Combat info
        content.append(f"[bold cyan]═══ БОЙ - Ход {combat_state.get('turn_number', 0)} ═══[/]")
        content.append("")
        
        # Character HP/MP with bars
        char_hp = combat_state.get('character_hp', 0)
        char_max_hp = combat_state.get('character_max_hp', 0)
        char_mp = combat_state.get('character_mp', 0)
        char_max_mp = combat_state.get('character_max_mp', 0)
        
        hp_percent = (char_hp / char_max_hp * 100) if char_max_hp > 0 else 0
        mp_percent = (char_mp / char_max_mp * 100) if char_max_mp > 0 else 0
        
        hp_bar = self._create_progress_bar(hp_percent, "red", 15)
        mp_bar = self._create_progress_bar(mp_percent, "blue", 15)
        
        content.append(f"[bold]Ваше HP:[/] [red]{char_hp}/{char_max_hp}[/] {hp_bar}")
        content.append(f"[bold]Ваше MP:[/] [blue]{char_mp}/{char_max_mp}[/] {mp_bar}")
        content.append("")
        
        # Monster info with bar
        monster_hp = combat_state.get('monster_hp', 0)
        monster_max_hp = combat_state.get('monster_max_hp', 0)
        monster_hp_percent = (monster_hp / monster_max_hp * 100) if monster_max_hp > 0 else 0
        monster_bar = self._create_progress_bar(monster_hp_percent, "red", 15)
        content.append(f"[bold]Враг HP:[/] [red]{monster_hp}/{monster_max_hp}[/] {monster_bar}")
        content.append("")
        
        # Time remaining
        time_remaining = combat_state.get('time_remaining', 0)
        if time_remaining > 0:
            time_bar = self._create_progress_bar((time_remaining / 15 * 100), "yellow", 20)
            content.append(f"[bold yellow]Время хода:[/] {time_remaining:.1f}с {time_bar}")
            content.append("")
        
        # Tactics
        tactics = combat_state.get('tactics', {})
        if tactics:
            tactics_list = [f"[cyan]{k}[/]: {v}" for k, v in tactics.items() if v > 0]
            if tactics_list:
                content.append(f"[bold]Тактики:[/] {', '.join(tactics_list)}")
                content.append("")
        
        # Actions
        content.append("[bold green]═══ ДЕЙСТВИЯ ═══[/]")
        content.append("  [bold][1][/] Обычная атака")
        
        if skills:
            for i, skill in enumerate(skills[:5], start=2):  # Show up to 5 skills
                mp_cost = skill.get('effects', {}).get('mp_cost', 0)
                tactics_cost = skill.get('effects', {}).get('tactics_cost', {})
                cost_parts = []
                if mp_cost > 0:
                    cost_parts.append(f"{mp_cost}MP")
                if tactics_cost:
                    for tactic, cost in tactics_cost.items():
                        cost_parts.append(f"{cost}{tactic}")
                cost_str = f" [dim]({', '.join(cost_parts)})[/]" if cost_parts else ""
                
                consumes = skill.get('effects', {}).get('consumes_turn', True)
                turn_str = " [green]⚡[/]" if not consumes else ""
                
                content.append(f"  [bold][{i}][/] {skill['name']}{cost_str}{turn_str}")
        
        content.append("  [bold][0][/] [dim]Отмена[/]")
        
        return "\n".join(content)
    
    def render_location_screen(self, location: Dict[str, Any], character: Dict[str, Any]) -> str:
        """Render location screen."""
        content = []
        
        content.append(f"[bold cyan]═══ {location['name']} ═══[/]")
        content.append("")
        content.append(f"[dim]{location.get('description', '')}[/]")
        content.append("")
        
        # Monsters
        monsters = location.get('monsters', [])
        if monsters:
            content.append("[bold green]═══ ОБИТАТЕЛИ ═══[/]")
            for i, monster in enumerate(monsters, start=1):
                hp_percent = (monster['current_hp'] / monster['max_hp']) * 100 if monster['max_hp'] > 0 else 0
                hp_color = "green" if hp_percent > 50 else "yellow" if hp_percent > 25 else "red"
                hp_bar = self._create_progress_bar(hp_percent, hp_color, 12)
                content.append(f"  [bold][{i}][/] [bold]{monster['name']}[/] [dim](Ур. {monster.get('level', 1)})[/]")
                content.append(f"      [{hp_color}]HP: {monster['current_hp']}/{monster['max_hp']}[/] {hp_bar}")
                content.append(f"      [cyan][⚔️ Атаковать: attack {monster.get('id', i)}][/]")
                content.append("")
        else:
            content.append("[dim]Нет обитателей[/]")
            content.append("")
        
        # Navigation
        connected = location.get('connected_locations', [])
        if connected:
            content.append("[bold blue]═══ НАВИГАЦИЯ ═══[/]")
            for loc_id in connected:
                content.append(f"  [cyan]➡️ Перейти: travel {loc_id}[/]")
            content.append("")
        
        content.append("[dim]Команды: меню, /chat[/]")
        
        return "\n".join(content)
    
    def render_full_screen(self, status: str, content: str, chat: str) -> str:
        """Render full screen layout as string (simpler approach)."""
        lines = []
        
        # Status bar (compact)
        lines.append("[bold green]" + "═" * 78 + "[/]")
        lines.append(status)
        lines.append("[bold green]" + "═" * 78 + "[/]")
        lines.append("")
        
        # Content
        if self.chat_expanded:
            # Chat expanded - show chat full screen
            lines.append("[bold blue]" + "═" * 78 + "[/]")
            lines.append("[bold blue]ЧАТ (Нажмите /chat для закрытия)[/]")
            lines.append("[bold blue]" + "═" * 78 + "[/]")
            lines.append("")
            lines.append(chat)
        else:
            # Normal view - content takes most space
            lines.append(content)
            lines.append("")
            lines.append("[bold blue]" + "─" * 78 + "[/]")
            lines.append("[dim]ЧАТ ([/][yellow]/chat[/][dim] для открытия)[/]")
            lines.append("[bold blue]" + "─" * 78 + "[/]")
            # Show only last few chat messages
            chat_lines = chat.split("\n")
            if len(chat_lines) > self.chat_visible_lines:
                chat_lines = chat_lines[-self.chat_visible_lines:]
            lines.append("\n".join(chat_lines))
        
        return "\n".join(lines)
    
    def show_combat_timer(self, time_remaining: float, total_time: float):
        """Show combat turn timer."""
        with console.status(f"[bold yellow]Время хода: {time_remaining:.1f}с / {total_time:.1f}с[/]") as status:
            while time_remaining > 0:
                time.sleep(0.1)
                time_remaining -= 0.1
                if time_remaining > 0:
                    status.update(f"[bold yellow]Время хода: {time_remaining:.1f}с / {total_time:.1f}с[/]")


def create_combat_action_menu(skills: List[Dict[str, Any]]) -> str:
    """Create combat action menu."""
    menu = ["[bold]Выберите действие:[/]", ""]
    menu.append("[1] Обычная атака")
    
    for i, skill in enumerate(skills[:6], start=2):
        mp_cost = skill.get('effects', {}).get('mp_cost', 0)
        tactics_cost = skill.get('effects', {}).get('tactics_cost', {})
        
        cost_parts = []
        if mp_cost > 0:
            cost_parts.append(f"{mp_cost}MP")
        if tactics_cost:
            for tactic, cost in tactics_cost.items():
                cost_parts.append(f"{cost}{tactic}")
        
        cost_str = f" ({', '.join(cost_parts)})" if cost_parts else ""
        consumes = skill.get('effects', {}).get('consumes_turn', True)
        turn_str = " [green]⚡[/]" if not consumes else ""
        
        menu.append(f"[{i}] {skill['name']}{cost_str}{turn_str}")
    
    menu.append("")
    menu.append("[0] Отмена")
    
    return "\n".join(menu)

