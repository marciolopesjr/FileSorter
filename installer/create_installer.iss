; Script Inno Setup para FileSorter
; Este script cria um instalador Windows profissional para o FileSorter

#define MyAppName "FileSorter"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "CurmudgeonApps"
#define MyAppExeName "FileSorter.exe"
#define MyAppURL "https://github.com/marciolopesjr/FileSorter"

[Setup]
; Configurações básicas
AppId={{A3B5C7D9-1234-5678-90AB-CDEF12345678}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
LicenseFile=..\LICENSE
OutputDir=.\Output
OutputBaseFilename=FileSorter_Setup_{#MyAppVersion}
SetupIconFile=..\FileSorter_logo.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
RestartIfNeededByRun=no

; Protocolo de arquivo (opcional)
; UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "portuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode
Name: "startupwithwindows"; Description: "Iniciar automaticamente com o Windows"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Arquivos principais
Source: ".\installer_source\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: ".\installer_source\requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: ".\installer_source\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: ".\installer_source\.env.example"; DestDir: "{app}"; DestName: ".env.example"; Flags: ignoreversion
Source: ".\installer_source\FileSorter_logo.png"; DestDir: "{app}"; Flags: ignoreversion
Source: ".\installer_source\config.json"; DestDir: "{app}"; Flags: ignoreversion

; Nota: Não inclua .env no instalador - cada usuário deve criar o seu

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
Filename: "notepad.exe"; Parameters: """{app}\.env.example"""; Description: "Abrir exemplo de configuração .env"; Flags: postinstall skipifsilent unchecked

[Code]
var
  ConfigPage: TInputQueryWizardPage;
  StartAutomaticallyCheckbox: TCheckBox;

procedure InitializeWizard;
begin
  // Criar página de configuração opcional
  ConfigPage := CreateInputQueryPage(wpWelcome,
    'Configuração da IA', 'Configure sua chave de API',
    'Insira sua chave de API para começar a usar o FileSorter.');
  
  ConfigPage.Add('Chave de API (OpenAI ou Gemini):', False);
  
  // Criar checkbox para iniciar automaticamente
  StartAutomaticallyCheckbox := WizardForm.CreateCheckBox(WizardForm);
  StartAutomaticallyCheckbox.Caption := 'Iniciar FileSorter automaticamente com o Windows';
  StartAutomaticallyCheckbox.Left := WizardForm.ClientWidth - 450;
  StartAutomaticallyCheckbox.Top := ConfigPage.Top + 100;
  StartAutomaticallyCheckbox.Width := 400;
  StartAutomaticallyCheckbox.Height := 30;
  StartAutomaticallyCheckbox.Parent := WizardForm;
end;

function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  
  // Verificar se o .NET Framework está instalado (necessário para algumas bibliotecas)
  if not RegKeyExists(HKLM, 'SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full') then
  begin
    if MsgBox('O .NET Framework 4.x não está instalado. Deseja continuar mesmo assim?', mbConfirmation, MB_YESNO) = IDNO then
      Result := False;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  EnvFilePath: String;
  APIKey: String;
begin
  if CurStep = ssPostInstall then
  begin
    // Criar arquivo .env se o usuário forneceu uma chave
    APIKey := ConfigPage.Values[0];
    if APIKey <> '' then
    begin
      EnvFilePath := ExpandConstant('{app}\.env');
      SaveStringToFile(EnvFilePath, '# Configuração do FileSorter' + #13#10 + 
        'OPENAI_API_KEY=' + '''' + APIKey + '''' + #13#10, False);
    end;
    
    // Configurar inicialização automática se selecionado
    if StartAutomaticallyCheckbox.Checked then
    begin
      // Criar entrada no registro para inicialização
      RegWriteStringValue(HKCU, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
        '{#MyAppName}', ExpandConstant('{app}\{#MyAppExeName}'));
    end;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  // Remover entrada de inicialização automática durante desinstalação
  if CurUninstallStep = usPostUninstall then
  begin
    RegDeleteValue(HKCU, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', '{#MyAppName}');
    
    // Remover tarefa agendada se existir
    Exec('schtasks', '/Delete /TN "FileSorter_AutoOrganization" /F', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;

[UninstallDelete]
; Limpar arquivos de configuração e log durante desinstalação
Type: filesandordirs; Name: "{localappdata}\FileSorter"
Type: filesandordirs; Name: "{userappdata}\FileSorter"
Type: filesandordirs; Name: "{userlogs}\FileSorter"

[UninstallRun]
; Parar o scheduler se estiver em execução
Filename: "taskkill"; Parameters: "/IM {#MyAppExeName} /F"; Flags: runhidden skipifsilent dontlogresult
