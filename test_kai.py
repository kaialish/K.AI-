"""
Автоматические тесты для K.AI (v2 — расширенная версия с памятью и новыми действиями).
"""

import io
import json
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import kai

EMPTY_MEMORY = {"aliases": {}, "habits": {}, "notes": []}


class TestKaiAssistant(unittest.TestCase):
    def setUp(self):
        self.config = {
            "model": "qwen2.5:3b-instruct",
            "ollama_url": "http://localhost:11434",
            "timeout": 10.0,
            "ide_command": "code",
            "last_project": "C:\\Projects\\MyApp",
            "browser": "chrome",
            "aliases": {
                "почта": "https://mail.google.com",
                "гитхаб": "https://github.com",
                "ютуб": "https://youtube.com",
            },
        }
        self.memory = dict(EMPTY_MEMORY)

    # 1. Очистка префикса
    def test_strip_prefix(self):
        cases = [
            ("K.AI, засеки таймер", "засеки таймер"),
            ("kai, открой телеграм", "открой телеграм"),
            ("к.ай: открой проект", "открой проект"),
            ("кай открой последнее видео на ютубе", "открой последнее видео на ютубе"),
            ("открой гитхаб", "открой гитхаб"),
            ("K.AI", ""),
        ]
        for src, expected in cases:
            self.assertEqual(kai.strip_assistant_prefix(src), expected)

    # 2. Белый список — блокировка неизвестных действий
    def test_whitelist_protection(self):
        malicious = [
            {"action": "os_system", "args": {"cmd": "calc.exe"}},
            {"action": "shell", "args": {"command": "dir"}},
            {"action": "unknown_action", "args": {}},
        ]
        for item in malicious:
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                res = kai.execute_action(item, self.config, self.memory)
                self.assertIsNone(res)
                self.assertIn("Не понял команду", fake_out.getvalue())

    # 3. Ollama mock — все действия
    def test_ollama_mocked_responses(self):
        actions = [
            ("открой ide", {"action": "open_ide", "args": {}}),
            ("открой последнее видео", {"action": "open_youtube_last", "args": {}}),
            ("открой почту", {"action": "open_url", "args": {"target": "почта"}}),
            ("засеки 10 секунд", {"action": "timer", "args": {"seconds": 10, "label": "10 секунд"}}),
            ("открой телеграм", {"action": "open_app", "args": {"app": "telegram"}}),
            ("выйти", {"action": "exit", "args": {}}),
            ("привет", {"action": "chat", "args": {"reply": "Привет!"}}),
            ("открой блокнот", {"action": "run_app", "args": {"name": "notepad", "args": ""}}),
            ("увеличь громкость", {"action": "system_op", "args": {"op": "volume_up", "value": ""}}),
            ("запомни, что работа это VS Code", {"action": "remember", "args": {"key": "работа", "value": "VS Code", "type": "habit"}}),
            ("что ты запомнил", {"action": "recall", "args": {"key": ""}}),
        ]
        for prompt, expected in actions:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"message": {"content": json.dumps(expected)}}
            with patch("requests.post", return_value=mock_resp):
                result = kai.parse_with_ollama(prompt, self.config, self.memory)
                self.assertEqual(result, expected)

    # 4. Regex fallback — таймеры
    def test_regex_fallback_timer(self):
        cases = [
            ("засеки таймер на 10 секунд", 10),
            ("таймер на 5 минут пицца", 300),
            ("таймер на 90 секунд", 90),
            ("таймер полчаса", 1800),
            ("таймер на час", 3600),
        ]
        for phrase, sec in cases:
            res = kai.parse_with_regex(phrase, self.memory)
            self.assertIsNotNone(res, f"Не распознано: {phrase}")
            self.assertEqual(res["action"], "timer")
            self.assertEqual(res["args"]["seconds"], sec)

    # 5. Regex fallback — приложения
    def test_regex_fallback_apps(self):
        cases = [
            ("открой телеграм", "telegram"),
            ("открой ватсап", "whatsapp"),
        ]
        for phrase, app in cases:
            res = kai.parse_with_regex(phrase, self.memory)
            self.assertEqual(res["action"], "open_app")
            self.assertEqual(res["args"]["app"], app)

    # 6. Regex fallback — IDE, YouTube
    def test_regex_fallback_ide_and_youtube(self):
        self.assertEqual(kai.parse_with_regex("открой проект в ide", self.memory)["action"], "open_ide")
        self.assertEqual(kai.parse_with_regex("открой последнее видео на ютубе", self.memory)["action"], "open_youtube_last")

    # 7. Regex fallback — URL, exit, chat, run_app
    def test_regex_fallback_url_and_exit(self):
        res = kai.parse_with_regex("открой гитхаб", self.memory)
        self.assertEqual(res["action"], "open_url")

        res = kai.parse_with_regex("выход", self.memory)
        self.assertEqual(res["action"], "exit")

        res = kai.parse_with_regex("привет", self.memory)
        self.assertEqual(res["action"], "chat")

        res = kai.parse_with_regex("открой блокнот", self.memory)
        self.assertEqual(res["action"], "run_app")
        self.assertEqual(res["args"]["name"], "notepad")

    # 8. Regex fallback — системные операции
    def test_regex_fallback_system_ops(self):
        cases = [
            ("увеличь громкость", "volume_up"),
            ("уменьши громкость", "volume_down"),
            ("заблокируй экран", "lock"),
        ]
        for phrase, op in cases:
            res = kai.parse_with_regex(phrase, self.memory)
            self.assertIsNotNone(res)
            self.assertEqual(res["action"], "system_op")
            self.assertEqual(res["args"]["op"], op)

    # 9. execute_chat
    def test_execute_chat(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            kai.execute_chat({"reply": "Тестовый ответ"})
            self.assertIn("Тестовый ответ", fake_out.getvalue())

    # 10. execute_exit
    def test_execute_exit(self):
        res = kai.execute_action({"action": "exit", "args": {}}, self.config, self.memory)
        self.assertEqual(res, "exit")

    # 11. execute_remember + recall
    def test_execute_remember_and_recall(self):
        with patch("kai.save_memory"):
            kai.execute_remember({"key": "тест", "value": "тестовое значение", "type": "alias"}, self.config, self.memory)
        self.assertIn("тест", self.memory["aliases"])
        self.assertEqual(self.memory["aliases"]["тест"], "тестовое значение")

        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            kai.execute_recall({"key": "тест"}, self.memory)
            self.assertIn("тестовое значение", fake_out.getvalue())

    # 12. execute_open_url с памятью
    @patch("webbrowser.open")
    def test_execute_open_url_alias(self, mock_web_open):
        kai.execute_open_url({"target": "гитхаб"}, self.config, self.memory)
        mock_web_open.assert_called_once_with("https://github.com")

    # 13. execute_open_app fallback
    @patch("os.startfile", side_effect=OSError)
    @patch("webbrowser.open")
    def test_execute_open_app_fallback(self, mock_web_open, mock_startfile):
        kai.execute_open_app({"app": "telegram"}, self.config)
        mock_web_open.assert_called_once_with("https://web.telegram.org")

    # 14. YouTube с фиктивной БД
    @patch("webbrowser.open")
    def test_execute_open_youtube_last_with_fake_db(self, mock_web_open):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite") as tmp:
            tmp_db = tmp.name
        try:
            conn = sqlite3.connect(tmp_db)
            c = conn.cursor()
            c.execute("CREATE TABLE urls (id INTEGER PRIMARY KEY, url TEXT, title TEXT, last_visit_time INTEGER)")
            c.execute("INSERT INTO urls VALUES (1, 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'Test', 13300000000)")
            conn.commit()
            conn.close()

            with patch("pathlib.Path.exists", return_value=True), \
                 patch("shutil.copy2", side_effect=lambda src, dst: shutil.copyfile(tmp_db, dst)):
                kai.execute_open_youtube_last({}, self.config)
                mock_web_open.assert_called_once_with("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        finally:
            if os.path.exists(tmp_db):
                os.remove(tmp_db)

    # 15. run_app — запуск приложения
    @patch("subprocess.Popen")
    def test_execute_run_app(self, mock_popen):
        kai.execute_run_app({"name": "notepad", "args": ""}, self.config)
        mock_popen.assert_called_once()

    # 16. IDE
    @patch("subprocess.Popen")
    def test_execute_open_ide(self, mock_popen):
        kai.execute_open_ide({}, self.config)
        mock_popen.assert_called_once()


if __name__ == "__main__":
    unittest.main()
