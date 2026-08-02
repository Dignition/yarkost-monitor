# SPDX-FileCopyrightText: 2026 Dignition
# SPDX-License-Identifier: GPL-3.0-only
"""Всплывающее окно у трея в стиле Windows 11."""
from PySide6.QtCore import (Qt, Signal, QPoint, QPropertyAnimation,
                            QEasingCurve, QParallelAnimationGroup)
from PySide6.QtGui import QPainter, QColor, QPainterPath, QGuiApplication
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame,
                               QSizePolicy)

from qfluentwidgets import (Slider, StrongBodyLabel, BodyLabel, CaptionLabel,
                            TransparentToolButton, FluentIcon, IconWidget,
                            isDarkTheme, FlowLayout)

try:
    from qfluentwidgets import PillPushButton as ProfileButton
except ImportError:  # старые версии qfluentwidgets
    from qfluentwidgets import TogglePushButton as ProfileButton

RADIUS = 12
WIDTH = 380


class _Separator(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(1)
        color = "rgba(255,255,255,20)" if isDarkTheme() else "rgba(0,0,0,25)"
        self.setStyleSheet(f"background:{color}; border:none;")


class MonitorRow(QWidget):
    """Строка одного монитора: имя, ползунок, значение."""
    changed = Signal(int, int)  # index, value

    def __init__(self, index: int, name: str, parent=None):
        super().__init__(parent)
        self.index = index
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 4, 0, 4)
        v.setSpacing(2)

        self.name_label = CaptionLabel(name)
        self.name_label.setStyleSheet("CaptionLabel{color: gray;}")
        v.addWidget(self.name_label)

        h = QHBoxLayout()
        h.setSpacing(10)
        self.slider = Slider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        self.slider.valueChanged.connect(
            lambda val: self.changed.emit(self.index, val))
        self.value_label = BodyLabel("--")
        self.value_label.setFixedWidth(34)
        self.value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        h.addWidget(self.slider, 1)
        h.addWidget(self.value_label)
        v.addLayout(h)

        self.slider.valueChanged.connect(
            lambda val: self.value_label.setText(str(val)))

    def set_value_silent(self, value: int) -> None:
        self.slider.blockSignals(True)
        self.slider.setValue(int(value))
        self.slider.blockSignals(False)
        self.value_label.setText(str(int(value)))

    def value(self) -> int:
        return self.slider.value()

    def set_unavailable(self, msg: str) -> None:
        self.slider.setEnabled(False)
        self.value_label.setText("—")
        self.name_label.setText(f"{self.name_label.text()}  ({msg})")


