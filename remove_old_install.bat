@echo off
rem === Full cleanup of ANY previous Yarkost Monitor installation ===
rem (both the old script-based install and the Inno Setup install)

echo Removing Yarkost Monitor...

rem stop the app if running
taskkill /im YarkostMonitor.exe /f >nul 2>nul
timeout /t 1 /nobreak >nul

rem autostart entry
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v YarkostMonitor /f >nul 2>nul

rem "Installed apps" entries
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\YarkostMonitor" /f >nul 2>nul
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\{8F0D5C2A-7B14-4E5D-9A33-2C4B8E1F6A90}_is1" /f >nul 2>nul

rem program files
rmdir /s /q "%LocalAppData%\Programs\YarkostMonitor" >nul 2>nul

rem shortcuts (Start menu + Desktop)
del "%AppData%\Microsoft\Windows\Start Menu\Programs\Yarkost Monitor.lnk" >nul 2>nul
del "%UserProfile%\Desktop\Yarkost Monitor.lnk" >nul 2>nul

echo.
echo Done. All previous installations were removed.
echo Your settings and profiles in %%APPDATA%%\YarkostMonitor are kept.
pause
