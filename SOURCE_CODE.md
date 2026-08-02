# Исходный код Yarkost Monitor

## Идентификация версии

- Программа: **Yarkost Monitor**
- Версия: **1.0.0**
- Идентификатор исходного кода: **git-тег `v1.0.0`** (создаётся в локальном
  репозитории проекта; commit SHA — см. `git rev-list -n 1 v1.0.0`)
- Репозиторий: https://github.com/Dignition/yarkost-monitor
- Исходный код именно этой версии:
  https://github.com/Dignition/yarkost-monitor/releases/tag/v1.0.0
  (страница релиза содержит автоматический архив Source code)

ВАЖНО: бинарный релиз (установщик) не должен распространяться до того,
как репозиторий и тег `v1.0.0` опубликованы по указанному адресу и
доступны без авторизации. Исходный код должен оставаться доступным не
меньше срока, требуемого применимыми лицензиями (для GPLv3 §6 — как
минимум пока предлагается соответствующий бинарный дистрибутив, а при
письменной оферте — не менее трёх лет).

## Состав репозитория

- Приложение: `main.py`, `flyout.py`, `settings_dialog.py`,
  `monitors.py`, `hotkeys.py`, `config.py`
- Ресурсы: `icon.ico`
- Упаковка: `make_installer.bat` (PyInstaller, onedir) и `setup.iss`
  (Inno Setup 6); сгенерированный spec: `YarkostMonitor.spec`
- Лицензионные файлы: `LICENSE`, `LICENSE_SUMMARY_RU.txt`,
  `THIRD_PARTY_NOTICES.md`, каталог `licenses/`
- Зависимости: `requirements.txt` (диапазоны), `requirements.lock.txt`
  (точные версии релиза 1.0.0)

## Сборка релиза (Windows 10/11 x64)

1. Установите 64-битный CPython (сборка 1.0.0 выполнялась на CPython
   3.14; модульные проверки — на CPython 3.10.12).
2. `python -m pip install -r requirements.lock.txt`
3. `python -m pip install pyinstaller==6.21.0`
4. Запустите `make_installer.bat` — он:
   - собирает `dist\YarkostMonitor\` (PyInstaller, onedir, без консоли);
   - записывает фактическое окружение сборки в
     `installer_output\build-environment.txt` (`pip freeze`);
   - компилирует `installer_output\YarkostMonitor-Setup-1.0.0.exe`
     (Inno Setup 6; при отсутствии ставится через winget).

Полная воспроизводимость до байта не гарантируется (PyInstaller и Inno
Setup не дают детерминированных сборок), но состав и версии компонентов
фиксируются lock-файлом и build-environment.txt.

## Чек-лист соответствия бинарника и исходников

1. Версия совпадает в: `config.py` (`APP_VERSION`), `setup.iss`
   (`MyAppVersion`), имени установщика и git-теге.
2. Создан и опубликован git-тег: `git tag v1.0.0 && git push origin main --tags`.
3. К GitHub-релизу приложен установщик; архив исходников создаётся
   GitHub автоматически.
4. В репозиторий не попадают секреты и локальные файлы; папки сборки
   исключены через `.gitignore`.
5. Доступность проверена из браузера без авторизации.
