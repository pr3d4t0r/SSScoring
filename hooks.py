# See: https://github.com/pr4d4t0r/SSSCoring/blob/master/LICENSE.txt


from PyInstaller.utils.hooks import copy_metadata as copyMetadata
from PyInstaller.utils.hooks import collect_submodules as collectSubmodules


datas = copyMetadata('streamlit')
hiddenimports = collectSubmodules('streamlit')

