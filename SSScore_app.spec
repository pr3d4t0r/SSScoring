# See: https://github.com/pr4d4t0r/SSSCoring/blob/master/LICENSE.txt

# SSScore_app.spec  -- PyInstaller spec, onedir mode.
# Build:
#   pyinstaller --noconfirm --clean SSScore_app.spec
#
# Targets: macOS arm64 (.app), Windows x64 (.exe + _internal/).
# The same spec works on both; platform-specific bits are guarded below.
#
# Naming note: PyInstaller's spec API (Analysis, EXE, PYZ, COLLECT, BUNDLE
# and their keyword arguments — datas=, hiddenimports=, info_plist=, etc.)
# is framework-imposed and cannot be renamed. Local variables follow the
# project's camelCase / ALL_CAPS_WITH_UNDERSCORES convention.

# -*- mode: python ; coding: utf-8 -*-

import platform
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_submodules, copy_metadata

IS_MAC = sys.platform == 'darwin'
IS_WIN = sys.platform == 'win32'

MAC_TARGET_ARCH = platform.machine() if IS_MAC else None

APP_NAME = 'SSScore'
APP_VERSION = '3.0.0'
BUNDLE_ID = 'eu.ciurana.ssscoring'
BUNDLE_DIR_NAME = 'SSScore'
ENTRY_SCRIPT = 'launch_gui.py'
STREAMLIT_SCRIPT = 'ssscrunner.py'

MAC_ICON = 'resources/SSScore.icns'
WIN_ICON = None  # TODO: drop a .ico into resources/ and point here.

ASSET_PACKAGES = ('streamlit', 'pydeck', 'plotly', 'bokeh', 'webview')

bundleData: list = []
bundleBinaries: list = []
hiddenImports: list = []

# -- Heavy-asset packages ----------------------------------------------------
# Each of these ships a JS/CSS frontend bundle that MUST be on disk at runtime
# or the rendered components silently 404 in the browser.
for assetPackage in ASSET_PACKAGES:
    pkgDatas, pkgBinaries, pkgHidden = collect_all(assetPackage)
    bundleData     += pkgDatas
    bundleBinaries += pkgBinaries
    hiddenImports  += pkgHidden

# Streamlit reads its own dist-info at runtime (version, entry points).
bundleData += copy_metadata('streamlit')

# -- Project package ---------------------------------------------------------
# collect_submodules picks up dynamically-imported modules (e.g. anything
# referenced via importlib, or only imported under a code branch the static
# analyzer can't see).
hiddenImports += collect_submodules('ssscoring')

# Bundle the entire ssscoring package as SOURCE FILES (not just the
# resources subdirectory). Streamlit's bootstrap exec()s SSScore_app.py
# in a context where PyInstaller's frozen importer doesn't always resolve
# user packages cleanly — having the .py files on disk lets Python's
# normal PathFinder locate them. The collect_submodules() call above
# also keeps a frozen copy in the PYZ as a fallback.
bundleData += [
    ('ssscoring', 'ssscoring'),
    (STREAMLIT_SCRIPT, '.'),  # bundled as data; Streamlit reads it as a script
]

# -- Hidden imports Streamlit/pydeck need but PyInstaller misses -------------
hiddenImports += [
    'streamlit.web.cli',
    'streamlit.runtime.scriptrunner.magic_funcs',
    'streamlit.runtime.caching.cache_resource_api',
    'streamlit.runtime.caching.cache_data_api',
    'pkg_resources.py2_warn',  # legacy shim some deps still touch
]

# -- Runtime deps imported from inside ssscoring's source files --------------
# Because ssscoring/ is bundled as data (see bundleData below), PyInstaller's
# analyzer never reads those .py files and never sees their imports. Anything
# ssscoring depends on at runtime — but that isn't already pulled in by the
# asset-package collect_all() above — must be declared here explicitly.
RUNTIME_DEPS = (
    'haversine',
    'geopy',
    'click',
    'psutil',
    'importlib_resources',
    'webview',
    'objc',
)
for runtimeDep in RUNTIME_DEPS:
    hiddenImports += collect_submodules(runtimeDep)

# -- Modules we deliberately exclude to shrink the bundle --------------------
moduleExcludes = [
    'tkinter', 'tcl', 'tk',
    'IPython', 'ipykernel', 'ipywidgets',
    'jupyter', 'jupyter_client', 'jupyter_core', 'notebook', 'nbconvert',
    'pytest', 'pytest_cov',
    'PyQt5', 'PyQt6', 'PySide2', 'PySide6',
    'matplotlib.tests', 'numpy.tests', 'pandas.tests',
]

# ----------------------------------------------------------------------------

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
    exclude_binaries=True,            # onedir, NOT onefile
    name=BUNDLE_DIR_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                         # UPX trips Defender + breaks codesigning
    console=True,                     # set True for first-run debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=MAC_TARGET_ARCH,
    codesign_identity=None,            # signing handled post-build
    entitlements_file=None,
    icon=(MAC_ICON if IS_MAC else WIN_ICON),
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

# macOS .app bundle wrapper. No-op on Windows.
if IS_MAC:
    macAppBundle = BUNDLE(
        collection,
        name=f'{BUNDLE_DIR_NAME}.app',
        icon=MAC_ICON,
        bundle_identifier=BUNDLE_ID,
        info_plist={
            'CFBundleShortVersionString': APP_VERSION,
            'CFBundleVersion': APP_VERSION,
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,
            'LSBackgroundOnly': False,
            'LSUIElement': False,
            'LSMinimumSystemVersion': '11.0',
            'CFBundleName': APP_NAME,
            'CFBundleDisplayName': APP_NAME,
        },
    )

