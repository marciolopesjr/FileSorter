# Script de Build para FileSorter
# Este script cria um executável Windows usando PyInstaller

import subprocess
import sys
import os
import shutil
from pathlib import Path

def build():
    """Compila a aplicação FileSorter para executável Windows."""
    
    project_dir = Path(__file__).parent
    build_dir = project_dir / "build"
    dist_dir = project_dir / "dist"
    
    # Limpar builds anteriores
    print("Limpando builds anteriores...")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    # Criar diretório dist
    dist_dir.mkdir(exist_ok=True)
    
    # Verificar se existe ícone
    icon_path = project_dir / "FileSorter_logo.ico"
    icon_arg = ["--icon", str(icon_path)] if icon_path.exists() else []
    
    # Comando PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "FileSorter",
        "--windowed",  # Sem console
        "--onefile",   # Executável único
    ] + icon_arg + [
        "--hidden-import", "google.generativeai",
        "--hidden-import", "openai",
        "--hidden-import", "watchdog",
        "--hidden-import", "tkinterdnd2",
        "--hidden-import", "tkinterdnd2.tkinterdnd2",
        "--collect-all", "tkinterdnd2",
        "--add-data", f"config.json{os.pathsep}.",
        str(project_dir / "FileSorter.py")
    ]
    
    print(f"Executando PyInstaller...")
    print(f"Comando: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True, cwd=project_dir)
        print("\n✅ Build concluído com sucesso!")
        print(f"Executável criado em: {dist_dir / 'FileSorter.exe'}")
        
        # Copiar arquivos adicionais para dist
        additional_files = [
            "requirements.txt",
            "README.md",
            ".env.example",
            "FileSorter_logo.png"
        ]
        
        for file in additional_files:
            src = project_dir / file
            if src.exists():
                shutil.copy(src, dist_dir / file)
                print(f"Copiado: {file}")
        
        # Criar pasta para o instalador
        installer_source = dist_dir / "installer_source"
        installer_source.mkdir(exist_ok=True)
        
        # Copiar tudo para a pasta do instalador
        for item in dist_dir.iterdir():
            if item.name not in ["installer_source", "build"]:
                shutil.copy2(item, installer_source / item.name)
        
        print(f"\n📁 Arquivos para instalador preparados em: {installer_source}")
        print("\nPróximo passo: Execute o script create_installer.iss no Inno Setup Compiler")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erro durante o build: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🔨 FileSorter Build Script")
    print("=" * 50)
    build()
