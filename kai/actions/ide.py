"""
Действие open_ide: открытие IDE / VS Code с последним проектом из storage.json.
Автоматическое определение пути к VS Code / Antigravity IDE.
"""

import json
import os
import shutil
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional


def resolve_ide_binary(config: Dict[str, Any]) -> str:
    """Определяет реальный путь к исполняемому файлу IDE (VS Code / Antigravity IDE)."""
    configured = str(config.get("ide_command") or "").strip().strip('"').strip("'")
    if configured and os.path.isabs(configured) and os.path.exists(configured):
        return configured

    # Приоритет 1: прямое исполнение Code.exe или Antigravity IDE (без cmd.exe оболочки)
    candidates = [
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
        r"C:\Program Files\Microsoft VS Code\Code.exe",
        r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
        r"K:\Antigravity IDE\Antigravity IDE.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\bin\code.cmd"),
        r"C:\Program Files\Microsoft VS Code\bin\code.cmd",
        r"K:\Microsoft VS Code\Code.exe",
    ]
    for cand in candidates:
        if cand and os.path.exists(cand):
            return cand

    # Приоритет 2: поиск через PATH
    which_cmd = shutil.which(configured or "code")
    if which_cmd and os.path.exists(which_cmd):
        if which_cmd.lower().endswith((".cmd", ".bat")):
            code_exe = os.path.normpath(os.path.join(os.path.dirname(which_cmd), "..", "Code.exe"))
            if os.path.exists(code_exe):
                return code_exe
        return which_cmd

    if configured and os.path.exists(configured):
        return configured

    return "code"


def launch_ide_with_project(project_path: str, config: Dict[str, Any]) -> bool:
    """Запускает IDE с указанной директорией проекта."""
    ide_bin = resolve_ide_binary(config)
    try:
        if ide_bin.lower().endswith((".cmd", ".bat")):
            subprocess.Popen([ide_bin, project_path], shell=True)
        elif os.path.exists(ide_bin):
            subprocess.Popen([ide_bin, project_path])
        else:
            subprocess.Popen(f'"{ide_bin}" "{project_path}"', shell=True)
        return True
    except Exception as e:
        print(f"K.AI: Ошибка запуска IDE ({ide_bin}): {e}")
        return False


def execute_open_ide(args: Dict[str, Any], config: Dict[str, Any]) -> None:
    """Открывает IDE с последним проектом из storage.json VS Code или last_project в config.json."""
    project_path: Optional[str] = None

    appdata = os.getenv("APPDATA")
    if appdata:
        storage_path = Path(appdata) / "Code" / "User" / "globalStorage" / "storage.json"
        try:
            if storage_path.exists():
                with open(storage_path, "r", encoding="utf-8") as f:
                    storage_data = json.load(f)
                win_state = storage_data.get("windowsState", {})
                last_win = win_state.get("lastActiveWindow", {}) if isinstance(win_state, dict) else {}
                candidate_uri = last_win.get("folder") or last_win.get("workspace")
                if not candidate_uri:
                    prof_assoc = storage_data.get("profileAssociations", {})
                    workspaces = prof_assoc.get("workspaces", {}) if isinstance(prof_assoc, dict) else {}
                    if workspaces:
                        candidate_uri = list(workspaces.keys())[-1]
                if candidate_uri and candidate_uri.startswith("file://"):
                    project_path = urllib.request.url2pathname(
                        urllib.parse.unquote(urllib.parse.urlparse(candidate_uri).path)
                    )
        except (OSError, json.JSONDecodeError):
            pass

    if not project_path:
        project_path = config.get("last_project", "").strip() or None

    if not project_path:
        print("K.AI: Последний проект не найден.")
        return

    print(f"K.AI: Открываю IDE с проектом: {project_path}")
    launch_ide_with_project(project_path, config)
