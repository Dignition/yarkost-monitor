# SPDX-FileCopyrightText: 2026 Dignition
# SPDX-License-Identifier: GPL-3.0-only
"""Глобальные горячие клавиши Ctrl+Alt+1..9 через WinAPI RegisterHotKey."""
import sys

from PySide6.QtCore import QAbstractNativeEventFilter

WM_HOTKEY = 0x0312
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_NOREPEAT = 0x4000


class HotkeyManager(QAbstractNativeEventFilter):
    """Регистрирует Ctrl+Alt+1..9 и вызывает callback(slot) при нажатии.

    Должен создаваться и регистрироваться в главном (GUI) потоке.
    Подключение: app.installNativeEventFilter(manager); manager.register().
    """

    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self._registered: list[int] = []

    def register(self) -> None:
        if sys.platform != "win32":
            return
        import ctypes
        user32 = ctypes.windll.user32
        for slot in range(1, 10):  # VK '1'..'9' = 0x31..0x39
            if user32.RegisterHotKey(None, slot,
                                     MOD_CONTROL | MOD_ALT | MOD_NOREPEAT,
                                     0x30 + slot):
                self._registered.append(slot)

    def unregister(self) -> None:
        if sys.platform != "win32":
            return
        import ctypes
        user32 = ctypes.windll.user32
        for slot in self._registered:
            user32.UnregisterHotKey(None, slot)
        self._registered.clear()

    def nativeEventFilter(self, event_type, message):
        if sys.platform == "win32" and event_type == b"windows_generic_MSG":
            import ctypes.wintypes
            msg = ctypes.wintypes.MSG.from_address(int(message))
            if msg.message == WM_HOTKEY and 1 <= msg.wParam <= 9:
                try:
                    self.callback(int(msg.wParam))
                except Exception:
                    pass
        return False, 0
