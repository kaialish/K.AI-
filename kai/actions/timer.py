"""
Действие timer: фоновый таймер со звуковым оповещением winsound.
"""

import threading
import time
from typing import Any, Dict


def _timer_worker(seconds: int, label: str) -> None:
    time.sleep(seconds)
    try:
        import winsound

        winsound.Beep(1000, 500)
    except Exception:
        pass
    print(f"\nK.AI: таймер '{label}' завершён.\nK.AI> ", end="", flush=True)


def execute_timer(args: Dict[str, Any], config: Dict[str, Any]) -> None:
    """Запускает неблокирующий таймер в фоновом потоке."""
    try:
        seconds = int(args.get("seconds", 0))
    except (ValueError, TypeError):
        seconds = 0
    label = str(args.get("label") or f"{seconds} сек").strip()
    if seconds <= 0:
        print("K.AI: Время таймера должно быть больше нуля.")
        return
    print(f"K.AI: Таймер '{label}' запущен на {seconds} сек.")
    threading.Thread(target=_timer_worker, args=(seconds, label), daemon=True).start()

