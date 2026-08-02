; Inno Setup script for Yarkost Monitor
; Produces a single distributable installer:
;   installer_output\YarkostMonitor-Setup-<version>.exe

#define MyAppName "Yarkost Monitor"
#define MyAppVersion "1.0.0"
#define MyAppExeName "YarkostMonitor.exe"

[Setup]
AppId={{8F0D5C2A-7B14-4E5D-9A33-2C4B8E1F6A90}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=Dignition
AppPublisherURL=https://github.com/Dignition/yarkost-monitor
AppSupportURL=https://github.com/Dignition/yarkost-monitor
DefaultDirName={autopf}\YarkostMonitor
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
; GPL не оформляется как обязательная EULA: используется
; информационная страница, а не страница принятия соглашения
InfoBeforeFile=LICENSE_SUMMARY_RU.txt
OutputDir=installer_output
OutputBaseFilename=YarkostMonitor-Setup-{#MyAppVersion}
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "autostart"; Description: "Запускать при старте Windows"
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; Flags: unchecked

[Files]
Source: "dist\YarkostMonitor\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion
; правовые файлы — устанавливаются вместе с программой и удаляются деинсталлятором
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE_SUMMARY_RU.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "THIRD_PARTY_NOTICES.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "SOURCE_CODE.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "licenses\*"; DestDir: "{app}\licenses"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autoprograms}\{#MyAppName} — лицензии и исходный код"; Filename: "{app}\LICENSE_SUMMARY_RU.txt"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
; автозапуск (галочка в установщике); удаляется при деинсталляции
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; \
    ValueType: string; ValueName: "YarkostMonitor"; \
    ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue; Tasks: autostart

[Run]
Filename: "{app}\{#MyAppExeName}"; \
    Description: "{cm:LaunchProgram,Yarkost Monitor}"; \
    Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{cmd}"; Parameters: "/c taskkill /im {#MyAppExeName} /f"; \
    Flags: runhidden; RunOnceId: "KillApp"
