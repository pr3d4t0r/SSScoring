; See: https://github.com/pr4d4t0r/SSSCoring/blob/master/LICENSE.txt
;
; installer.iss — SSScore Windows onedir installer
; Build: make -f Makefile.win installer

#ifndef AppVersion
  #define AppVersion "3.0.0"        ; fallback; Makefile passes the real one via //DAppVersion=
#endif

[Setup]
AppId={{GENERATE-A-GUID-IN-INNO-TOOLS-MENU}}    ; fixed GUID = clean upgrades/uninstall
AppName=SSScore
AppVersion={#AppVersion}
AppPublisher=Eugene Ciurana
DefaultDirName={autopf}\SSScore
DisableProgramGroupPage=yes
OutputDir=dist
OutputBaseFilename=SSScore-{#AppVersion}-Setup
Compression=lzma2/max
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible    ; lands in Program Files, not (x86)
PrivilegesRequired=admin
WizardStyle=modern
SetupIconFile=resources\SSScore.ico
UninstallDisplayIcon={app}\SSScore.exe

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Files]
Source: "dist\SSScore\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "redist\MicrosoftEdgeWebview2Setup.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
Name: "{autoprograms}\SSScore"; Filename: "{app}\SSScore.exe"
Name: "{autodesktop}\SSScore"; Filename: "{app}\SSScore.exe"; Tasks: desktopicon

[Run]
Filename: "{tmp}\MicrosoftEdgeWebview2Setup.exe"; Parameters: "/silent /install"; \
  StatusMsg: "Installing Edge WebView2 Runtime..."; Flags: waituntilterminated; Check: NeedsWebView2
Filename: "{app}\SSScore.exe"; Description: "Launch SSScore"; Flags: nowait postinstall skipifsilent

[Code]
function NeedsWebView2(): Boolean;
var v: string;
begin
  // Evergreen runtime stamps its version in 'pv'; absent/empty => install it
  Result := not RegQueryStringValue(HKLM,
    'SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}',
    'pv', v) or (v = '');
end;

