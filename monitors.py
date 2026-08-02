# SPDX-FileCopyrightText: 2026 Dignition
# SPDX-License-Identifier: GPL-3.0-only
"""Работа с мониторами.

Внешние мониторы — по DDC/CI (библиотека monitorcontrol),
встроенный экран ноутбука — по WMI (пакет wmi).

Каждый монитор обслуживается своим потоком, который при старте
читает текущую яркость, а затем плавно ведёт её к целевому значению.
"""
import sys
import threading
import time

from PySide6.QtCore import QObject, Signal

try:
    from monitorcontrol import get_monitors
except ImportError:
    get_monitors = None


class Bridge(QObject):
    """Сигналы из потоков мониторов в GUI."""
    initial_read = Signal(int, int)   # index, brightness (0..100)
    monitor_error = Signal(int, str)  # index, message


class BaseWorker(threading.Thread):
    """Поток одного монитора: чтение яркости и плавное изменение."""

    def __init__(self, index: int, name: str, bridge: Bridge, settings: dict):
        super().__init__(daemon=True)
        self.index = index
        self.name = name
        self.bridge = bridge
        self.settings = settings  # живая ссылка на конфиг
        self.current: int | None = None
        self.target: int | None = None
        self.alive_ok = True
        self._cond = threading.Condition()
        self._stopped = False  # не "_stop": имя занято внутри threading.Thread

    # ---- API для GUI ----
    def set_target(self, value: int) -> None:
        with self._cond:
            self.target = max(0, min(100, int(value)))
            self._cond.notify()

    def stop(self) -> None:
        with self._cond:
            self._stopped = True
            self._cond.notify()

    # ---- переопределяется в наследниках ----
    def _open(self) -> None: ...
    def _read(self) -> int: raise NotImplementedError
    def _write(self, value: int) -> None: raise NotImplementedError

    def run(self) -> None:
        try:
            self._open()
            value = self._read()
            with self._cond:
                self.current = value
                if self.target is None:
                    self.target = value
            self.bridge.initial_read.emit(self.index, value)
        except Exception as e:
            self.alive_ok = False
            self.bridge.monitor_error.emit(self.index, str(e))
            return
        self._loop()

    def _loop(self) -> None:
        errors = 0
        while True:
            with self._cond:
                while not self._stopped and self.target == self.current:
                    self._cond.wait(timeout=1.0)
                if self._stopped:
                    return
                target = self.target
            if self.settings.get("smooth", True):
                delta = target - self.current
                step = max(1, min(8, round(abs(delta) * 0.25)))
                new = self.current + (step if delta > 0 else -step)
            else:
                new = target
            try:
                self._write(new)
                self.current = new
                errors = 0
            except Exception:
                errors += 1
                if errors > 10:
                    self.alive_ok = False
                    self.bridge.monitor_error.emit(
                        self.index, "монитор перестал отвечать")
                    return
                time.sleep(1.0)  # монитор мог уснуть — подождём
                continue
            if self.settings.get("smooth", True):
                speed = max(0.1, float(self.settings.get("speed", 1.0)))
                time.sleep(0.03 / speed)


class DDCWorker(BaseWorker):
    """Внешний монитор по DDC/CI."""

    def __init__(self, monitor, index, name, bridge, settings):
        super().__init__(index, name, bridge, settings)
        self.monitor = monitor

    def _read(self) -> int:
        with self.monitor:
            return int(self.monitor.get_luminance())

    def _write(self, value: int) -> None:
        with self.monitor:
            self.monitor.set_luminance(int(value))


class WMIWorker(BaseWorker):
    """Встроенный экран ноутбука по WMI."""

    def _open(self) -> None:
        import pythoncom
        pythoncom.CoInitialize()
        import wmi
        self._wmi = wmi.WMI(namespace="wmi")
        self._methods = self._wmi.WmiMonitorBrightnessMethods()[0]

    def _read(self) -> int:
        return int(self._wmi.WmiMonitorBrightness()[0].CurrentBrightness)

    def _write(self, value: int) -> None:
        self._methods.WmiSetBrightness(Timeout=0, Brightness=int(value))


def _wmi_available() -> bool:
    if sys.platform != "win32":
        return False
    try:
        import pythoncom
        pythoncom.CoInitialize()
        import wmi
        return len(wmi.WMI(namespace="wmi").WmiMonitorBrightness()) > 0
    except Exception:
        return False


def create_workers(bridge: Bridge, settings: dict,
                   screen_names: list[str]) -> list[BaseWorker]:
    """Находит все мониторы и запускает по потоку на каждый."""
    workers: list[BaseWorker] = []
    idx = 0
    if get_monitors is not None:
        try:
            ddc_monitors = get_monitors()
        except Exception:
            ddc_monitors = []
        for m in ddc_monitors:
            name = (screen_names[idx] if idx < len(screen_names)
                    else f"Монитор {idx + 1}")
            workers.append(DDCWorker(m, idx, name, bridge, settings))
            idx += 1
    if _wmi_available():
        workers.append(WMIWorker(idx, "Встроенный экран", bridge, settings))
        idx += 1
    for w in workers:
        w.start()
    return workers


def stop_workers(workers: list[BaseWorker]) -> None:
    for w in workers:
        w.stop()
