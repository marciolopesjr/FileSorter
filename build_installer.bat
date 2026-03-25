@echo off
chcp 65001 >nul
echo ============================================
echo    FileSorter - Build e Instalador
echo ============================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python não está instalado ou não está no PATH
    echo Instale Python 3.8+ e tente novamente
    pause
    exit /b 1
)

echo [1/4] Instalando dependências...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependências
    pause
    exit /b 1
)
echo [OK] Dependências instaladas

echo.
echo [2/4] Criando executável com PyInstaller...
python build.py
if errorlevel 1 (
    echo [ERRO] Falha ao criar executável
    pause
    exit /b 1
)

echo.
echo [3/4] Verificando Inno Setup...
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set IS_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set IS_PATH=C:\Program Files\Inno Setup 6\ISCC.exe
) else (
    echo [AVISO] Inno Setup não encontrado
    echo.
    echo Para criar o instalador, instale o Inno Setup em:
    echo https://jrsoftware.org/isdl.php
    echo.
    echo O executável já está pronto em: dist\FileSorter.exe
    goto :skip_installer
)

echo [OK] Inno Setup encontrado: %IS_PATH%

echo.
echo [4/4] Criando instalador...
cd installer
"%IS_PATH%" create_installer.iss
cd ..

if exist "installer\Output\FileSorter_Setup_*.exe" (
    echo.
    echo [OK] Instalador criado com sucesso!
    echo.
    for %%f in (installer\Output\FileSorter_Setup_*.exe) do set INSTALLER=%%f
    echo Local: %INSTALLER%
) else (
    echo [AVISO] Instalador não foi criado, mas o executável está pronto
)

:skip_installer
echo.
echo ============================================
echo    Build concluído!
echo ============================================
echo.
echo O executável está disponível em:
echo   dist\FileSorter.exe
echo.
if defined INSTALLER (
    echo O instalador está disponível em:
    echo   %INSTALLER%
    echo.
)
echo Para testar o executável sem instalar:
echo   1. Navegue até a pasta 'dist'
echo   2. Execute FileSorter.exe
echo.
pause
