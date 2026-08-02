# SPDX-FileCopyrightText: 2026 Dignition
# SPDX-License-Identifier: GPL-3.0-only
"""Конфигурация: настройки, профили, автозапуск."""
import json
import os
import sys

APP_NAME = "YarkostMonitor"
APP_VERSION = "1.0.0"
REPO_URL = "https://github.com/Dignition/yarkost-monitor"
SOURCE_URL = f"{REPO_URL}/releases/tag/v{APP_VERSION}"


def app_dir() -> str:
    """Каталог приложения: рядом с exe (сборка) или с исходниками."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

DEFAULTS = {
    "smooth": True,          # плавное изменение яркости
    "speed": 1.0,            # множитель скорости анимации
    "autostart": True,       # автозапуск с Windows
    "profiles": [],          # [{"name": str, "slot": int|None, "values": {"0": 80}}]
}


def config_dir() -> str:
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    d = os.path.join(base, APP_NAME)
    os.makedirs(d, exist_ok=True)
    return d


CONFIG_PATH = os.path.join(config_dir(), "config.json")


def load() -> dict:
    cfg = dict(DEFAULTS)
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            cfg.update(data)
    except (OSError, ValueError):
        pass
    if not isinstance(cfg.get("profiles"), list):
        cfg["profiles"] = []
    return cfg


def save(cfg: dict) -> None:
    tmp = CONFIG_PATH + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        os.replace(tmp, CONFIG_PATH)
    except OSError:
        pass


def _autostart_command() -> str:
    if getattr(sys, "frozen", False):  # собрано pyinstaller'ом
        return f'"{sys.executable}"'
    exe = sys.executable
    pythonw = os.path.join(os.path.dirname(exe), "pythonw.exe")
    if os.path.exists(pythonw):
        exe = pythonw
    script = os.path.abspath(os.path.join(os.path.dirname(__file__), "main.py"))
    return f'"{exe}" "{script}"'


def get_autostart() -> bool:
    """Есть ли сейчас запись автозапуска в реестре."""
    if sys.platform != "win32":
        return False
    import winreg
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.QueryValueEx(key, APP_NAME)
        return True
    except OSError:
        return False


def set_autostart(enabled: bool) -> None:
    """Включает/выключает автозапуск через реестр (HKCU\\...\\Run)."""
    if sys.platform != "win32":
        return
    import winreg
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0,
                            winreg.KEY_SET_VALUE) as key:
            if enabled:
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ,
                                  _autostart_command())
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                except FileNotFoundError:
                    pass
    except OSError:
        pass
