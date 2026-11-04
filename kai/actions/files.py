"""
Действие file_op: безопасные операции с файлами (list, mkdir, copy, move, rename, delete с подтверждением).
"""

import os
import shutil
from typing import Any, Dict

from kai.constants import DESTRUCTIVE_FILE_OPS


def execute_file_op(args: Dict[str, Any], config: Dict[str, Any]) -> None:
    """Выполняет операции с файлами. Деструктивные — только с подтверждением пользователя."""
    op = str(args.get("op") or "").strip().lower()
    src = str(args.get("src") or "").strip()
    dst = str(args.get("dst") or "").strip()
    need_confirm = args.get("confirm", op in DESTRUCTIVE_FILE_OPS)

    if not op:
        print("K.AI: Не указана операция с файлом.")
        return

    if op == "list":
        target = src or "."
        try:
            items = os.listdir(target)
            print(f"K.AI: Содержимое '{target}':")
            for item in sorted(items):
                full = os.path.join(target, item)
                kind = "📁" if os.path.isdir(full) else "📄"
                print(f"  {kind} {item}")
        except Exception as e:
            print(f"K.AI: Ошибка просмотра '{target}': {e}")
        return

    if op == "mkdir":
        if not src:
            print("K.AI: Укажите путь для создания папки.")
            return
        try:
            os.makedirs(src, exist_ok=True)
            print(f"K.AI: Папка '{src}' создана.")
        except Exception as e:
            print(f"K.AI: Ошибка создания папки: {e}")
        return

    if need_confirm:
        action_name = {"delete": "Удалить", "move": "Переместить", "rename": "Переименовать"}.get(op, op)
        preview = f"'{src}'" + (f" → '{dst}'" if dst else "")
        confirm = input(f"K.AI: {action_name} {preview}? [y/N]: ").strip().lower()
        if confirm not in ("y", "yes", "д", "да"):
            print("K.AI: Операция отменена.")
            return

    try:
        if op == "copy":
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            print(f"K.AI: Скопировано '{src}' → '{dst}'.")
        elif op == "move":
            shutil.move(src, dst)
            print(f"K.AI: Перемещено '{src}' → '{dst}'.")
        elif op == "delete":
            if os.path.isdir(src):
                shutil.rmtree(src)
            else:
                os.remove(src)
            print(f"K.AI: Удалено '{src}'.")
        elif op == "rename":
            os.rename(src, dst)
            print(f"K.AI: Переименовано '{src}' → '{dst}'.")
        else:
            print(f"K.AI: Неизвестная операция '{op}'.")
    except Exception as e:
        print(f"K.AI: Ошибка операции '{op}': {e}")

