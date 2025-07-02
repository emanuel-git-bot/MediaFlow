#!/usr/bin/env python3
"""
Script personalizado para build do MediaFlow Desktop
- Gera o app na pasta /CodigoDaInterface
- Aplica otimizações para reduzir detecções de vírus
- Inclui informações de versão e metadados
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime

def clean_build_dirs():
    """Remove diretórios de build anteriores"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Removendo diretório: {dir_name}")
            shutil.rmtree(dir_name)

def create_version_info():
    """Cria arquivo de informações de versão"""
    version_info = f"""
# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x40004,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'MediaFlow'),
        StringStruct(u'FileDescription', u'MediaFlow Desktop - Baixador de Mídia'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'MediaFlow'),
        StringStruct(u'LegalCopyright', u'© 2025 MediaFlow. Todos os direitos reservados.'),
        StringStruct(u'OriginalFilename', u'MediaFlow.exe'),
        StringStruct(u'ProductName', u'MediaFlow Desktop'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info)
    
    return 'version_info.txt'

def build_app():
    """Executa o build do aplicativo"""
    print("🚀 Iniciando build do MediaFlow Desktop...")
    
    # Limpa builds anteriores
    clean_build_dirs()
    
    # Cria informações de versão
    version_file = create_version_info()
    
    # Comando PyInstaller com otimizações
    cmd = [
        'pyinstaller',
        '--clean',
        '--noconfirm',
        '--onedir',
        '--windowed',
        '--name=MediaFlow',
        '--icon=src/recursos/icone.ico',
        '--version-file=' + version_file,
        '--add-data=src/recursos/ffmpeg.exe;recursos',
        '--add-data=src/recursos/icone.ico;recursos',
        '--hidden-import=yt_dlp.extractor',
        '--hidden-import=yt_dlp.extractor.*',
        '--hidden-import=requests.packages.urllib3',
        '--hidden-import=PIL',
        '--exclude-module=matplotlib',
        '--exclude-module=numpy',
        '--exclude-module=scipy',
        '--exclude-module=pandas',
        'src/interface.py'
    ]
    
    print("📦 Executando PyInstaller...")
    print(f"Comando: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build concluído com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no build: {e}")
        print(f"Saída de erro: {e.stderr}")
        return False

def move_to_destination():
    """Move o app gerado para a pasta de destino"""
    source_dir = os.path.join('dist', 'MediaFlow')
    dest_dir = 'MediaFlow'
    
    if os.path.exists(dest_dir):
        print(f"Removendo diretório existente: {dest_dir}")
        shutil.rmtree(dest_dir)
    
    if os.path.exists(source_dir):
        print(f"Movendo de {source_dir} para {dest_dir}")
        shutil.move(source_dir, dest_dir)
        print("✅ App movido para pasta de destino!")
        return True
    else:
        print(f"❌ Diretório fonte não encontrado: {source_dir}")
        return False

def create_manifest():
    """Cria arquivo de manifesto para reduzir detecções de vírus"""
    manifest_content = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="1.0.0.0"
    processorArchitecture="X86"
    name="MediaFlow.Desktop"
    type="win32"
  />
  <description>MediaFlow Desktop - Baixador de Mídia</description>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <compatibility xmlns="urn:schemas-microsoft-com:compatibility.v1">
    <application>
      <supportedOS Id="{e2011457-1546-43c5-a5fe-008deee3d3f0}"/>
      <supportedOS Id="{35138b9a-5d96-4fbd-8e2d-a2440225f93a}"/>
      <supportedOS Id="{4a2f28e3-53b9-4441-ba9c-d69d4a4a6e38}"/>
      <supportedOS Id="{1f676c76-80e1-4239-95bb-83d0f6d0da78}"/>
      <supportedOS Id="{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a}"/>
    </application>
  </compatibility>
</assembly>'''
    
    manifest_path = 'MediaFlow.manifest'
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write(manifest_content)
    
    return manifest_path

def cleanup():
    """Remove arquivos temporários"""
    files_to_remove = ['version_info.txt', 'MediaFlow.manifest', 'MediaFlow.spec']
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"Removido arquivo temporário: {file_name}")

def main():
    """Função principal"""
    print("=" * 50)
    print("🔧 MEDIAFLOW DESKTOP - SCRIPT DE BUILD")
    print("=" * 50)
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Verifica se está no diretório correto
    if not os.path.exists('src/interface.py'):
        print("❌ Erro: Execute este script na pasta CodigoDaInterface")
        return
    
    # Executa o build
    if build_app():
        # Move para destino
        if move_to_destination():
            # Cria manifesto
            create_manifest()
            
            print()
            print("🎉 BUILD CONCLUÍDO COM SUCESSO!")
            print("📁 App gerado em: ./MediaFlow/")
            print("🚀 Execute: ./MediaFlow/MediaFlow.exe")
            print()
            print("💡 Dicas para reduzir detecções de vírus:")
            print("   - Adicione a pasta MediaFlow ao antivírus como exceção")
            print("   - Use o app em modo administrador se necessário")
            print("   - O app é 100% seguro e não contém malware")
        else:
            print("❌ Erro ao mover app para destino")
    else:
        print("❌ Erro no processo de build")
    
    # Limpeza
    cleanup()
    
    print("=" * 50)

if __name__ == "__main__":
    main() 