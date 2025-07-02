# -*- mode: python -*-
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT
from PyInstaller.utils.hooks import collect_data_files
import os

blocked_dlls = ['api-ms-win-crt-math-l1-1-0.dll']

a = Analysis(
    ['src/interface.py'],
    pathex=[os.getcwd()],  # CORREÇÃO AQUI - usa diretório atual
    binaries=[
        ('src/recursos/ffmpeg.exe', 'recursos'),
    ],
    datas=[
        *collect_data_files('customtkinter', include_py_files=True),
        *collect_data_files('yt_dlp'),
        *collect_data_files('requests'),
        ('src/recursos/icone.ico', 'recursos'),  # Garantir que o ícone seja incluído
    ],
    hiddenimports=[
        'yt_dlp.extractor',
        'yt_dlp.extractor.*',
        'requests.packages.urllib3',
        'PIL'  # Importante para Pillow
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
    block_dlls=blocked_dlls,  # Note: o parâmetro correto é block_dlls (singular)
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MediaFlow',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Desabilita UPX para reduzir detecções de vírus
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join('src', 'recursos', 'icone.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,  # Desabilita UPX aqui também
    name='MediaFlow'
)