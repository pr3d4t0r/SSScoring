# See: https://github.com/pr4d4t0r/SSSCoring/blob/master/LICENSE.txt
# -*- mode: python ; coding: utf-8 -*-


from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files as collectDataFiles
from PyInstaller.utils.hooks import collect_submodules as collectSubmodules
from PyInstaller.utils.hooks import copy_metadata as copyMetadata

import importlib.util
import os
import site

import plotly.validators


sitePackages = site.getsitepackages()[0]


def getValidatorsPath():
    spec = importlib.util.find_spec('plotly.validators')
    if spec and spec.origin:
        return os.path.dirname(spec.origin)
    elif spec and spec.submodule_search_locations:
        return list(spec.submodule_search_locations)[0]
    else:
        raise ImportError("Can't resolve the plotly.validators path")


datas = [(getValidatorsPath(), '_internal/plotly/validators')]
datas += copyMetadata('streamlit')
datas += collectDataFiles('plotly', includes=['validators/*.json'])
datas += collectDataFiles('ssscoring', includes=['resources/*'])
datas += [ ( '%s/streamlit/static' % sitePackages, 'streamlit/static' ) ]
datas += [ ( 'ssscrunner.py', '.') ]

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
