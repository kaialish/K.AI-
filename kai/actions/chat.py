"""
Действие chat: вывод дружелюбных ответов и свободный диалог с пользователем.
"""

from typing import Any, Dict


def execute_chat(args: Dict[str, Any]) -> None:
    """Выводит ответ нейросети в режиме диалога/общения."""
    reply = str(args.get("reply") or "Чем могу помочь?").strip()
    print(f"K.AI: {reply}")

