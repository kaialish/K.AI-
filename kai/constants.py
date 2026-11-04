"""
Константы, настройки по умолчанию и списки разрешённых действий для K.AI.
"""

from typing import Any, Dict

ALLOWED_ACTIONS = {
    "open_ide",
    "open_youtube_last",
    "open_url",
    "timer",
    "open_app",
    "exit",
    "chat",
    "run_app",
    "file_op",
    "remember",
    "recall",
    "system_op",
    "close_app",
    "find_and_open",
}

DEFAULT_CONFIG: Dict[str, Any] = {
    "model": "qwen2.5:3b-instruct",
    "ollama_url": "http://localhost:11434",
    "ollama_bin": r"K:\Различные установщики\ollama-windows-amd64\ollama.exe",
    "timeout": 12.0,
    "ide_command": "code",
    "last_project": "",
    "browser": "chrome",
    "aliases": {
        "почта": "https://mail.google.com",
        "гитхаб": "https://github.com",
        "ютуб": "https://youtube.com",
    },
}

KNOWN_APPS: Dict[str, str] = {
    "блокнот": "notepad",
    "notepad": "notepad",
    "калькулятор": "calc",
    "calc": "calc",
    "проводник": "explorer",
    "explorer": "explorer",
    "диспетчер задач": "taskmgr",
    "taskmgr": "taskmgr",
    "paint": "mspaint",
    "реестр": "regedit",
    "cmd": "cmd",
    "командная строка": "cmd",
    "powershell": "powershell",
    "excel": "excel",
    "word": "winword",
    "outlook": "outlook",
    "chrome": "chrome",
    "firefox": "firefox",
    "edge": "msedge",
    "spotify": "spotify",
    "discord": "discord",
    "zoom": "zoom",
    "obs": "obs64",
    "obs studio": "obs64",
    "steam": "steam",
    "snip": "SnippingTool",
    "ножницы": "SnippingTool",
}

SAFE_SYSTEM_OPS = {
    "volume_up",
    "volume_down",
    "mute",
    "clipboard_set",
    "clipboard_get",
    "shutdown",
    "restart",
    "sleep",
    "lock",
    "open_settings",
}

DESTRUCTIVE_FILE_OPS = {"delete", "move", "rename"}

