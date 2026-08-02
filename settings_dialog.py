# SPDX-FileCopyrightText: 2026 Dignition
# SPDX-License-Identifier: GPL-3.0-only
"""Окно настроек: общие параметры и управление профилями."""
import copy
import os

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QWidget,
                               QScrollArea, QFrame)

from qfluentwidgets import (SwitchButton, ComboBox, LineEdit, PushButton,
                            PrimaryPushButton, ToolButton, FluentIcon,
                            StrongBodyLabel, BodyLabel, CaptionLabel,
                            isDarkTheme)

import config

SLOT_NONE = "—"


class _ProfileRow(QWidget):
    """Строка профиля: имя, слот хоткея, удалить."""

    def __init__(self, profile: dict, parent=None):
        super().__init__(parent)
        self.deleted = False
        h = QHBoxLayout(self)
        h.setContentsMargins(0, 2, 0, 2)
        h.setSpacing(8)

        self.name_edit = LineEdit()
        self.name_edit.setText(profile["name"])
        self.slot_combo = ComboBox()
        self.slot_combo.addItems([SLOT_NONE] + [str(i) for i in range(1, 10)])
        slot = profile.get("slot")
        self.slot_combo.setCurrentIndex(int(slot) if slot else 0)
        self.slot_combo.setFixedWidth(70)
        self.del_btn = ToolButton(FluentIcon.DELETE)
        self.del_btn.setToolTip("Удалить профиль")
        self.del_btn.clicked.connect(self._on_delete)

        h.addWidget(self.name_edit, 1)
        h.addWidget(self.slot_combo)
        h.addWidget(self.del_btn)
        self._values = profile.get("values", {})

    def _on_delete(self) -> None:
        self.deleted = True
        self.hide()

    def result(self) -> dict | None:
        if self.deleted:
            return None
        name = self.name_edit.text().strip() or "Профиль"
        idx = self.slot_combo.currentIndex()
        return {"name": name,
                "slot": idx if idx > 0 else None,
                "values": self._values}


