"""
Диспетчер действий: валидация по белому списку ALLOWED_ACTIONS и маршрутизация.
"""

from typing import Any, Dict, Optional

from kai.actions.apps import execute_open_app, execute_run_app
from kai.actions.browser import execute_open_url, execute_open_youtube_last
from kai.actions.chat import execute_chat
from kai.actions.files import execute_file_op
from kai.actions.ide import execute_open_ide
from kai.actions.memory import execute_recall, execute_remember
from kai.actions.system import execute_system_op
from kai.actions.timer import execute_timer
from kai.constants import ALLOWED_ACTIONS


def execute_action(
    action_data: Dict[str, Any],
    config: Dict[str, Any],
    memory: Dict[str, Any],
) -> Optional[str]:
    """
    Валидирует действие по белому списку и исполняет соответствующую функцию.
    Возвращает 'exit' для завершения цикла работы.
    """
    action = action_data.get("action")
    args = action_data.get("args") or {}

    if action not in ALLOWED_ACTIONS:
        print("K.AI: Не понял команду.")
        return None

    if action == "exit":
        print("K.AI: Завершение работы. До свидания!")
        return "exit"
    elif action == "open_ide":
        execute_open_ide(args, config)
    elif action == "open_youtube_last":
        execute_open_youtube_last(args, config)
    elif action == "open_url":
        execute_open_url(args, config, memory)
    elif action == "timer":
        execute_timer(args, config)
    elif action == "open_app":
        execute_open_app(args, config)
    elif action == "chat":
        execute_chat(args)
    elif action == "run_app":
        execute_run_app(args, config)
    elif action == "file_op":
        execute_file_op(args, config)
    elif action == "remember":
        execute_remember(args, config, memory)
    elif action == "recall":
        execute_recall(args, memory)
    elif action == "system_op":
        execute_system_op(args, config)

    return None

