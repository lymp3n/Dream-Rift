"""Simple startup script for Dreamforge."""

import subprocess
import sys
import os
import time
from pathlib import Path
from pathlib import Path as PathLib


def check_dependencies():
    """Check if dependencies are installed."""
    try:
        import fastapi
        import rich
        import sqlalchemy
        return True
    except ImportError:
        return False


def install_dependencies():
    """Install dependencies."""
    print("Установка зависимостей...")
    
    # First, upgrade pip to get latest wheel support
    print("Обновление pip...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=False)
    
    # Try to install main requirements
    print("Установка основных зависимостей...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        capture_output=True,
        text=True
    )
    
    # If that fails, try alternative installer
    if result.returncode != 0:
        print("Основные зависимости не установились, пробуем альтернативный метод...")
        if Path("install_deps.py").exists():
            result = subprocess.run(
                [sys.executable, "install_deps.py"],
                check=False
            )
        else:
            # Fallback: install core packages manually
            print("Установка основных пакетов вручную...")
            core_packages = [
                "fastapi", "uvicorn[standard]", "sqlalchemy", "alembic",
                "pydantic", "pydantic-settings", "python-dotenv", "python-multipart",
                "rich", "prompt-toolkit", "requests", "pytest", "pytest-asyncio"
            ]
            for pkg in core_packages:
                subprocess.run([sys.executable, "-m", "pip", "install", pkg], check=False)
        
        if result.returncode != 0:
            print("\n[ПРЕДУПРЕЖДЕНИЕ] Некоторые зависимости могут быть не установлены.")
            print("Попробуйте:")
            print("  python install_deps.py")
            print("Или установите вручную основные пакеты:")
            print("  pip install fastapi uvicorn sqlalchemy rich")
            # Continue anyway - maybe core packages are installed
    
    print("Зависимости установлены!")
    return True


def init_database():
    """Initialize database if needed."""
    db_path = Path("backend/dreamforge.db")
    if not db_path.exists():
        print("Инициализация базы данных...")
        try:
            # Add project root to path
            project_root = Path.cwd()
            sys.path.insert(0, str(project_root))
            
            # Change to project root for imports
            import os
            old_cwd = os.getcwd()
            os.chdir(project_root)
            
            try:
                from backend.src.database.init_db import init_db
                init_db()
                print("База данных инициализирована!")
            finally:
                os.chdir(old_cwd)
        except Exception as e:
            print(f"Ошибка инициализации БД: {e}")
            import traceback
            traceback.print_exc()
            print("Продолжаем без БД...")


def start_backend():
    """Start backend server."""
    print("Запуск бэкенда...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.src.api.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=Path.cwd()
    )
    return backend_process


def start_frontend():
    """Start frontend CLI."""
    print("Запуск фронтенда...")
    time.sleep(2)  # Wait for backend to start
    # Try modern UI first, fallback to old
    try:
        subprocess.run([sys.executable, "-m", "frontend.cli.main_modern"], cwd=Path.cwd())
    except:
        subprocess.run([sys.executable, "-m", "frontend.cli.main"], cwd=Path.cwd())


def main():
    """Main entry point."""
    print("=" * 50)
    print("Dreamforge: Эхо Бездны")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("Зависимости не установлены. Устанавливаем...")
        if not install_dependencies():
            print("Продолжаем с частично установленными зависимостями...")
    
    # Initialize database
    init_database()
    
    # Start backend
    backend = start_backend()
    
    try:
        # Start frontend
        start_frontend()
    except KeyboardInterrupt:
        print("\nОстановка сервера...")
    finally:
        backend.terminate()
        backend.wait()
        print("Сервер остановлен.")


if __name__ == "__main__":
    main()

