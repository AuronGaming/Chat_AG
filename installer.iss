#define MyAppName "Chat_AG"
#define MyAppVersion "1.0.3"
#define MyAppPublisher "AuronGaming"
#define MyAppExeName "Chat_AG.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=installer_output
OutputBaseFilename=Chat_AG_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64


[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Создать ярлык на рабочем столе"; GroupDescription: "Дополнительные ярлыки:"; Flags: unchecked

[Files]
Source: "dist\Chat_AG\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "chat_ag_icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "chat_ag_icon.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "config.json"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Chat_AG"; Filename: "{app}\Chat_AG.exe"; IconFilename: "{app}\chat_ag_icon.ico"
Name: "{autodesktop}\Chat_AG"; Filename: "{app}\Chat_AG.exe"; IconFilename: "{app}\chat_ag_icon.ico"; Tasks: desktopicon



[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Запустить Chat_AG"; Flags: nowait postinstall skipifsilent

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "Chat_AG"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue; Tasks: autostart