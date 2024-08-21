# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

"""
Speed Skydiving Scoring tools package for processing FlySight v1 and v2 CSV data
files.

This library relies on NumPy and pandas.  When running in a Lucyfer notebook,
it also requires the Bokeh plotting library.

The documentation for each module in this package is linked from the navigation
bar.  The **fs1** module contains functions that process v1 files.  The v2
implementation is in progress in a private Git branch.
"""

import importlib.metadata


__VERSION__ = importlib.metadata.version('ssscoring')
"""
@public
"""


