# SPDX-FileCopyrightText: 2026 Dignition
# SPDX-License-Identifier: GPL-3.0-only
"""ЯркостьМонитор — управление яркостью всех мониторов из трея.

Copyright (C) 2026 Dignition (автор: https://github.com/Dignition).
Лицензия: GPL-3.0-only — см. файл LICENSE.
Исходный код: https://github.com/Dignition/yarkost-monitor

Запуск:  pythonw main.py   (или python main.py для вывода ошибок в консоль)
"""
import os
import sys

from PySide6.QtCore import Qt, QSharedMemory
from PySide6.QtGui import (QIcon, QPixmap, QPainter, QColor, QPen,
                           QGuiApplication, QAction)
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu

from qfluentwidgets import setTheme, Theme, isDarkTheme

import config
import monitors
from flyout import FlyoutWindow
from hotkeys import HotkeyManager
from settings_dialog import SettingsDialog, NewProfileDialog, AboutDialog


def resource_path(name: str) -> str:
    """Путь к ресурсу: рядом со скриптом или внутри сборки PyInstaller."""
    base = getattr(sys, "_MEIPASS",
                   os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


def make_tray_icon() -> QIcon:
    """Рисует иконку-солнце (белую в тёмной теме, чёрную в светлой)."""
    color = QColor("white") if isDarkTheme() else QColor("black")
    pm = QPixmap(64, 64)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    pen = QPen(color, 6)
    pen.setCapStyle(Qt.RoundCap)
    p.setPen(pen)
    p.drawEllipse(20, 20, 24, 24)
    import math
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        x1 = 32 + 18 * math.cos(rad)
        y1 = 32 + 18 * math.sin(rad)
        x2 = 32 + 26 * math.cos(rad)
        y2 = 32 + 26 * math.sin(rad)
        p.drawLine(int(x1), int(y1), int(x2), int(y2))
    p.end()
    return QIcon(pm)


def screen_names() -> list[str]:
    names = []
    for i, s in enumerate(QGuiApplication.screens()):
        model = ""
        try:
            model = (s.model() or "").strip()
        except Exception:
            pass
        name = model or s.name().replace("\\\\.\\", "").strip()
        names.append(name or f"Монитор {i + 1}")
    return names


class App:
    def __init__(self, qapp: QApplication):
        self.qapp = qapp
        self.cfg = config.load()
        self.active_profile: str | None = None

        # автозапуском управляют установщик и настройки; при старте
        # просто читаем фактическое состояние из реестра
        if sys.platform == "win32":
            self.cfg["autostart"] = config.get_autostart()

        # мониторы
        self.bridge = monitors.Bridge()
        self.bridge.initial_read.connect(self.on_initial_read)
        self.bridge.monitor_error.connect(self.on_monitor_error)
        self.workers: list[monitors.BaseWorker] = []

        # окно
        self.flyout = FlyoutWindow()
        self.flyout.master_changed.connect(self.on_master_changed)
        self.flyout.monitor_changed.connect(self.on_monitor_changed)
        self.flyout.profile_clicked.connect(self.apply_profile)
        self.flyout.add_profile_clicked.connect(self.on_add_profile)
        self.flyout.settings_clicked.connect(self.on_settings)
        self.flyout.refresh_clicked.connect(self.rescan_monitors)

        # хоткеи
        self.hotkeys = HotkeyManager(self.on_hotkey)
        qapp.installNativeEventFilter(self.hotkeys)
        self.hotkeys.register()

        # трей
        self.tray = QSystemTrayIcon(make_tray_icon())
        self.tray.setToolTip(f"Яркость мониторов {config.APP_VERSION}")
        self.menu = QMenu()
        self.menu.aboutToShow.connect(self.rebuild_tray_menu)
        self.tray.setContextMenu(self.menu)
        self.tray.activated.connect(self.on_tray_activated)
        self.tray.show()

        qapp.aboutToQuit.connect(self.cleanup)
        self.rescan_monitors()

    # ---------- мониторы ----------
    def rescan_monitors(self) -> None:
        monitors.stop_workers(self.workers)
        self.workers = monitors.create_workers(self.bridge, self.cfg,
                                               screen_names())
        self.flyout.set_monitors([w.name for w in self.workers])
        self.refresh_profiles_ui()

    def on_initial_read(self, index: int, value: int) -> None:
        if index < len(self.flyout.rows):
            self.flyout.rows[index].set_value_silent(value)
            self.flyout.update_master_from_rows()

    def on_monitor_error(self, index: int, msg: str) -> None:
        if index < len(self.flyout.rows):
            self.flyout.rows[index].set_unavailable("нет DDC/CI")

    # ---------- ползунки ----------
    def on_master_changed(self, value: int) -> None:
        self.active_profile = None
        for row in self.flyout.rows:
            if row.slider.isEnabled():
                row.set_value_silent(value)
        for w in self.workers:
            if w.alive_ok:
                w.set_target(value)
        self.refresh_profiles_ui()

    def on_monitor_changed(self, index: int, value: int) -> None:
        self.active_profile = None
        if index < len(self.workers):
            self.workers[index].set_target(value)
        self.flyout.update_master_from_rows()
        self.refresh_profiles_ui()

    # ---------- профили ----------
    def find_profile(self, name: str) -> dict | None:
        for p in self.cfg["profiles"]:
            if p["name"] == name:
                return p
        return None

    def apply_profile(self, name: str) -> None:
        prof = self.find_profile(name)
        if prof is None:
            return
        self.active_profile = name
        for key, value in prof.get("values", {}).items():
            try:
                idx = int(key)
            except ValueError:
                continue
            if idx < len(self.workers) and self.workers[idx].alive_ok:
                self.workers[idx].set_target(int(value))
                if idx < len(self.flyout.rows):
                    self.flyout.rows[idx].set_value_silent(int(value))
        self.flyout.update_master_from_rows()
        self.refresh_profiles_ui()

    def on_hotkey(self, slot: int) -> None:
        for p in self.cfg["profiles"]:
            if p.get("slot") == slot:
                self.apply_profile(p["name"])
                return

    def on_add_profile(self) -> None:
        taken = {p["slot"] for p in self.cfg["profiles"] if p.get("slot")}
        default = f"Профиль {len(self.cfg['profiles']) + 1}"
        dlg = NewProfileDialog(taken, default)
        if dlg.exec() and dlg.result_data:
            values = {str(r.index): r.value()
                      for r in self.flyout.rows if r.slider.isEnabled()}
            name = dlg.result_data["name"]
            base, n = name, 2
            while self.find_profile(name):
                name = f"{base} ({n})"
                n += 1
            self.cfg["profiles"].append({"name": name,
                                         "slot": dlg.result_data["slot"],
                                         "values": values})
            config.save(self.cfg)
            self.active_profile = name
            self.refresh_profiles_ui()

    def refresh_profiles_ui(self) -> None:
        self.flyout.set_profiles(self.cfg["profiles"], self.active_profile)

    # ---------- настройки ----------
    def on_settings(self) -> None:
        dlg = SettingsDialog(self.cfg)
        if dlg.exec() and dlg.result_cfg is not None:
            old_autostart = self.cfg.get("autostart")
            self.cfg.clear()
            self.cfg.update(dlg.result_cfg)
            config.save(self.cfg)
            if self.cfg.get("autostart") != old_autostart:
                config.set_autostart(self.cfg["autostart"])
            if self.active_profile and not self.find_profile(self.active_profile):
                self.active_profile = None
            self.refresh_profiles_ui()

    # ---------- трей ----------
    def on_tray_activated(self, reason) -> None:
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.flyout.popup()

    def rebuild_tray_menu(self) -> None:
        self.menu.clear()
        act_open = QAction("Открыть", self.menu)
        act_open.triggered.connect(self.flyout.popup)
        self.menu.addAction(act_open)
        if self.cfg["profiles"]:
            self.menu.addSeparator()
            for p in self.cfg["profiles"]:
                slot = p.get("slot")
                text = p["name"] + (f"\tCtrl+Alt+{slot}" if slot else "")
                act = QAction(text, self.menu)
                act.setCheckable(True)
                act.setChecked(p["name"] == self.active_profile)
                act.triggered.connect(
                    lambda _=False, n=p["name"]: self.apply_profile(n))
                self.menu.addAction(act)
        self.menu.addSeparator()
        act_settings = QAction("Настройки", self.menu)
        act_settings.triggered.connect(self.on_settings)
        self.menu.addAction(act_settings)
        act_about = QAction("О программе", self.menu)
        act_about.triggered.connect(lambda: AboutDialog().exec())
        self.menu.addAction(act_about)
        act_quit = QAction("Выход", self.menu)
        act_quit.triggered.connect(self.qapp.quit)
        self.menu.addAction(act_quit)

    def cleanup(self) -> None:
        self.hotkeys.unregister()
        monitors.stop_workers(self.workers)
        self.tray.hide()


def main() -> int:
    qapp = QApplication(sys.argv)
    qapp.setQuitOnLastWindowClosed(False)
    qapp.setApplicationName("YarkostMonitor")

    # только один экземпляр
    shared = QSharedMemory("YarkostMonitor_single_instance")
    if not shared.create(1):
        return 0

    setTheme(Theme.AUTO)
    ico = resource_path("icon.ico")
    if os.path.exists(ico):
        qapp.setWindowIcon(QIcon(ico))
    app = App(qapp)  # noqa: F841 — держим ссылку
    return qapp.exec()


if __name__ == "__main__":
    sys.exit(main())
