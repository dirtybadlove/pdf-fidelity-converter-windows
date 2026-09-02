#ifndef SourceDir
  #error SourceDir must point to the PyInstaller application folder.
#endif

#ifndef OutputDir
  #error OutputDir must point to the installer output folder.
#endif

#define MyAppName "PDF 原版保真转换器"
#define MyAppVersion "0.3.0"
#define MyAppExeName "PDF-Fidelity-Converter.exe"

[Setup]
AppId={{5F0830EA-7B64-4C1D-A956-0BFC9DFBD5AF}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=PDF Content Converter contributors
DefaultDirName={localappdata}\Programs\PDF-Fidelity-Converter
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir={#OutputDir}
OutputBaseFilename=PDF-Fidelity-Converter-Setup-{#MyAppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
LicenseFile=..\LICENSE
UninstallDisplayIcon={app}\{#MyAppExeName}
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加快捷方式:"; Flags: unchecked

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\THIRD-PARTY-NOTICES.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "启动 {#MyAppName}"; Flags: nowait postinstall skipifsilent
