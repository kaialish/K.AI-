"""
Главный цикл консольного приложения K.AI и обработка пользовательских запросов.
"""

from typing import Any, Dict, Optional

from kai.actions.dispatcher import execute_action
from kai.config import load_config, load_memory
from kai.core.fallback import parse_with_regex, strip_assistant_prefix
from kai.core.ollama import ensure_ollama_running, parse_with_ollama
from kai.utils.platform import init_windows_console, set_console_title


def process_query(
    raw_text: str,
    config: Dict[str, Any],
    memory: Dict[str, Any],
) -> Optional[str]:
    """
    Обрабатывает единичный ввод пользователя:
    1. Очищает от обращения 'K.AI'.
    2. Пробует распознать через Ollama с учётом памяти.
    3. При ошибке/недоступности переходит к Regex Fallback.
    4. Исполняет валидированное действие из белого списка.
    """
    text = strip_assistant_prefix(raw_text)
    if not text:
        return None

    action_data = parse_with_ollama(text, config, memory)
    if not action_data:
        action_data = parse_with_regex(text, memory)

    if not action_data:
        print("K.AI: Не понял команду.")
        return None

    return execute_action(action_data, config, memory)


def main() -> None:
    """Точка входа консольного ассистента."""
    init_windows_console()
    set_console_title("K.AI")
    config = load_config()
    memory = load_memory()
    ensure_ollama_running(config)

    print("K.AI запущен. Чем помочь?")
    try:
        while True:
            try:
                user_input = input("K.AI> ")
            except EOFError:
                break

            status = process_query(user_input, config, memory)
            if status == "exit":
                break
    except KeyboardInterrupt:
        print("\nK.AI: Завершение работы.")


if __name__ == "__main__":
    main()

