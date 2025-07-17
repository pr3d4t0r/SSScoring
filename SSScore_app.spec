# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files as collectDataFiles
from PyInstaller.utils.hooks import collect_submodules as collectSubmodules
from PyInstaller.utils.hooks import copy_metadata as copyMetadata

from pathlib import Path


import site
import sys


site_packages = site.getsitepackages()[0]

datas = [('/Users/ciurana/Python-3_13_4/lib/Python3.13/site-packages/plotly/validators', '_internal/plotly/validators')]
datas += copyMetadata('streamlit')
datas += collectDataFiles('plotly', includes=['validators/*.json'])
datas += [ ( '%s/streamlit/static' % site_packages, 'streamlit/static' ) ]

plotlyPath = Path(site.getusersitepackages()) / 'plotly' / 'validators' / '_validators.json'

streamlitModules = collectSubmodules('streamlit')
plotlyModules = collectSubmodules('plotly.validators')
hiddenimports = streamlitModules + plotlyModules

a = Analysis(
    ['SSScore_app.py', 'ssscrunner.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=['.', ],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[ ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SSScore_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SSScore_app',
)
