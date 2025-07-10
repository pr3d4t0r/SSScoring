# See: https://github.com/pr4d4t0r/SSSCoring/blob/master/LICENSE.txt


from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_submodules as collectSubmodules
from PyInstaller.utils.hooks import copy_metadata as copyMetadata

import site

plotlyPath = Path(site.getusersitepackages()) / 'plotly' / 'validators' / '_validators.json'

datas = copyMetadata('streamlit')
datas += [(plotlyPath.as_posix(), 'plotly/validators/'), ]
streamlitModules = collectSubmodules('streamlit')
plotlyModules = collectSubmodules('plotly.validators')
hiddenimports = streamlitModules + plotlyModules

