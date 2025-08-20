[Setup]
; Basic Information
AppId={{8D5B8F1C-9B2A-4E3F-8C7D-1A2B3C4D5E6F}
AppName=EchoScribe
AppVersion=1.0.0
AppVerName=EchoScribe 1.0.0
AppPublisher=EchoScribe Team
AppPublisherURL=https://github.com/yourusername/echoscribe
AppSupportURL=https://github.com/yourusername/echoscribe/issues
AppUpdatesURL=https://github.com/yourusername/echoscribe/releases
DefaultDirName={autopf}\EchoScribe
DefaultGroupName=EchoScribe
AllowNoIcons=yes
LicenseFile=LICENSE.txt
OutputDir=Output
OutputBaseFilename=EchoScribe-Setup
SetupIconFile=Assets\icons\echoscribe.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
PrivilegesRequired=admin

; 现代化外观设置
WizardImageFile=
WizardSmallImageFile=
DisableWelcomePage=no
ShowLanguageDialog=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
Source: "dist\EchoScribe-v1.0.0.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Assets\*"; DestDir: "{app}\Assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\Models\*"; DestDir: "{app}\Models"; Flags: ignoreversion recursesubdirs createallsubdirs  
Source: "dist\vendor\*"; DestDir: "{app}\vendor"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\EchoScribe"; Filename: "{app}\EchoScribe-v1.0.0.exe"
Name: "{group}\{cm:UninstallProgram,EchoScribe}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\EchoScribe"; Filename: "{app}\EchoScribe-v1.0.0.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\EchoScribe"; Filename: "{app}\EchoScribe-v1.0.0.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\EchoScribe-v1.0.0.exe"; Description: "{cm:LaunchProgram,EchoScribe}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
