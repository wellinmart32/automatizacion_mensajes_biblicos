[Setup]
AppName=Mensajes Biblicos AutoPro
AppVersion=1.0.0
AppPublisher=AutomaPro
AppPublisherURL=https://automapro.com
DefaultDirName={userdocs}\AutomaPro\MensajesBiblicos
DefaultGroupName=AutomaPro\MensajesBiblicos
OutputDir=installer_output
OutputBaseFilename=InstaladorMensajesBiblicos
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear icono en el Escritorio"; GroupDescription: "Iconos adicionales:"

[Files]
Source: "dist\MensajesBiblicos.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\GestorTareasMensajes.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\WizardMensajes.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "config_global.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "compartido\*"; DestDir: "{app}\compartido"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "publicadores\*"; DestDir: "{app}\publicadores"; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
Name: "{app}\mensajes"
Name: "{app}\perfiles"

[Icons]
Name: "{group}\Mensajes Biblicos"; Filename: "{app}\MensajesBiblicos.exe"
Name: "{group}\Gestor de Tareas"; Filename: "{app}\GestorTareasMensajes.exe"
Name: "{group}\Configuracion Inicial"; Filename: "{app}\WizardMensajes.exe"
Name: "{commondesktop}\Mensajes Biblicos"; Filename: "{app}\MensajesBiblicos.exe"; Tasks: desktopicon
Name: "{commondesktop}\Gestor Mensajes"; Filename: "{app}\GestorTareasMensajes.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\WizardMensajes.exe"; Description: "Ejecutar configuracion inicial"; Flags: nowait postinstall skipifsilent