"""
Действие open_ide: открытие IDE / VS Code с последним проектом из storage.json.
"""

import json
import os
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional


def execute_open_ide(args: Dict[str, Any], config: Dict[str, Any]) -> None:
    """Открывает IDE с последним проектом из storage.json VS Code или last_project в config.json."""
    ide_cmd = config.get("ide_command", "code")
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
    try:
        subprocess.Popen(f'"{ide_cmd}" "{project_path}"', shell=True)
    except Exception as e:
        print(f"K.AI: Ошибка запуска IDE: {e}")

