@echo off
rem === Build a distributable installer: installer_output\YarkostMonitor-Setup-1.0.0.exe ===
setlocal
cd /d "%~dp0"

where python >nul 2>nul && (set "PY=python") || (set "PY=py -3")

echo [1/4] Installing pinned build dependencies...
%PY% -m pip install --quiet -r requirements.lock.txt pyinstaller==6.21.0 || goto :err

echo [2/4] Building YarkostMonitor.exe ...
%PY% -m PyInstaller --noconfirm --clean --noconsole ^
  --name YarkostMonitor --icon icon.ico --add-data "icon.ico;." ^
  --collect-all qfluentwidgets main.py || goto :err

echo [3/4] Recording build environment (pip freeze)...
if not exist installer_output mkdir installer_output
%PY% -m pip freeze > installer_output\build-environment.txt

echo [4/4] Compiling installer with Inno Setup...
call :findiscc
if not defined ISCC (
    echo Inno Setup not found. Trying to install it via winget...
    winget install --id JRSoftware.InnoSetup -e --silent --accept-source-agreements --accept-package-agreements
    call :findiscc
)
if not defined ISCC (
    echo Could not find Inno Setup. Install it from https://jrsoftware.org/isdl.php and re-run this script.
    goto :err
)
"%ISCC%" /Q setup.iss || goto :err

echo.
echo Done! Distributable installer:
echo   %~dp0installer_output\YarkostMonitor-Setup-1.0.0.exe
echo Build environment recorded in installer_output\build-environment.txt
echo REMINDER: publish the source (git tag v1.0.0) BEFORE distributing the installer.
pause
exit /b 0

:findiscc
set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%LocalAppData%\Programs\Inno Setup 6\ISCC.exe" set "ISCC=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"
exit /b 0

:err
echo.
echo FAILED - see messages above.
pause
exit /b 1
