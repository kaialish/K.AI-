"""
K.AI - Консольный AI-ассистент для Windows.
Точка входа приложения. Архитектура и модули вынесены в пакет kai/.
"""

import sys
from pathlib import Path

# Обеспечиваем доступ к модулям пакета kai при прямом запуске скрипта
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from kai import (
    ALLOWED_ACTIONS,
    DEFAULT_CONFIG,
    DESTRUCTIVE_FILE_OPS,
    KNOWN_APPS,
    SAFE_SYSTEM_OPS,
    build_system_prompt,
    ensure_ollama_running,
    execute_action,
    execute_chat,
    execute_close_app,
    execute_file_op,
    execute_find_and_open,
    execute_open_app,
    execute_open_ide,
    execute_open_url,
    execute_open_youtube_last,
    execute_recall,
    execute_remember,
    execute_run_app,
    execute_system_op,
    execute_timer,
    get_base_dir,
    get_clipboard,
    init_windows_console,
    load_config,
    load_memory,
    main,
    parse_with_ollama,
    parse_with_regex,
    press_media_key,
    process_query,
    save_memory,
    set_clipboard,
    set_console_title,
    strip_assistant_prefix,
)

if __name__ == "__main__":
    main()
