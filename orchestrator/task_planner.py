"""Task planner agent - breaks down project into tasks and subtasks."""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class TaskPlanner:
    """Agent that breaks down project into manageable tasks."""
    
    def __init__(self, tasks_file: str = "orchestrator/tasks.json"):
        self.tasks_file = Path(tasks_file)
        self.tasks = self._load_tasks()
    
    def _load_tasks(self) -> Dict[str, Any]:
        """Load tasks from file."""
        if self.tasks_file.exists():
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "tasks": [],
            "last_updated": None,
            "version": 1
        }
    
    def _save_tasks(self):
        """Save tasks to file."""
        self.tasks["last_updated"] = datetime.now().isoformat()
        with open(self.tasks_file, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, indent=2, ensure_ascii=False)
    
    def add_task(self, title: str, description: str, priority: str = "medium", 
                 dependencies: List[str] = None, subtasks: List[Dict] = None) -> str:
        """Add a new task."""
        task_id = f"task_{len(self.tasks.get('tasks', [])) + 1}"
        
        task = {
            "id": task_id,
            "title": title,
            "description": description,
            "priority": priority,  # low, medium, high, critical
            "status": "pending",  # pending, in_progress, completed, blocked
            "dependencies": dependencies or [],
            "subtasks": subtasks or [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "estimated_hours": 0,
            "actual_hours": 0,
            "assignee": None,
            "tags": []
        }
        
        if "tasks" not in self.tasks:
            self.tasks["tasks"] = []
        
        self.tasks["tasks"].append(task)
        self._save_tasks()
        return task_id
    
    def add_subtask(self, task_id: str, title: str, description: str):
        """Add subtask to existing task."""
        task = self.get_task(task_id)
        if not task:
            return False
        
        subtask = {
            "title": title,
            "description": description,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        task["subtasks"].append(subtask)
        task["updated_at"] = datetime.now().isoformat()
        self._save_tasks()
        return True
    
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get task by ID."""
        for task in self.tasks.get("tasks", []):
            if task["id"] == task_id:
                return task
        return None
    
    def update_task_status(self, task_id: str, status: str):
        """Update task status."""
        task = self.get_task(task_id)
        if not task:
            return False
        
        task["status"] = status
        task["updated_at"] = datetime.now().isoformat()
        self._save_tasks()
        return True
    
    def get_pending_tasks(self, priority: str = None) -> List[Dict[str, Any]]:
        """Get pending tasks, optionally filtered by priority."""
        tasks = [t for t in self.tasks.get("tasks", []) if t["status"] == "pending"]
        
        if priority:
            tasks = [t for t in tasks if t["priority"] == priority]
        
        # Sort by priority (critical > high > medium > low)
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        tasks.sort(key=lambda x: priority_order.get(x["priority"], 4))
        
        return tasks
    
    def break_down_feature(self, feature_name: str, description: str) -> str:
        """Break down a feature into tasks and subtasks."""
        task_id = self.add_task(
            title=f"Реализовать: {feature_name}",
            description=description,
            priority="high"
        )
        
        # Add common subtasks
        subtasks = [
            {
                "title": "Проектирование",
                "description": "Спроектировать архитектуру и интерфейсы",
                "status": "pending"
            },
            {
                "title": "Реализация бэкенда",
                "description": "Реализовать backend логику",
                "status": "pending"
            },
            {
                "title": "Реализация фронтенда",
                "description": "Реализовать UI/UX",
                "status": "pending"
            },
            {
                "title": "Тестирование",
                "description": "Написать и запустить тесты",
                "status": "pending"
            },
            {
                "title": "Документация",
                "description": "Обновить документацию",
                "status": "pending"
            }
        ]
        
        task = self.get_task(task_id)
        task["subtasks"] = subtasks
        self._save_tasks()
        
        return task_id
    
    def get_task_report(self) -> str:
        """Generate task report."""
        tasks = self.tasks.get("tasks", [])
        
        report = f"Отчет по задачам\n"
        report += f"Всего задач: {len(tasks)}\n"
        report += f"Ожидающих: {len([t for t in tasks if t['status'] == 'pending'])}\n"
        report += f"В работе: {len([t for t in tasks if t['status'] == 'in_progress'])}\n"
        report += f"Завершено: {len([t for t in tasks if t['status'] == 'completed'])}\n\n"
        
        pending = self.get_pending_tasks()
        if pending:
            report += "Приоритетные задачи:\n"
            for task in pending[:5]:
                report += f"  - [{task['priority']}] {task['title']}\n"
        
        return report


# Initialize planner with current project tasks
def init_project_tasks():
    """Initialize project with current tasks."""
    planner = TaskPlanner()
    
    # Check if tasks already exist
    if planner.tasks.get("tasks"):
        return planner
    
    # Add current project tasks
    planner.break_down_feature(
        "Улучшенная система боя",
        "Реализовать пошаговый бой с таймингом, выбором скиллов, системой тактик"
    )
    
    planner.break_down_feature(
        "Современный интерфейс",
        "Переделать интерфейс в более современный с чатом и улучшенной навигацией"
    )
    
    return planner


if __name__ == "__main__":
    planner = init_project_tasks()
    print(planner.get_task_report())