class AboutDialog(QDialog):
    """«Правовая информация»: лицензия, исходный код, сторонние компоненты.

    Все тексты доступны локально (устанавливаются вместе с программой),
    интернет не требуется.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Правовая информация")
        self.setModal(True)
        self.setFixedWidth(420)
        if isDarkTheme():
            self.setStyleSheet("QDialog{background:#202020;}")

        v = QVBoxLayout(self)
        v.setContentsMargins(24, 20, 24, 20)
        v.setSpacing(8)

        v.addWidget(StrongBodyLabel(f"Yarkost Monitor {config.APP_VERSION}"))
        v.addWidget(BodyLabel("Copyright (C) 2026 Dignition"))
        v.addWidget(BodyLabel("Лицензия: GNU GPL v3 (SPDX: GPL-3.0-only)"))

        src = BodyLabel(
            f'Исходный код этой версии: '
            f'<a href="{config.SOURCE_URL}">{config.SOURCE_URL}</a>')
        src.setOpenExternalLinks(True)
        src.setWordWrap(True)
        src.setTextInteractionFlags(Qt.TextBrowserInteraction)
        v.addWidget(src)

        warranty = CaptionLabel(
            "Программа предоставляется «как есть», без каких-либо гарантий. "
            "В пределах, допускаемых применимым законодательством, "
            "правообладатель не несёт ответственности за ущерб от "
            "использования программы. Подробности — в тексте лицензии.")
        warranty.setWordWrap(True)
        warranty.setStyleSheet("CaptionLabel{color: gray;}")
        v.addWidget(warranty)

        base = config.app_dir()
        self._paths = {
            "Текст лицензии (GPLv3)": os.path.join(base, "LICENSE"),
            "Сторонние компоненты": os.path.join(base,
                                                 "THIRD_PARTY_NOTICES.md"),
            "Все тексты лицензий": os.path.join(base, "licenses"),
        }
        for text, path in self._paths.items():
            btn = PushButton(text)
            if os.path.exists(path):
                btn.clicked.connect(
                    lambda _=False, p=path:
                    QDesktopServices.openUrl(QUrl.fromLocalFile(p)))
            else:
                btn.setEnabled(False)
                btn.setToolTip(f"Файл не найден: {path}")
            v.addWidget(btn)

        close_row = QHBoxLayout()
        close_row.addStretch(1)
        close_btn = PrimaryPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        close_row.addWidget(close_btn)
        v.addLayout(close_row)


class SettingsDialog(QDialog):
    """Модальное окно настроек. После accept() результат в self.result_cfg."""

    def __init__(self, cfg: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Яркость — настройки")
        self.setModal(True)
        self.resize(440, 520)
        self.result_cfg: dict | None = None
        self._cfg = copy.deepcopy(cfg)
        if isDarkTheme():
            self.setStyleSheet("QDialog{background:#202020;}")
        self._build()

    def _build(self) -> None:
        v = QVBoxLayout(self)
        v.setContentsMargins(24, 20, 24, 20)
        v.setSpacing(12)

        v.addWidget(StrongBodyLabel("Общие"))

        def switch_row(text: str, checked: bool) -> SwitchButton:
            h = QHBoxLayout()
            h.addWidget(BodyLabel(text))
            h.addStretch(1)
            sw = SwitchButton()
            sw.setChecked(checked)
            h.addWidget(sw)
            v.addLayout(h)
            return sw

        self.autostart_sw = switch_row("Автозапуск с Windows",
                                       self._cfg.get("autostart", True))
        self.smooth_sw = switch_row("Плавное изменение яркости",
                                    self._cfg.get("smooth", True))

        h = QHBoxLayout()
        h.addWidget(BodyLabel("Скорость анимации"))
        h.addStretch(1)
        self.speed_combo = ComboBox()
        self.speed_combo.addItems(["Медленно", "Средне", "Быстро"])
        speed = float(self._cfg.get("speed", 1.0))
        self.speed_combo.setCurrentIndex(0 if speed < 0.75 else
                                         (1 if speed < 1.5 else 2))
        self.speed_combo.setFixedWidth(130)
        h.addWidget(self.speed_combo)
        v.addLayout(h)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: rgba(128,128,128,60); border:none;")
        v.addWidget(sep)

        v.addWidget(StrongBodyLabel("Профили"))
        hint = CaptionLabel("Слот — цифра в хоткее: Ctrl+Alt+<слот> "
                            "мгновенно применяет профиль.")
        hint.setStyleSheet("CaptionLabel{color: gray;}")
        hint.setWordWrap(True)
        v.addWidget(hint)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea{background:transparent;}")
        inner = QWidget()
        inner.setStyleSheet("background:transparent;")
        self.profiles_layout = QVBoxLayout(inner)
        self.profiles_layout.setContentsMargins(0, 0, 0, 0)
        self.profiles_layout.setSpacing(4)
        self.profile_rows: list[_ProfileRow] = []
        for prof in self._cfg.get("profiles", []):
            row = _ProfileRow(prof)
            self.profiles_layout.addWidget(row)
            self.profile_rows.append(row)
        if not self.profile_rows:
            empty = CaptionLabel("Профилей пока нет — создайте их кнопкой «+» "
                                 "в окне яркости.")
            empty.setStyleSheet("CaptionLabel{color: gray;}")
            empty.setWordWrap(True)
            self.profiles_layout.addWidget(empty)
        self.profiles_layout.addStretch(1)
        scroll.setWidget(inner)
        v.addWidget(scroll, 1)

        buttons = QHBoxLayout()
        legal = PushButton("Правовая информация")
        legal.clicked.connect(lambda: AboutDialog(self).exec())
        buttons.addWidget(legal)
        buttons.addStretch(1)
        cancel = PushButton("Отмена")
        cancel.clicked.connect(self.reject)
        ok = PrimaryPushButton("Сохранить")
        ok.clicked.connect(self._on_save)
        buttons.addWidget(cancel)
        buttons.addWidget(ok)
        v.addLayout(buttons)

    def _on_save(self) -> None:
        cfg = self._cfg
        cfg["autostart"] = self.autostart_sw.isChecked()
        cfg["smooth"] = self.smooth_sw.isChecked()
        cfg["speed"] = [0.5, 1.0, 2.0][self.speed_combo.currentIndex()]

        profiles = []
        used_slots: set[int] = set()
        for row in self.profile_rows:
            prof = row.result()
            if prof is None:
                continue
            slot = prof["slot"]
            if slot in used_slots:  # дубликат слота — снимаем
                prof["slot"] = None
            elif slot:
                used_slots.add(slot)
            profiles.append(prof)
        cfg["profiles"] = profiles

        self.result_cfg = cfg
        self.accept()


class NewProfileDialog(QDialog):
    """Диалог создания профиля: имя + слот хоткея."""

    def __init__(self, taken_slots: set[int], default_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Новый профиль")
        self.setModal(True)
        self.setFixedWidth(340)
        self.result_data: dict | None = None
        if isDarkTheme():
            self.setStyleSheet("QDialog{background:#202020;}")

        v = QVBoxLayout(self)
        v.setContentsMargins(24, 20, 24, 20)
        v.setSpacing(10)

        v.addWidget(BodyLabel("Название профиля"))
        self.name_edit = LineEdit()
        self.name_edit.setText(default_name)
        self.name_edit.selectAll()
        v.addWidget(self.name_edit)

        v.addWidget(BodyLabel("Хоткей (Ctrl+Alt+…)"))
        self.slot_combo = ComboBox()
        items = [SLOT_NONE]
        free = [str(i) for i in range(1, 10) if i not in taken_slots]
        items += free
        self.slot_combo.addItems(items)
        if free:
            self.slot_combo.setCurrentIndex(1)  # первый свободный слот
        v.addWidget(self.slot_combo)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        cancel = PushButton("Отмена")
        cancel.clicked.connect(self.reject)
        ok = PrimaryPushButton("Создать")
        ok.clicked.connect(self._on_ok)
        buttons.addWidget(cancel)
        buttons.addWidget(ok)
        v.addLayout(buttons)
        self.name_edit.returnPressed.connect(self._on_ok)

    def _on_ok(self) -> None:
        name = self.name_edit.text().strip() or "Профиль"
        text = self.slot_combo.currentText()
        slot = int(text) if text != SLOT_NONE else None
        self.result_data = {"name": name, "slot": slot}
        self.accept()
