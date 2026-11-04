"""
Взаимодействие с локальным сервером Ollama: автозапуск, генерация промптов, вызов LLM и постобработка.
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from typing import Any, Dict, Optional

import requests


def ensure_ollama_running(config: Dict[str, Any]) -> None:
    """
    Проверяет доступность Ollama и при необходимости запускает 'ollama serve' в фоне
    без лишних всплывающих окон консоли.
    """
    ollama_url = config.get("ollama_url", "http://localhost:11434").rstrip("/")
    try:
        r = requests.get(ollama_url, timeout=0.8)
        if r.status_code == 200:
            return
    except Exception:
        pass

    candidates = [
        config.get("ollama_bin"),
        shutil.which("ollama"),
        r"K:\Различные установщики\ollama-windows-amd64\ollama.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe"),
        r"C:\Program Files\Ollama\ollama.exe",
    ]
    ollama_exe = None
    for cand in candidates:
        if cand and os.path.exists(cand):
            ollama_exe = cand
            break

    if not ollama_exe:
        return

    try:
        creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        subprocess.Popen(
            [ollama_exe, "serve"],
            creationflags=creationflags,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        for _ in range(8):
            time.sleep(0.5)
            try:
                r = requests.get(ollama_url, timeout=0.5)
                if r.status_code == 200:
                    break
            except Exception:
                pass
    except Exception:
        pass


def build_system_prompt(memory: Dict[str, Any]) -> str:
    """Формирует системный промпт с учётом памяти пользователя."""
    mem_aliases = memory.get("aliases", {})
    mem_habits = memory.get("habits", {})

    mem_section = ""
    if mem_aliases:
        items = ", ".join(f'"{k}" → {v}' for k, v in list(mem_aliases.items())[:10])
        mem_section += f"\nЗапомненные алиасы пользователя: {items}."
    if mem_habits:
        items = ", ".join(f'"{k}" → {v}' for k, v in list(mem_habits.items())[:10])
        mem_section += f"\nПривычки пользователя: {items}."

    return (
        "Ты — умный консольный AI-ассистент K.AI для Windows. "
        "ВАЖНО: всегда отвечай ТОЛЬКО на русском языке, никогда не используй другие языки. "
        "Преврати фразу пользователя в JSON строго формата: "
        '{"action": "<action_name>", "args": { ... }}\n\n'
        "Разрешённые action и их args:\n"
        '1. "open_ide": {} — открыть IDE / VS Code с последним проектом.\n'
        '2. "open_youtube_last": {} — открыть последнее видео YouTube из истории браузера.\n'
        '3. "open_url": {"target": "<url_or_alias>"} — открыть сайт по URL или алиасу.\n'
        '4. "timer": {"seconds": <int>, "label": "<string>"} — поставить таймер.\n'
        '5. "open_app": {"app": "telegram"|"whatsapp"} — запустить Telegram или WhatsApp.\n'
        '6. "exit": {} — выйти из ассистента.\n'
        '7. "chat": {"reply": "<ответ>"} — свободное общение, вопросы, ответы СТРОГО на русском языке, никогда не используй китайский или английский.\n'
        '8. "run_app": {"name": "<имя_программы>", "args": "<доп_аргументы>"} — запустить любую установленную программу на Windows (notepad, calc, explorer, chrome, spotify, discord, excel, word и др.).\n'
        '9. "file_op": {"op": "copy"|"move"|"delete"|"rename"|"mkdir"|"list", "src": "<путь>", "dst": "<путь_назначения>", "confirm": true|false} — операции с файлами. Для delete, move, rename — всегда "confirm": true.\n'
        '10. "remember": {"key": "<ключ>", "value": "<значение>", "type": "alias"|"habit"} — запомнить алиас или привычку пользователя для будущего использования.\n'
        '11. "recall": {"key": "<ключ>"} — вспомнить что-то из памяти. Если key пустой — показать всё.\n'
        '12. "system_op": {"op": "volume_up"|"volume_down"|"mute"|"clipboard_set"|"clipboard_get"|"shutdown"|"restart"|"sleep"|"lock"|"open_settings", "value": "<опциональное_значение>"} — системные операции Windows.\n'
        '13. "close_app": {"target": "<имя_программы_или_окна_или_все>", "all_except_self": true|false} — закрыть конкретное приложение/окно (телеграм, хром, блокнот) или закрыть всё кроме своего терминала (target: "все", all_except_self: true).\n'
        '14. "find_and_open": {"query": "<имя_файла_или_проекта>", "as_project": true|false} — найти и открыть любой файл на диске без указания пути или найти проект и открыть в IDE.\n'
        "\nПримеры:\n"
        '- "открой блокнот" → {"action": "run_app", "args": {"name": "notepad", "args": ""}}\n'
        '- "закрой телеграм" → {"action": "close_app", "args": {"target": "telegram", "all_except_self": false}}\n'
        '- "закрой все окна кроме терминала" → {"action": "close_app", "args": {"target": "все", "all_except_self": true}}\n'
        '- "открой файл resume.pdf" → {"action": "find_and_open", "args": {"query": "resume.pdf", "as_project": false}}\n'
        '- "открой проект tou_bot" → {"action": "find_and_open", "args": {"query": "tou_bot", "as_project": true}}\n'
        '- "увеличь громкость" → {"action": "system_op", "args": {"op": "volume_up", "value": ""}}\n'
        '- "скопируй C:/file.txt в D:/backup" → {"action": "file_op", "args": {"op": "copy", "src": "C:/file.txt", "dst": "D:/backup", "confirm": false}}\n'
        '- "запомни, что работа — это открыть VS Code и гитхаб" → {"action": "remember", "args": {"key": "работа", "value": "открыть VS Code и гитхаб", "type": "habit"}}\n'
        '- "что ты запомнил?" → {"action": "recall", "args": {"key": ""}}\n'
        f"{mem_section}\n"
        "ВНИМАНИЕ: отвечай ТОЛЬКО чистым валидным JSON без markdown и пояснений. Все текстовые значения (reply, label) пиши ТОЛЬКО на русском языке."
    )


def contains_cjk(text: str) -> bool:
    """Проверяет наличие китайских/японских/корейских символов."""
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


def translate_cjk_greeting(original: str) -> str:
    """Заменяет китайский ответ на русский (для известных шаблонов)."""
    greetings = [
        "Привет! Чем могу помочь?",
        "Здравствуйте! Как могу помочь?",
        "Привет! Я K.AI. Что вас интересует?",
    ]
    idx = int(hashlib.md5(original.encode()).hexdigest(), 16) % len(greetings)
    return greetings[idx]


def parse_with_ollama(
    text: str,
    config: Dict[str, Any],
    memory: Dict[str, Any],
    timeout: Optional[float] = None,
) -> Optional[Dict[str, Any]]:
    """
    Отправляет фразу в Ollama и получает строго JSON-структуру действия.
    Возвращает dict вида {"action": str, "args": dict} или None при ошибке/недоступности.
    """
    if timeout is None:
        timeout = float(config.get("timeout", 12.0))

    ollama_url = config.get("ollama_url", "http://localhost:11434").rstrip("/")
    endpoint = f"{ollama_url}/api/chat"
    model = config.get("model", "qwen2.5:3b-instruct")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": build_system_prompt(memory)},
            {"role": "user", "content": text},
        ],
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.1},
    }

    try:
        resp = requests.post(endpoint, json=payload, timeout=timeout)
        if resp.status_code == 200:
            content = resp.json().get("message", {}).get("content", "").strip()
            data = json.loads(content)
            if isinstance(data, dict) and "action" in data:
                if not isinstance(data.get("args"), dict):
                    data["args"] = {}
                # Постобработка: защита от китайского текста в chat-ответах
                if data["action"] == "chat" and "reply" in data["args"]:
                    reply = data["args"]["reply"]
                    if contains_cjk(reply):
                        data["args"]["reply"] = translate_cjk_greeting(reply)
                return data
    except Exception:
        return None
    return None

