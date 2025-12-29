"""Alternative dependency installer that handles Rust compilation issues."""

import subprocess
import sys
from pathlib import Path


def install_without_rust():
    """Install dependencies that don't require Rust compilation."""
    print("Установка зависимостей без компиляции...")
    
    # Core packages that should have wheels
    packages = [
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.20.0",
        "sqlalchemy>=2.0.0",
        "alembic>=1.10.0",
        "pydantic>=2.0.0,<2.10.0",  # Use version with wheels
        "pydantic-settings>=2.0.0",
        "python-dotenv>=1.0.0",
        "python-multipart>=0.0.6",
        "rich>=13.0.0",
        "prompt-toolkit>=3.0.0",
        "requests>=2.28.0",
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.0.0",
    ]
    
    for package in packages:
        print(f"Установка {package}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"  [ПРЕДУПРЕЖДЕНИЕ] Не удалось установить {package}")
            print(f"  {result.stderr[:200]}")
        else:
            print(f"  [OK] {package} установлен")
    
    print("\nПроверка установленных пакетов...")
    try:
        import fastapi
        import rich
        import sqlalchemy
        print("[OK] Основные пакеты установлены!")
        return True
    except ImportError as e:
        print(f"[ОШИБКА] Не удалось импортировать: {e}")
        return False


if __name__ == "__main__":
    install_without_rust()

