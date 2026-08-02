# Сторонние компоненты Yarkost Monitor

Yarkost Monitor 1.0.0 распространяется вместе со следующими сторонними
компонентами. Полные тексты лицензий находятся в каталоге `licenses/`,
устанавливаемом вместе с программой. Сведения получены из файлов лицензий
и метаданных конкретных версий пакетов (dist-info/METADATA, LICENSE) и из
фактического состава собранного дистрибутива (`dist/YarkostMonitor/_internal`).

| Компонент | Версия | Правообладатель | Лицензия | Текст лицензии | В дистрибутиве |
|---|---|---|---|---|---|
| PySide6 / Qt for Python (PySide6, PySide6_Essentials, PySide6_Addons, shiboken6) | 6.11.1 | The Qt Company Ltd. | LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only (используется на условиях LGPL-3.0/GPL-3.0) | `licenses/LGPL-3.0.txt`, `licenses/GPL-3.0.txt` | Да (Qt6*.dll, plugins, shiboken6) |
| PySide6-Fluent-Widgets (qfluentwidgets) | 1.11.3 | zhiyiYo | Файл LICENSE пакета: GNU GPL v3 (см. примечание 1) | `licenses/PySide6-Fluent-Widgets-1.11.3-LICENSE.txt` | Да (включая dist-info с LICENSE) |
| PySideSix-Frameless-Window | 0.8.1 | zhiyiYo | LGPL v3 (по LICENSE пакета) | `licenses/PySideSix-Frameless-Window-0.8.1-LICENSE.txt` | Да |
| darkdetect | 0.8.0 | Alberto Sottile | BSD-3-Clause | `licenses/darkdetect-0.8.0-LICENSE.txt` | Да |
| monitorcontrol | 4.2.0 | Alex Martens | MIT | `licenses/monitorcontrol-4.2.0-LICENSE.txt` | Да |
| Pillow (PIL) | 12.2.0 (см. примечание 2) | Jeffrey A. Clark и участники; Secret Labs AB; Fredrik Lundh | MIT-CMU (лицензия Pillow) | `licenses/Pillow-LICENSE.txt` | Да |
| pywin32 (win32, Pythonwin, pywin32_system32) | 312 (см. примечание 2) | Mark Hammond и авторы включённых компонентов | Лицензии в составе пакета (основная — разрешительная, см. файл; Scintilla — отдельное уведомление) | `licenses/pywin32-LICENSE.txt` | Да |
| WMI (пакет Python «WMI») | 1.5.1 | Tim Golden | MIT (объявлена в метаданных; отдельный файл лицензии в пакете не поставляется) | `licenses/WMI-1.5.1-NOTICE.txt` | Да |
| CPython (python3.dll, python314.dll, стандартная библиотека) | 3.14 (сборочная машина) | Python Software Foundation | PSF License Version 2 | `licenses/Python-PSF-LICENSE.txt` (см. примечание 3) | Да |
| OpenSSL (libcrypto-3.dll, libssl-3.dll) | серия 3.x (поставляется с CPython) | The OpenSSL Project | Apache-2.0 | `licenses/OpenSSL-3-Apache-2.0.txt` | Да |
| libffi (libffi-8.dll) | 8 (ABI) | Anthony Green и участники | MIT-подобная (см. файл) | `licenses/libffi-LICENSE.txt` | Да |
| Microsoft Visual C++ Runtime и UCRT (VCRUNTIME140.dll, VCRUNTIME140_1.dll, ucrtbase.dll, api-ms-win-*.dll) | из состава CPython/VS Redistributable | Microsoft Corporation | Проприетарные распространяемые компоненты; редистрибуция в составе приложений разрешена условиями Microsoft (текст лицензии не поставляется) | — | Да |
| PyInstaller bootloader | 6.21.0 (контрольное окружение; см. примечание 2) | PyInstaller Development Team, Giovanni Bajo и др. | GPL-2.0-or-later с исключением загрузчика (позволяет распространять собранные программы под любой лицензией) | `licenses/PyInstaller-COPYING.txt` | Да (загрузчик внутри YarkostMonitor.exe) |
| Inno Setup (движок установщика) | 6.x | Jordan Russell, Martijn Laan | Inno Setup License | `licenses/InnoSetup-LICENSE.txt` | Да (внутри YarkostMonitor-Setup-*.exe) |

Собственный код Yarkost Monitor и иконка `icon.ico`:
Copyright (C) 2026 Dignition, лицензия GPL-3.0-only (файл `LICENSE`).

## Примечание 1. Лицензирование PySide6-Fluent-Widgets

Файл `LICENSE` пакета версии 1.11.3 содержит полный текст GNU GPL v3 без
дополнительных условий; поле `License` метаданных — «GPLv3». Одновременно
описание пакета (METADATA/README upstream) содержит следующее заявление:

> "PySide6-Fluent-Widgets adopts dual licenses. Non-commercial usage is
> licensed under GPLv3. For commercial purposes, please purchase
> commercial license to support the development of this project."
> (https://qfluentwidgets.com/price)

Между файлом LICENSE (GPLv3 без ограничения сферы использования) и
заявлением о «только некоммерческом» применении GPLv3-версии есть
расхождение. Настоящий документ фиксирует оба факта дословно и не делает
самостоятельного юридического вывода. Yarkost Monitor распространяется
бесплатно с открытым исходным кодом под GPL-3.0-only; при любом
коммерческом сценарии распространения Yarkost Monitor этот вопрос
подлежит разрешению до релиза (см. SOURCE_CODE.md и раздел
«Лицензия» в README.md).

## Примечание 2. Версии, зависящие от сборочной машины

Точные версии Pillow, pywin32 и PyInstaller на конкретной сборочной
машине фиксируются автоматически при каждой сборке в файле
`installer_output/build-environment.txt` (вывод `pip freeze`).
Указанные в таблице версии соответствуют контрольному окружению
подготовки релиза 1.0.0 и файлу `requirements.lock.txt`.

## Примечание 3. Qt и CPython: встроенные сторонние компоненты

Библиотеки Qt (Qt6*.dll) сами включают сторонние компоненты (например,
FreeType, HarfBuzz, libpng, PCRE2, zlib и другие). Официальный перечень
и тексты: https://doc.qt.io/qt-6/licenses-used-in-qt.html. Колёса PyPI
PySide6 6.11.1 не содержат отдельных файлов этих лицензий; данный
перечень включён по ссылке. Текст PSF-лицензии в `licenses/` взят из
дистрибутива CPython; применимая версия текста соответствует версии
CPython, использованной при сборке.
