"""
Действие close_app: закрытие конкретных окон/приложений или закрытие всех окон кроме терминала K.AI.
"""

import ctypes
import os
import subprocess
import sys
from ctypes import wintypes
from typing import Any, Dict, List, Set, Tuple

# Процессы, которые категорически нельзя завершать при "закрой всё"
PROTECTED_PROCESSES = {
    "explorer.exe",
    "ollama.exe",
    "conhost.exe",
    "cmd.exe",
    "powershell.exe",
    "pwsh.exe",
    "windowsterminal.exe",
    "system",
    "idle",
    "smss.exe",
    "csrss.exe",
    "wininit.exe",
    "services.exe",
    "lsass.exe",
    "svchost.exe",
    "winlogon.exe",
    "dwm.exe",
    "taskmgr.exe",
}

# Системные классы окон Windows, которые нельзя закрывать
PROTECTED_WINDOW_CLASSES = {
    "Progman",
    "WorkerW",
    "Shell_TrayWnd",
    "Shell_SecondaryTrayWnd",
    "Windows.UI.Core.CoreWindow",
}

# Карта популярных пользовательских названий в имена процессов
APP_NAME_MAP: Dict[str, str] = {
    "телеграм": "telegram.exe",
    "telegram": "telegram.exe",
    "тг": "telegram.exe",
    "ватсап": "whatsapp.exe",
    "ватсапп": "whatsapp.exe",
    "вацап": "whatsapp.exe",
    "whatsapp": "whatsapp.exe",
    "блокнот": "notepad.exe",
    "notepad": "notepad.exe",
    "калькулятор": "calc.exe",
    "calc": "calc.exe",
    "хром": "chrome.exe",
    "chrome": "chrome.exe",
    "браузер": "chrome.exe",
    "edge": "msedge.exe",
    "эдж": "msedge.exe",
    "msedge": "msedge.exe",
    "файрфокс": "firefox.exe",
    "firefox": "firefox.exe",
    "vs code": "code.exe",
    "vscode": "code.exe",
    "код": "code.exe",
    "спотифай": "spotify.exe",
    "spotify": "spotify.exe",
    "дискорд": "discord.exe",
    "discord": "discord.exe",
    "проводник": "explorer.exe",
    "word": "winword.exe",
    "ворд": "winword.exe",
    "excel": "excel.exe",
    "эксель": "excel.exe",
    "paint": "mspaint.exe",
    "паинт": "mspaint.exe",
}


def _get_process_name_by_pid(pid: int) -> str:
    """Получает имя исполняемого файла по PID процесса через tasklist или wmic."""
    try:
        res = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        out = res.stdout.strip()
        if out and out.startswith('"'):
            # формат: "notepad.exe","1234","Console","1","10,000 K"
            parts = out.split('","')
            return parts[0].strip('"').lower()
    except Exception:
        pass
    return ""


def get_all_visible_windows() -> List[Tuple[int, str, int]]:
    """
    Возвращает список видимых пользовательских окон: (hwnd, title, pid).
    """
    if sys.platform != "win32":
        return []

    user32 = ctypes.windll.user32
    results: List[Tuple[int, str, int]] = []

    def enum_windows_callback(hwnd: int, lparam: int) -> bool:
        if not user32.IsWindowVisible(hwnd):
            return True

        length = user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return True

        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        title = buff.value.strip()
        if not title:
            return True

        # Проверяем класс окна
        class_buff = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, class_buff, 256)
        cls_name = class_buff.value.strip()
        if cls_name in PROTECTED_WINDOW_CLASSES:
            return True

        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        results.append((hwnd, title, pid.value))
        return True

    wnd_proc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)(enum_windows_callback)
    user32.EnumWindows(wnd_proc, 0)
    return results


def close_window_by_hwnd(hwnd: int) -> bool:
    """Мягко закрывает окно через WM_CLOSE."""
    try:
        user32 = ctypes.windll.user32
        WM_CLOSE = 0x0010
        user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
        return True
    except Exception:
        return False


def close_all_windows_except_self() -> None:
    """
    Закрывает все видимые окна приложений, кроме самого окна терминала K.AI
    и защищённых системных процессов.
    """
    if sys.platform != "win32":
        print("K.AI: Управление окнами доступно только на Windows.")
        return

    kernel32 = ctypes.windll.kernel32
    my_console_hwnd = kernel32.GetConsoleWindow()
    my_pid = os.getpid()
    parent_pid = os.getppid() if hasattr(os, "getppid") else 0

    windows = get_all_visible_windows()
    closed_titles: List[str] = []

    for hwnd, title, pid in windows:
        # Пропускаем своё окно и родительские терминалы
        if hwnd == my_console_hwnd or pid in (my_pid, parent_pid):
            continue

        proc_name = _get_process_name_by_pid(pid)
        if proc_name in PROTECTED_PROCESSES:
            continue

        # Закрываем окно
        if close_window_by_hwnd(hwnd):
            closed_titles.append(title)

    if closed_titles:
        # Убираем дубликаты заголовков
        uniq = list(dict.fromkeys(closed_titles))
        preview = ", ".join(f"«{t}»" for t in uniq[:5])
        if len(uniq) > 5:
            preview += f" и ещё {len(uniq) - 5}"
        print(f"K.AI: Все активные окна закрыты: {preview}. Терминал K.AI сохранён.")
    else:
        print("K.AI: Других активных окон не обнаружено.")


def close_specific_app(target: str) -> None:
    """Закрывает конкретное приложение по имени, алиасу или заголовку окна."""
    target_clean = target.strip().lower()
    if not target_clean:
        print("K.AI: Укажите приложение или окно, которое нужно закрыть.")
        return

    proc_name = APP_NAME_MAP.get(target_clean, target_clean)
    if not proc_name.endswith(".exe"):
        proc_exe = f"{proc_name}.exe"
    else:
        proc_exe = proc_name

    # 1. Попытка закрыть через видимые окна по совпадению заголовка или процесса
    windows = get_all_visible_windows()
    closed_any = False
    for hwnd, title, pid in windows:
        p_name = _get_process_name_by_pid(pid)
        if target_clean in title.lower() or proc_exe == p_name or target_clean in p_name:
            if close_window_by_hwnd(hwnd):
                closed_any = True

    # 2. Попытка taskkill для надёжного завершения процесса
    try:
        res = subprocess.run(
            ["taskkill", "/IM", proc_exe],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if res.returncode == 0 or closed_any:
            print(f"K.AI: Приложение '{target}' закрыто.")
            return
    except Exception:
        pass

    if closed_any:
        print(f"K.AI: Окна приложения '{target}' закрыты.")
    else:
        print(f"K.AI: Приложение '{target}' не найдено среди активных.")


def execute_close_app(args: Dict[str, Any], config: Dict[str, Any]) -> None:
    """Диспетчер действия close_app."""
    target = str(args.get("target") or "").strip()
    all_except_self = bool(args.get("all_except_self", False))

    if all_except_self or target.lower() in ("все", "всё", "все окна", "все приложения", "all", "*"):
        close_all_windows_except_self()
    else:
        close_specific_app(target)

