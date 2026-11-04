"""
Действия remember и recall: сохранение и воспроизведение пользовательских алиасов и привычек.
"""

from typing import Any, Dict

from kai.config import save_memory


def execute_remember(
    args: Dict[str, Any],
    config: Dict[str, Any],
    memory: Dict[str, Any],
) -> None:
    """Запоминает алиас или привычку пользователя в memory.json."""
    key = str(args.get("key") or "").strip()
    value = str(args.get("value") or "").strip()
    kind = str(args.get("type") or "alias").strip().lower()

    if not key or not value:
        print("K.AI: Укажите, что запомнить (ключ и значение).")
        return

    if kind == "habit":
        memory.setdefault("habits", {})[key] = value
    else:
        memory.setdefault("aliases", {})[key] = value

    save_memory(memory)
    print(f"K.AI: Запомнил! «{key}» = {value}")


def execute_recall(args: Dict[str, Any], memory: Dict[str, Any]) -> None:
    """Выводит запомненные данные."""
    key = str(args.get("key") or "").strip()

    aliases = memory.get("aliases", {})
    habits = memory.get("habits", {})

    if key:
        found = aliases.get(key) or habits.get(key)
        if found:
            print(f"K.AI: «{key}» → {found}")
        else:
            print(f"K.AI: Ничего не найдено для «{key}».")
        return

    if not aliases and not habits:
        print("K.AI: Память пуста. Используй «запомни, что … это …» чтобы научить меня.")
        return

    if aliases:
        print("K.AI: Алиасы:")
        for k, v in aliases.items():
            print(f"  • {k} → {v}")
    if habits:
        print("K.AI: Привычки:")
        for k, v in habits.items():
            print(f"  • {k} → {v}")