class FlyoutWindow(QWidget):
    """Окно у трея: общий ползунок, мониторы, профили."""
    master_changed = Signal(int)
    monitor_changed = Signal(int, int)
    profile_clicked = Signal(str)
    add_profile_clicked = Signal()
    settings_clicked = Signal()
    refresh_clicked = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint |
                            Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(WIDTH)
        self.rows: list[MonitorRow] = []
        self._anim = None
        self._build()

    # ---------- построение ----------
    def _build(self) -> None:
        self.vbox = QVBoxLayout(self)
        self.vbox.setContentsMargins(20, 16, 20, 16)
        self.vbox.setSpacing(8)

        # заголовок
        header = QHBoxLayout()
        header.setSpacing(4)
        title = StrongBodyLabel("Яркость")
        self.refresh_btn = TransparentToolButton(FluentIcon.SYNC)
        self.refresh_btn.setToolTip("Найти мониторы заново")
        self.refresh_btn.clicked.connect(self.refresh_clicked)
        self.settings_btn = TransparentToolButton(FluentIcon.SETTING)
        self.settings_btn.setToolTip("Настройки")
        self.settings_btn.clicked.connect(self.settings_clicked)
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(self.refresh_btn)
        header.addWidget(self.settings_btn)
        self.vbox.addLayout(header)

        # общий ползунок
        master_row = QHBoxLayout()
        master_row.setSpacing(10)
        icon = IconWidget(FluentIcon.BRIGHTNESS)
        icon.setFixedSize(20, 20)
        self.master_slider = Slider(Qt.Horizontal)
        self.master_slider.setRange(0, 100)
        self.master_slider.setValue(50)
        self.master_slider.valueChanged.connect(self._on_master)
        self.master_label = StrongBodyLabel("--")
        self.master_label.setFixedWidth(34)
        self.master_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        master_row.addWidget(icon)
        master_row.addWidget(self.master_slider, 1)
        master_row.addWidget(self.master_label)
        self.vbox.addLayout(master_row)

        self.vbox.addWidget(_Separator())

        # контейнер строк мониторов
        self.monitors_box = QWidget()
        self.monitors_layout = QVBoxLayout(self.monitors_box)
        self.monitors_layout.setContentsMargins(0, 0, 0, 0)
        self.monitors_layout.setSpacing(0)
        self.vbox.addWidget(self.monitors_box)

        self.vbox.addWidget(_Separator())

        # профили
        prof_header = QHBoxLayout()
        prof_title = CaptionLabel("Профили")
        prof_title.setStyleSheet("CaptionLabel{color: gray;}")
        self.add_btn = TransparentToolButton(FluentIcon.ADD)
        self.add_btn.setToolTip("Сохранить текущие значения как профиль")
        self.add_btn.clicked.connect(self.add_profile_clicked)
        prof_header.addWidget(prof_title)
        prof_header.addStretch(1)
        prof_header.addWidget(self.add_btn)
        self.vbox.addLayout(prof_header)

        self.profiles_box = QWidget()
        self.profiles_box.setSizePolicy(QSizePolicy.Preferred,
                                        QSizePolicy.Minimum)
        self.profiles_layout = FlowLayout(self.profiles_box)
        self.profiles_layout.setContentsMargins(0, 0, 0, 0)
        self.vbox.addWidget(self.profiles_box)

    def _on_master(self, value: int) -> None:
        self.master_label.setText(str(value))
        self.master_changed.emit(value)

    # ---------- мониторы ----------
    def set_monitors(self, names: list[str]) -> None:
        while self.monitors_layout.count():
            item = self.monitors_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self.rows = []
        if not names:
            lbl = BodyLabel("Мониторы не найдены.\n"
                            "Проверьте, включён ли DDC/CI в меню монитора.")
            self.monitors_layout.addWidget(lbl)
            return
        for i, name in enumerate(names):
            row = MonitorRow(i, name)
            row.changed.connect(self.monitor_changed)
            self.monitors_layout.addWidget(row)
            self.rows.append(row)

    def set_master_silent(self, value: int) -> None:
        self.master_slider.blockSignals(True)
        self.master_slider.setValue(int(value))
        self.master_slider.blockSignals(False)
        self.master_label.setText(str(int(value)))

    def update_master_from_rows(self) -> None:
        active = [r.value() for r in self.rows if r.slider.isEnabled()]
        if active:
            self.set_master_silent(round(sum(active) / len(active)))

    # ---------- профили ----------
    def set_profiles(self, profiles: list[dict], active_name: str | None) -> None:
        self.profiles_layout.takeAllWidgets()
        for prof in profiles:
            btn = ProfileButton(prof["name"])
            btn.setCheckable(True)
            btn.setChecked(prof["name"] == active_name)
            slot = prof.get("slot")
            if slot:
                btn.setToolTip(f"Ctrl+Alt+{slot}")
            btn.clicked.connect(
                lambda _=False, n=prof["name"]: self.profile_clicked.emit(n))
            self.profiles_layout.addWidget(btn)
        if not profiles:
            hint = CaptionLabel("Нажмите «+», чтобы сохранить профиль")
            hint.setStyleSheet("CaptionLabel{color: gray;}")
            self.profiles_layout.addWidget(hint)
        self.profiles_box.adjustSize()
        self.adjustSize()

    # ---------- показ ----------
    def popup(self) -> None:
        self.adjustSize()
        geo = QGuiApplication.primaryScreen().availableGeometry()
        x = geo.right() - self.width() - 12
        y = geo.bottom() - self.height() - 12
        self.move(x, y + 16)
        self.setWindowOpacity(0.0)
        self.show()

        pos_anim = QPropertyAnimation(self, b"pos", self)
        pos_anim.setDuration(220)
        pos_anim.setStartValue(QPoint(x, y + 16))
        pos_anim.setEndValue(QPoint(x, y))
        pos_anim.setEasingCurve(QEasingCurve.OutCubic)
        op_anim = QPropertyAnimation(self, b"windowOpacity", self)
        op_anim.setDuration(180)
        op_anim.setStartValue(0.0)
        op_anim.setEndValue(1.0)
        group = QParallelAnimationGroup(self)
        group.addAnimation(pos_anim)
        group.addAnimation(op_anim)
        group.start()
        self._anim = group

    # ---------- отрисовка фона ----------
    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        if isDarkTheme():
            bg = QColor(40, 40, 40, 247)
            border = QColor(255, 255, 255, 20)
        else:
            bg = QColor(246, 246, 246, 250)
            border = QColor(0, 0, 0, 22)
        rect = self.rect().adjusted(0, 0, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(rect, RADIUS, RADIUS)
        p.fillPath(path, bg)
        p.setPen(border)
        p.drawPath(path)
