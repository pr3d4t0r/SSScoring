# See: https://github.com/pr4d4t0r/SSSCoring/blob/master/LICENSE.txt

# SSScore-Intel_app.spec  -- PyInstaller spec, onedir mode, Intel (x86_64) macOS.
# Build:
#   activate86 && pyinstaller --noconfirm --clean SSScore-Intel_app.spec
#
# Produces: dist/SSScore-Intel.app  (Mach-O x86_64; runs natively on Intel
# Macs and under Rosetta 2 on Apple Silicon).
#
# Sibling spec for arm64: SSScore_app.spec — produces dist/SSScore.app.
# The two specs differ ONLY in BUNDLE_ID and BUNDLE_DIR_NAME so a diff
# audit is a 4-line reading. Keep them structurally aligned.

# -*- mode: python ; coding: utf-8 -*-

import platform
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_submodules, copy_metadata

IS_MAC = sys.platform == "darwin"
IS_WIN = sys.platform == "win32"

MAC_TARGET_ARCH = platform.machine() if IS_MAC else None

APP_NAME = "SSScore"
APP_VERSION = "3.0.0"
BUNDLE_ID = "net.cime.ssscoring.x86_64"
BUNDLE_DIR_NAME = "SSScore-Intel"
ENTRY_SCRIPT = "launch_gui.py"
STREAMLIT_SCRIPT = "ssscrunner.py"

MAC_ICON = "resources/Reventlou.icns"
WIN_ICON = None

ASSET_PACKAGES = ('streamlit', 'pydeck', 'plotly', 'bokeh', 'webview')

bundleData: list = []
bundleBinaries: list = []
hiddenImports: list = []

for assetPackage in ASSET_PACKAGES:
    pkgDatas, pkgBinaries, pkgHidden = collect_all(assetPackage)
    bundleData     += pkgDatas
    bundleBinaries += pkgBinaries
    hiddenImports  += pkgHidden

bundleData += copy_metadata("streamlit")
hiddenImports += collect_submodules("ssscoring")

bundleData += [
    ("ssscoring", "ssscoring"),
    (STREAMLIT_SCRIPT, "."),
]

hiddenImports += [
    "streamlit.web.cli",
    "streamlit.runtime.scriptrunner.magic_funcs",
    "streamlit.runtime.caching.cache_resource_api",
    "streamlit.runtime.caching.cache_data_api",
    "pkg_resources.py2_warn",
]

RUNTIME_DEPS = (
    "haversine",
    "geopy",
    "click",
    "psutil",
    "importlib_resources",
    'webview',
    'objc',
)
for runtimeDep in RUNTIME_DEPS:
    hiddenImports += collect_submodules(runtimeDep)

moduleExcludes = [
    "tkinter", "tcl", "tk",
    "IPython", "ipykernel", "ipywidgets",
    "jupyter", "jupyter_client", "jupyter_core", "notebook", "nbconvert",
    "pytest", "pytest_cov",
    "PyQt5", "PyQt6", "PySide2", "PySide6",
    "matplotlib.tests", "numpy.tests", "pandas.tests",
]

analysis = Analysis(
    [ENTRY_SCRIPT],
    pathex=[str(Path(".").resolve())],
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
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=MAC_TARGET_ARCH,
    codesign_identity=None,
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

if IS_MAC:
    macAppBundle = BUNDLE(
        collection,
        name=f"{BUNDLE_DIR_NAME}.app",
        icon=MAC_ICON,
        bundle_identifier=BUNDLE_ID,
        info_plist={
            "CFBundleName": APP_NAME,
            "CFBundleDisplayName": APP_NAME,
            "CFBundleShortVersionString": APP_VERSION,
            "CFBundleVersion": APP_VERSION,
            "NSHighResolutionCapable": True,
            "NSRequiresAquaSystemAppearance": False,
            "LSBackgroundOnly": False,
            "LSUIElement": False,
            "LSMinimumSystemVersion": "11.0",
        },
    )

