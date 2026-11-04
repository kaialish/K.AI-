"""
Запасной разбор команд по регулярным выражениям и ключевым словам при недоступности Ollama.
"""

import re
from typing import Any, Dict, Optional

from kai.constants import KNOWN_APPS


def strip_assistant_prefix(text: str) -> str:
    """Отбрасывает обращение к ассистенту в начале фразы."""
    pattern = r"^(?:k\.ai|kai|к\.ай|кай)[\s,:\-–—]*"
    return re.sub(pattern, "", text.strip(), flags=re.IGNORECASE).strip()


def parse_with_regex(text: str, memory: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Запасной разбор по ключевым словам при недоступности Ollama."""
    cleaned = text.strip().lower()
    if not cleaned:
        return None

    # Проверка привычек пользователя из памяти
    habits = memory.get("habits", {})
    for key, value in habits.items():
        if key.lower() in cleaned:
            return {
                "action": "chat",
                "args": {
                    "reply": f"Привычка '{key}': {value}. (Выполнение по привычке пока требует Ollama)"
                },
            }

    # 1. Выход
    if re.search(r"^(выход|выйти|exit|quit|закройся|пока|стоп)$", cleaned):
        return {"action": "exit", "args": {}}

    # 2. Таймер
    if "полтора часа" in cleaned:
        return {"action": "timer", "args": {"seconds": 5400, "label": "полтора часа"}}
    if "полчаса" in cleaned:
        return {"action": "timer", "args": {"seconds": 1800, "label": "полчаса"}}
    if re.search(r"\b(?:на\s+)?(?:один\s+|1\s+)?час\b", cleaned):
        return {"action": "timer", "args": {"seconds": 3600, "label": "1 час"}}
    m = re.search(
        r"(?:таймер|засеки|поставь\s+таймер)(?:\s+на)?\s+(\d+)\s*(сек\w*|с\b|мин\w*|м\b|час\w*|ч\b)?(?:\s+(.+))?",
        cleaned,
    )
    if m:
        val = int(m.group(1))
        unit = m.group(2) or "сек"
        label = m.group(3) or f"{val} {unit}"
        seconds = val
        if re.match(r"^(мин\w*|м)$", unit):
            seconds = val * 60
        elif re.match(r"^(час\w*|ч)$", unit):
            seconds = val * 3600
        return {"action": "timer", "args": {"seconds": seconds, "label": label.strip()}}

    # 3. YouTube
    if re.search(r"(последн\w*\s+видео|ютуб.*последн|youtube.*last)", cleaned):
        return {"action": "open_youtube_last", "args": {}}

    # 4. IDE
    if re.search(
        r"\b(открой\s+проект\s+в\s+ide|открой\s+ide|открой\s+проект|открой\s+код|vs\s*code|vscode)\b",
        cleaned,
    ):
        return {"action": "open_ide", "args": {}}

    # 5. Telegram / WhatsApp
    if re.search(r"\b(телеграм|telegram|тг|tg)\b", cleaned):
        return {"action": "open_app", "args": {"app": "telegram"}}
    if re.search(r"\b(ватсап\w*|whatsapp)\b", cleaned):
        return {"action": "open_app", "args": {"app": "whatsapp"}}

    # 6. Системные операции
    if re.search(r"(увелич\w*\s+громкость|громче)", cleaned):
        return {"action": "system_op", "args": {"op": "volume_up", "value": ""}}
    if re.search(r"(уменьш\w*\s+громкость|тише)", cleaned):
        return {"action": "system_op", "args": {"op": "volume_down", "value": ""}}
    if re.search(r"(выключ\w*\s+звук|без\s+звука|mute)", cleaned):
        return {"action": "system_op", "args": {"op": "mute", "value": ""}}
    if re.search(r"(заблокируй\s+экран|lock|заблокировать)", cleaned):
        return {"action": "system_op", "args": {"op": "lock", "value": ""}}
    if re.search(r"(выключ\w*\s+компьютер|shutdown|выключи\s+пк)", cleaned):
        return {"action": "system_op", "args": {"op": "shutdown", "value": ""}}
    if re.search(r"(перезагруз\w*|restart|перезапуст\w*)", cleaned):
        return {"action": "system_op", "args": {"op": "restart", "value": ""}}
    if re.search(r"(спящий\s+режим|sleep|усыпи)", cleaned):
        return {"action": "system_op", "args": {"op": "sleep", "value": ""}}
    if re.search(r"(открой\s+настройки|settings|параметры\s+виндоус)", cleaned):
        return {"action": "system_op", "args": {"op": "open_settings", "value": ""}}

    # 7. Запуск приложений
    for app_key, app_exe in KNOWN_APPS.items():
        if app_key in cleaned:
            return {"action": "run_app", "args": {"name": app_exe, "args": ""}}

    # 8. Запомнить
    m_rem = re.search(r"запомни,?\s+что\s+(.+?)\s+(?:это|—|-|=|:)\s+(.+)", cleaned)
    if m_rem:
        return {
            "action": "remember",
            "args": {
                "key": m_rem.group(1).strip(),
                "value": m_rem.group(2).strip(),
                "type": "alias",
            },
        }

    # 9. Вспомнить
    if re.search(r"(что\s+ты\s+запомнил|вспомни|recall|покажи\s+память)", cleaned):
        return {"action": "recall", "args": {"key": ""}}

    # 10. URL или алиас
    m_url = re.search(r"^(?:открой|перейди\s+на|сайт)\s+(.+)$", cleaned)
    if m_url:
        return {"action": "open_url", "args": {"target": m_url.group(1).strip()}}
    if cleaned.startswith("http://") or cleaned.startswith("https://"):
        return {"action": "open_url", "args": {"target": cleaned}}

    # 11. Приветствия / общение
    if re.search(r"^(привет|здравствуй\w*|хай|хей|ку|hi|hello)$", cleaned):
        return {"action": "chat", "args": {"reply": "Привет! Чем могу помочь?"}}
    if re.search(r"^(что\s+ты\s+умеешь|помощь|help|команды)$", cleaned):
        return {
            "action": "chat",
            "args": {
                "reply": "Я умею запускать программы, управлять файлами, ставить таймеры, открывать сайты, управлять системой Windows и запоминать ваши предпочтения!"
            },
        }

    return None

