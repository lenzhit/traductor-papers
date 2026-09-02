# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import copy_metadata, collect_data_files, collect_submodules

block_cipher = None

# Recolectar metadatos y archivos de datos necesarios para Streamlit y dependencias
datas = [
    ('app.py', '.'),
    ('utils', 'utils'),
]

if os.path.exists('.streamlit'):
    datas.append(('.streamlit', '.streamlit'))

if os.path.exists('.env.example'):
    datas.append(('.env.example', '.'))

datas += copy_metadata('streamlit')
datas += collect_data_files('streamlit')
datas += collect_data_files('reportlab')
datas += collect_data_files('docx')

hiddenimports = [
    'streamlit',
    'streamlit.web.cli',
    'streamlit.runtime.scriptrunner.magic_expressions',
    'streamlit.runtime.caching',
    'streamlit.elements',
    'altair',
    'reportlab',
    'reportlab.lib',
    'reportlab.platypus',
    'docx',
    'docx.shared',
    'docx.enum.text',
    'pypdf',
    'dotenv',
    'google.genai',
    'google.genai.types',
    'google.generativeai',
    'utils',
    'utils.extractor',
    'utils.chunker',
    'utils.translator',
    'utils.exporter',
    'utils.i18n',
    'utils.theme',
]

hiddenimports += collect_submodules('streamlit')
hiddenimports += collect_submodules('reportlab')
hiddenimports += collect_submodules('docx')
hiddenimports += collect_submodules('pypdf')

a = Analysis(
    ['run_app.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TraductorPapers',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Mantener consola visible para ver logs de arranque
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None
)
