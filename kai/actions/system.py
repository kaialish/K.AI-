"""
Действие system_op: управление громкостью, буфером обмена, блокировкой, питанием и настройками Windows.
"""

import ctypes
import subprocess
from typing import Any, Dict

from kai.utils.platform import get_clipboard, press_media_key, set_clipboard


def execute_system_op(args: Dict[str, Any], config: Dict[str, Any]) -> None:
    """Выполняет системные операции Windows."""
    op = str(args.get("op") or "").strip().lower()
    value = str(args.get("value") or "").strip()

    if op == "volume_up":
        press_media_key(0xAF)  # VK_VOLUME_UP
        print("K.AI: Громкость увеличена.")
    elif op == "volume_down":
        press_media_key(0xAE)  # VK_VOLUME_DOWN
        print("K.AI: Громкость уменьшена.")
    elif op == "mute":
        press_media_key(0xAD)  # VK_VOLUME_MUTE
        print("K.AI: Звук переключён.")
    elif op == "lock":
        ctypes.windll.user32.LockWorkStation()
        print("K.AI: Экран заблокирован.")
    elif op == "sleep":
        confirm = input("K.AI: Перевести компьютер в спящий режим? [y/N]: ").strip().lower()
        if confirm in ("y", "yes", "д", "да"):
            subprocess.Popen(
                [
                    "powershell",
                    "-Command",
                    "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState('Suspend', $false, $false)",
                ],
                shell=True,
            )
    elif op == "shutdown":
        confirm = input("K.AI: Выключить компьютер? [y/N]: ").strip().lower()
        if confirm in ("y", "yes", "д", "да"):
            print("K.AI: Выключаю компьютер...")
            subprocess.Popen(["shutdown", "/s", "/t", "5"], shell=True)
    elif op == "restart":
        confirm = input("K.AI: Перезагрузить компьютер? [y/N]: ").strip().lower()
        if confirm in ("y", "yes", "д", "да"):
            print("K.AI: Перезагружаю...")
            subprocess.Popen(["shutdown", "/r", "/t", "5"], shell=True)
    elif op == "clipboard_set":
        if value:
            set_clipboard(value)
            print(f"K.AI: Скопировано в буфер обмена: {value}")
        else:
            text = input("K.AI: Что скопировать в буфер? ").strip()
            if text:
                set_clipboard(text)
                print("K.AI: Скопировано.")
    elif op == "clipboard_get":
        text = get_clipboard()
        print(f"K.AI: В буфере обмена: {text}")
    elif op == "open_settings":
        subprocess.Popen(["ms-settings:"], shell=True)
        print("K.AI: Открываю Настройки Windows.")
    else:
        print(f"K.AI: Неизвестная системная операция '{op}'.")

