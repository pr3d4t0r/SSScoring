# -*- mode: python ; coding: utf-8 -*-
# See: https://github.com/pr4d4t0r/SSSCoring/blob/master/LICENSE.txt


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
datas += [ ( 'SSScore_app.py', '.') ]

# Collect hidden imports
streamlitModules = collectSubmodules('streamlit')
plotlyModules = collectSubmodules('plotly.validators')
hiddenimports = streamlitModules + plotlyModules

# Analysis
a = Analysis(
    # ['SSScore_app.py', 'ssscrunner.py'],
    [ 'launch_gui.py', ],
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
# Python bytecode archive
pyz = PYZ(a.pure)

# macOS App bundle settings
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
    console=False,  # GUI / windowed mode (will produce a .app on macOS)
)

# Collect and create the final app bundle
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SSScore_app',
)
