"""
Действие find_and_open: умное сканирование дисков и открытие любых файлов или проектов в IDE без указания пути.
"""

import os
import subprocess
import webbrowser
from pathlib import Path
from typing import Any, Dict, List, Optional

from kai.actions.ide import execute_open_ide

# Папки, которые следует пропускать при сканировании для максимальной скорости
IGNORE_DIRS = {
    "$recycle.bin",
    "system volume information",
    "windows",
    "node_modules",
    "__pycache__",
    ".git",
    ".svn",
    ".idea",
    ".vscode-server",
    "appdata",
    "winsxs",
}

# Маркеры директории проекта разработки
PROJECT_MARKERS = {
    ".git",
    "package.json",
    "go.mod",
    "requirements.txt",
    "cargo.toml",
    "pyproject.toml",
    ".vscode",
    "pom.xml",
    "build.gradle",
    "makefile",
    "cmakelists.txt",
}


def get_search_roots() -> List[str]:
    """Возвращает приоритетные корни поиска: сначала пользовательские каталоги, затем диски."""
    roots: List[str] = []
    user_prof = os.getenv("USERPROFILE")
    if user_prof:
        for folder in ["Desktop", "Downloads", "Documents", "Projects", "Source"]:
            p = os.path.join(user_prof, folder)
            if os.path.exists(p):
                roots.append(p)

    # Добавляем доступные системные диски (K:\, D:\, C:\)
    for letter in ["K", "D", "C", "E", "F"]:
        drive = f"{letter}:\\"
        if os.path.exists(drive) and drive not in roots:
            roots.append(drive)

    return roots


def is_project_directory(dirpath: str) -> bool:
    """Проверяет, является ли папка проектом разработки по наличию маркеров."""
    try:
        entries = set(os.listdir(dirpath))
        if any(marker in entries or marker.lower() in {e.lower() for e in entries} for marker in PROJECT_MARKERS):
            return True
    except (OSError, PermissionError):
        pass
    return False


def scan_for_file(query: str, max_depth: int = 5) -> Optional[str]:
    """
    Сканирует диски в поисках файла по названию или подстроке.
    Возвращает полный путь к наиболее свежему совпадению.
    """
    clean_query = query.strip().lower()
    matches: List[str] = []
    roots = get_search_roots()

    for root in roots:
        root_depth = root.rstrip("\\/").count(os.sep)
        for dirpath, dirnames, filenames in os.walk(root, topdown=True):
            # Ограничение глубины поиска
            current_depth = dirpath.count(os.sep) - root_depth
            if current_depth >= max_depth:
                dirnames.clear()
                continue

            # Фильтрация медленных системных каталогов
            dirnames[:] = [
                d for d in dirnames
                if not d.startswith(".") and d.lower() not in IGNORE_DIRS
            ]

            for fname in filenames:
                fname_lower = fname.lower()
                # Точное совпадение имени или расширения
                if clean_query == fname_lower or clean_query in fname_lower:
                    full_path = os.path.join(dirpath, fname)
                    matches.append(full_path)
                    # Если нашли точное совпадение в приоритетной папке — возвращаем сразу
                    if clean_query == fname_lower:
                        return full_path

        # Если уже нашли несколько совпадений на текущем диске, выбираем самый свежий
        if matches:
            break

    if not matches:
        return None

    # Сортируем совпадения по времени последнего изменения (самый свежий — первый)
    try:
        matches.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    except Exception:
        pass

    return matches[0]


def scan_for_project(query: str, max_depth: int = 4) -> Optional[str]:
    """
    Сканирует диски в поисках директории проекта по названию.
    """
    clean_query = query.strip().lower()
    roots = get_search_roots()

    for root in roots:
        root_depth = root.rstrip("\\/").count(os.sep)
        for dirpath, dirnames, _ in os.walk(root, topdown=True):
            current_depth = dirpath.count(os.sep) - root_depth
            if current_depth >= max_depth:
                dirnames.clear()
                continue

            dirnames[:] = [
                d for d in dirnames
                if not d.startswith(".") and d.lower() not in IGNORE_DIRS
            ]

            for dname in dirnames:
                dname_lower = dname.lower()
                if clean_query == dname_lower or clean_query in dname_lower:
                    full_candidate = os.path.join(dirpath, dname)
                    if is_project_directory(full_candidate):
                        return full_candidate

    return None


def execute_find_and_open(args: Dict[str, Any], config: Dict[str, Any]) -> None:
    """
    Находит и открывает файл или проект без указания пути.
    """
    query = str(args.get("query") or args.get("target") or args.get("name") or "").strip()
    as_project = bool(args.get("as_project", False))
    ide_cmd = config.get("ide_command", "code")

    # Если запрос пустой или явный запрос на "последний проект"
    if not query or query.lower() in ("проект", "последний проект", "ide", "vscode"):
        execute_open_ide(args, config)
        return

    # 1. Если запрошен проект (например, "открой проект tou_bot")
    if as_project or "проект" in query.lower():
        proj_name = query.lower().replace("проект", "").strip() or query
        print(f"K.AI: Ищу проект '{proj_name}' на дисках...")
        found_proj = scan_for_project(proj_name)
        if found_proj:
            print(f"K.AI: Проект найден: {found_proj}. Открываю в IDE...")
            try:
                subprocess.Popen(f'"{ide_cmd}" "{found_proj}"', shell=True)
                return
            except Exception as e:
                print(f"K.AI: Ошибка запуска IDE: {e}")
        else:
            print(f"K.AI: Проект '{proj_name}' не найден на доступных дисках.")
            return

    # 2. Поиск и открытие любого файла
    print(f"K.AI: Ищу файл '{query}' на дисках...")
    found_file = scan_for_file(query)
    if found_file:
        print(f"K.AI: Файл найден: {found_file}. Открываю...")
        try:
            os.startfile(found_file)
            return
        except OSError:
            try:
                webbrowser.open(found_file)
                return
            except Exception:
                pass
        except Exception as e:
            print(f"K.AI: Не удалось открыть файл '{found_file}': {e}")
    else:
        print(f"K.AI: Файл '{query}' не найден на дисках (C:, K:, D:).")

