# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt
"""
## Utility reusable code for notebooks.
"""


from collections import namedtuple

from ssscoring import dropNonSkydiveDataFrom
from ssscoring import getSpeedSkydiveFrom
from ssscoring import isValidJump
from ssscoring import jumpAnalysisTable

import bokeh.plotting as bp
import ipywidgets as widgets
import pandas as pd

# *** constants ***
DATA_LAKE_ROOT = './data' # Lucyfer default
SPEED_COLORS = colors = ('blue', 'limegreen', 'tomato', 'turquoise', 'deepskyblue', 'forestgreen', 'coral', 'darkcyan',)


# *** functions ***

