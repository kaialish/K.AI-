"""
Низкоуровневые утилиты Windows: WinAPI, буфер обмена, заголовок консоли, кодировки.
"""

import ctypes
import subprocess
import sys


def init_windows_console() -> None:
    """Настраивает консоль Windows на корректную работу с UTF-8."""
    if sys.platform == "win32":
        try:
            if sys.stdout and hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            if sys.stderr and hasattr(sys.stderr, "reconfigure"):
                sys.stderr.reconfigure(encoding="utf-8", errors="replace")
            if sys.stdin and hasattr(sys.stdin, "reconfigure"):
                sys.stdin.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def set_console_title(title: str = "K.AI") -> None:
    """Устанавливает заголовок окна консоли через WinAPI."""
    try:
        ctypes.windll.kernel32.SetConsoleTitleW(title)
    except Exception:
        pass


def press_media_key(vk_code: int) -> None:
    """Нажимает системную медиа-клавишу через WinAPI (громкость, mute)."""
    try:
        ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
        ctypes.windll.user32.keybd_event(vk_code, 0, 2, 0)  # KEYEVENTF_KEYUP
    except Exception:
        pass


def set_clipboard(text: str) -> None:
    """Помещает текст в буфер обмена Windows."""
    try:
        subprocess.Popen(
            ["powershell", "-Command", f"Set-Clipboard -Value '{text}'"],
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


def get_clipboard() -> str:
    """Получает текущий текст из буфера обмена Windows."""
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-Clipboard"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        return result.stdout.strip() or "(пусто)"
    except Exception:
        return "(не удалось прочитать)"

