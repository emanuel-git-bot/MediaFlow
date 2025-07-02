# Configurações de build para MediaFlow Desktop
# Otimizações para reduzir detecções de vírus

BUILD_CONFIG = {
    # Configurações básicas
    'app_name': 'MediaFlow',
    'app_version': '1.0.0',
    'company_name': 'MediaFlow',
    'file_description': 'MediaFlow Desktop - Baixador de Mídia',
    'legal_copyright': '© 2025 MediaFlow. Todos os direitos reservados.',
    
    # Configurações PyInstaller
    'pyinstaller_opts': {
        '--clean': True,
        '--noconfirm': True,
        '--onedir': True,
        '--windowed': True,
        '--name': 'MediaFlow',
        '--icon': 'src/recursos/icone.ico',
        '--version-file': 'version_info.txt',
        '--add-data': [
            'src/recursos/ffmpeg.exe;recursos',
            'src/recursos/icone.ico;recursos'
        ],
        '--hidden-import': [
            'yt_dlp.extractor',
            'yt_dlp.extractor.*',
            'requests.packages.urllib3',
            'PIL'
        ],
        '--exclude-module': [
            'matplotlib',
            'numpy', 
            'scipy',
            'pandas',
            'tkinter.test',
            'unittest',
            'test',
            'distutils',
            'setuptools'
        ],
        '--upx-exclude': [
            'vcruntime140.dll',
            'python*.dll'
        ]
    },
    
    # Configurações de segurança
    'security': {
        'disable_upx': True,  # Desabilita UPX para reduzir detecções
        'add_manifest': True,  # Adiciona manifesto Windows
        'add_version_info': True,  # Adiciona informações de versão
        'verify_integrity': True,  # Verifica integridade do app
        'delay_startup': 0.1  # Delay no início para evitar detecções
    }
}

# Função para gerar comando PyInstaller
def get_pyinstaller_command():
    cmd = ['pyinstaller']
    
    for opt, value in BUILD_CONFIG['pyinstaller_opts'].items():
        if isinstance(value, bool) and value:
            cmd.append(opt)
        elif isinstance(value, str):
            cmd.extend([opt, value])
        elif isinstance(value, list):
            for item in value:
                cmd.extend([opt, item])
    
    cmd.append('src/interface.py')
    return cmd

if __name__ == "__main__":
    print("Configurações de build carregadas!")
    print(f"Comando PyInstaller: {' '.join(get_pyinstaller_command())}") 