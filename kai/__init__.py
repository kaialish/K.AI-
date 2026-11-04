"""
K.AI - Пакет консольного AI-ассистента для Windows.
"""

from kai.actions import (
    execute_action,
    execute_chat,
    execute_file_op,
    execute_open_app,
    execute_open_ide,
    execute_open_url,
    execute_open_youtube_last,
    execute_recall,
    execute_remember,
    execute_run_app,
    execute_system_op,
    execute_timer,
)
from kai.app import main, process_query
from kai.config import get_base_dir, load_config, load_memory, save_memory
from kai.constants import (
    ALLOWED_ACTIONS,
    DEFAULT_CONFIG,
    DESTRUCTIVE_FILE_OPS,
    KNOWN_APPS,
    SAFE_SYSTEM_OPS,
)
from kai.core import (
    build_system_prompt,
    ensure_ollama_running,
    parse_with_ollama,
    parse_with_regex,
    strip_assistant_prefix,
)
from kai.utils import (
    get_clipboard,
    init_windows_console,
    press_media_key,
    set_clipboard,
    set_console_title,
)

__all__ = [
    "main",
    "process_query",
    "load_config",
    "load_memory",
    "save_memory",
    "get_base_dir",
    "strip_assistant_prefix",
    "parse_with_ollama",
    "parse_with_regex",
    "build_system_prompt",
    "ensure_ollama_running",
    "execute_action",
    "execute_chat",
    "execute_file_op",
    "execute_open_app",
    "execute_open_ide",
    "execute_open_url",
    "execute_open_youtube_last",
    "execute_recall",
    "execute_remember",
    "execute_run_app",
    "execute_system_op",
    "execute_timer",
    "ALLOWED_ACTIONS",
    "DEFAULT_CONFIG",
    "KNOWN_APPS",
    "SAFE_SYSTEM_OPS",
    "DESTRUCTIVE_FILE_OPS",
    "set_console_title",
    "init_windows_console",
    "press_media_key",
    "set_clipboard",
    "get_clipboard",
]

