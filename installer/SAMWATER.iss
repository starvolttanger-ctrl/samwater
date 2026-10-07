[Setup]
AppName=SAMWATER
AppVersion=1.0
DefaultDirName={pf}\SAMWATER
OutputBaseFilename=SAMWATER_Setup

[Files]
Source: "..\dist\SAMWATER.exe"; DestDir: "{app}"

[Icons]
Name: "{commondesktop}\SAMWATER"; Filename: "{app}\SAMWATER.exe"
