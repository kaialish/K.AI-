"""
Действия open_youtube_last и open_url: открытие последнего видео YouTube и сайтов по URL или алиасам.
"""

import os
import re
import shutil
import sqlite3
import tempfile
import webbrowser
from pathlib import Path
from typing import Any, Dict, Optional


def execute_open_youtube_last(args: Dict[str, Any], config: Dict[str, Any]) -> None:
    """Копирует файл истории браузера во временный файл и открывает самое свежее видео YouTube."""
    local_app_data = os.getenv("LOCALAPPDATA", "")
    pref_browser = config.get("browser", "chrome").lower()
    chrome_hist = Path(local_app_data) / "Google" / "Chrome" / "User Data" / "Default" / "History"
    edge_hist = Path(local_app_data) / "Microsoft" / "Edge" / "User Data" / "Default" / "History"

    candidates = [edge_hist, chrome_hist] if pref_browser == "edge" else [chrome_hist, edge_hist]
    history_file: Optional[Path] = None
    for cand in candidates:
        try:
            if cand.exists():
                history_file = cand
                break
        except OSError:
            continue

    if not history_file:
        print("K.AI: Файл истории браузера не найден.")
        return

    temp_db_path: Optional[str] = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite") as tmp:
            temp_db_path = tmp.name
        shutil.copy2(history_file, temp_db_path)
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT url, title FROM urls "
            "WHERE url LIKE '%youtube.com/watch?v=%' "
            "ORDER BY last_visit_time DESC LIMIT 1"
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            url, title = row[0], row[1]
            print(f"K.AI: Открываю: {url}{' (' + title + ')' if title else ''}")
            webbrowser.open(url)
        else:
            print("K.AI: Видео YouTube не найдено в истории браузера.")
    except Exception as e:
        print(f"K.AI: Ошибка чтения истории: {e}")
    finally:
        if temp_db_path and os.path.exists(temp_db_path):
            try:
                os.remove(temp_db_path)
            except Exception:
                pass


def execute_open_url(
    args: Dict[str, Any],
    config: Dict[str, Any],
    memory: Dict[str, Any],
) -> None:
    """Открывает сайт по алиасу из памяти/конфига или по прямому URL."""
    target = str(args.get("target") or args.get("url") or "").strip()
    if not target:
        target = input("K.AI: Введите алиас или URL: ").strip()
        if not target:
            return

    mem_aliases = {k.lower(): v for k, v in memory.get("aliases", {}).items()}
    cfg_aliases = {k.lower(): v for k, v in config.get("aliases", {}).items()}
    all_aliases = {**cfg_aliases, **mem_aliases}

    target_lower = target.lower()
    if target_lower in all_aliases:
        url = all_aliases[target_lower]
        print(f"K.AI: Открываю '{target}': {url}")
        webbrowser.open(url)
        return

    if target.startswith("http://") or target.startswith("https://"):
        print(f"K.AI: Открываю: {target}")
        webbrowser.open(target)
        return

    if re.match(r"^[a-zA-Z0-9\-]+(?:\.[a-zA-Z0-9\-]+)+(?:/.*)?$", target):
        url = f"https://{target}"
        print(f"K.AI: Открываю {url}")
        webbrowser.open(url)
        return

    print(f"K.AI: Алиас '{target}' не найден.")
    user_url = input(f"K.AI: Введите URL для '{target}' (или Enter для отмены): ").strip()
    if user_url:
        if not (user_url.startswith("http://") or user_url.startswith("https://")):
            user_url = f"https://{user_url}"
        webbrowser.open(user_url)

