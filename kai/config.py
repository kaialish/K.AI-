"""
Управление конфигурацией (config.json) и долговременной памятью (memory.json).
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

from kai.constants import DEFAULT_CONFIG


def get_base_dir() -> Path:
    """Возвращает базовую директорию рядом с EXE или скриптом."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    # Если запущен из пакета, поднимаемся к корню проекта (где лежит kai.py)
    root = Path(__file__).resolve().parent.parent
    return root


def load_config() -> Dict[str, Any]:
    """Загружает config.json или создаёт его с дефолтными значениями при отсутствии."""
    cfg_path = get_base_dir() / "config.json"
    if not cfg_path.exists():
        try:
            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
        return dict(DEFAULT_CONFIG)
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = dict(DEFAULT_CONFIG)
        merged.update(data)
        return merged
    except Exception:
        return dict(DEFAULT_CONFIG)


def load_memory() -> Dict[str, Any]:
    """Загружает память K.AI: пользовательские алиасы, привычки, история обучения."""
    mem_path = get_base_dir() / "memory.json"
    default: Dict[str, Any] = {"aliases": {}, "habits": {}, "notes": []}
    if not mem_path.exists():
        return default
    try:
        with open(mem_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key in default:
            if key not in data:
                data[key] = default[key]
        return data
    except Exception:
        return default


def save_memory(memory: Dict[str, Any]) -> None:
    """Сохраняет память K.AI в memory.json."""
    mem_path = get_base_dir() / "memory.json"
    try:
        with open(mem_path, "w", encoding="utf-8") as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"K.AI: Не удалось сохранить память: {e}")

