"""
Действия open_app и run_app: запуск Telegram/WhatsApp и любых установленных приложений Windows.
"""

import os
import subprocess
import webbrowser
from typing import Any, Dict

from kai.constants import KNOWN_APPS


def execute_open_app(args: Dict[str, Any], config: Dict[str, Any]) -> None:
    """Открывает Telegram или WhatsApp через системный протокол или веб-версию."""
    app = str(args.get("app") or "").strip().lower()
    if "tele" in app or "tg" in app:
        try:
            print("K.AI: Запускаю Telegram...")
            os.startfile("tg://")
        except OSError:
            print("K.AI: Открываю web.telegram.org...")
            webbrowser.open("https://web.telegram.org")
    elif "what" in app or "wa" in app:
        try:
            print("K.AI: Запускаю WhatsApp...")
            os.startfile("whatsapp://")
        except OSError:
            print("K.AI: Открываю web.whatsapp.com...")
            webbrowser.open("https://web.whatsapp.com")
    else:
        print(f"K.AI: Неизвестное приложение '{app}'.")


def execute_run_app(args: Dict[str, Any], config: Dict[str, Any]) -> None:
    """Запускает любую установленную Windows-программу."""
    name = str(args.get("name") or "").strip()
    extra_args = str(args.get("args") or "").strip()

    if not name:
        print("K.AI: Укажите имя программы для запуска.")
        return

    resolved = KNOWN_APPS.get(name.lower(), name)

    if resolved == "calc":
        resolved = "calc.exe"

    cmd = [resolved] + ([extra_args] if extra_args else [])
    print(f"K.AI: Запускаю {resolved}{'  ' + extra_args if extra_args else ''}...")
    try:
        subprocess.Popen(cmd, shell=True)
    except FileNotFoundError:
        try:
            subprocess.Popen(["powershell", "-Command", f"Start-Process '{resolved}'"], shell=True)
        except Exception as e:
            print(f"K.AI: Не удалось запустить '{name}': {e}")
    except Exception as e:
        print(f"K.AI: Ошибка запуска '{name}': {e}")

