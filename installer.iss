; See: https://github.com/pr4d4t0r/SSSCoring/blob/master/LICENSE.txt
;
; installer.iss — SSScore Windows onedir installer
; Build: make -f Makefile.win installer

#ifndef AppVersion
  #define AppVersion "3.0.0"        ; fallback; Makefile passes the real one via //DAppVersion=
#endif

[Setup]
AppId={{3981C7AD-B9C3-4B7C-A24C-A6AA2DF2365B}}
AppName=SSScore
AppPublisher=Eugene Ciurana
AppVersion={#AppVersion}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible    ; lands in Program Files, not (x86)
Compression=lzma2/max
DefaultDirName={autopf}\SSScore
DisableProgramGroupPage=yes
MinVersion=10.0.19044
OutputBaseFilename=SSScore-{#AppVersion}-Setup
OutputDir=dist
PrivilegesRequired=admin
SetupIconFile=resources\SSScore.ico
SolidCompression=yes
UninstallDisplayIcon={app}\SSScore.exe
WizardStyle=modern

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Files]
Source: "dist\SSScore\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{autoprograms}\SSScore"; Filename: "{app}\SSScore.exe"
Name: "{autodesktop}\SSScore"; Filename: "{app}\SSScore.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\SSScore.exe"; Description: "Launch SSScore"; Flags: nowait postinstall skipifsilent

