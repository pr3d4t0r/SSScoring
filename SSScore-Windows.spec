# See: https://github.com/pr4d4t0r/SSSCoring/blob/master/LICENSE.txt

# SSScore-Windows.spec — dedicated Windows build (onedir .exe)
# Build:  make -f Makefile.win app   (or pyinstaller --noconfirm --clean SSScore-Windows.spec)

from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_submodules, copy_metadata

import platform
import sys


#+++ constants +++

IS_WIN = sys.platform == 'win32'

APP_NAME = 'SSScore'

from ssscoring import __VERSION__
APP_VERSION = __VERSION__

BUNDLE_DIR_NAME = 'SSScore'          # folder that will contain the .exe + _internal
ENTRY_SCRIPT = 'launch_gui.py'
STREAMLIT_SCRIPT = 'ssscrunner.py'

WIN_ICON = 'resources/SSScore.ico'

ASSET_PACKAGES = ('streamlit', 'pydeck', 'plotly', 'bokeh', 'webview')


# +++ globals +++

bundleData: list = []
bundleBinaries: list = []
hiddenImports: list = []

# Heavy asset packages (JS/CSS bundles that must be on disk)
for assetPackage in ASSET_PACKAGES:
    pkgDatas, pkgBinaries, pkgHidden = collect_all(assetPackage)
    bundleData     += pkgDatas
    bundleBinaries += pkgBinaries
    hiddenImports  += pkgHidden

bundleData += copy_metadata('streamlit')
hiddenImports += collect_submodules('ssscoring')

bundleData += [
    ('ssscoring', 'ssscoring'),
    (STREAMLIT_SCRIPT, '.'),
]

hiddenImports += [
    'streamlit.web.cli',
    'streamlit.runtime.scriptrunner.magic_funcs',
    'streamlit.runtime.caching.cache_resource_api',
    'streamlit.runtime.caching.cache_data_api',
    'pkg_resources.py2_warn',
]

RUNTIME_DEPS = (
    'haversine', 'geopy', 'click', 'psutil', 'importlib_resources',
    'webview', 'pythonnet',          # explicit for Windows
)
for runtimeDep in RUNTIME_DEPS:
    hiddenImports += collect_submodules(runtimeDep)

moduleExcludes = [
    'tkinter', 'tcl', 'tk',
    'IPython', 'ipykernel', 'ipywidgets',
    'jupyter', 'jupyter_client', 'jupyter_core', 'notebook', 'nbconvert',
    'pytest', 'pytest_cov',
    'PyQt5', 'PyQt6', 'PySide2', 'PySide6',
    'matplotlib.tests', 'numpy.tests', 'pandas.tests',
]

analysis = Analysis(
    [ENTRY_SCRIPT],
    pathex=[str(Path('.').resolve())],
    binaries=bundleBinaries,
    datas=bundleData,
    hiddenimports=hiddenImports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=moduleExcludes,
    noarchive=False,
)

pyzArchive = PYZ(analysis.pure, analysis.zipped_data)

executable = EXE(
    pyzArchive,
    analysis.scripts,
    [],
    exclude_binaries=False,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    icon=WIN_ICON,
)

collection = COLLECT(
    executable,
    analysis.binaries,
    analysis.zipfiles,
    analysis.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name=BUNDLE_DIR_NAME,
)
