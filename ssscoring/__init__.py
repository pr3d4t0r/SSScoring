# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

"""
Speed Skydiving Scoring tools package for processing FlySight v1 and v2 CSV data
files.

This library relies on NumPy and pandas.  When running in a Lucyfer notebook or
in Streamlit.io, it also requires the Bokeh plotting library.


## Installation

```bash
pip install -U ssscoring
```

## Source code

You are welcome to **<a href='https://github.com/pr3d4t0r/SSScoring' target='_new'>fork SSScoring</a>**
on GitHub.  You will need Python 3.9 or later, pandas, and NumPy as minimum
requirements.

You may study or download the latest stable source files at:

<a href='https://github.com/pr3d4t0r/SSScoring/tree/master/ssscoring' target='_new'>https://github.com/pr3d4t0r/SSScoring/tree/master/ssscoring</a>
"""

import importlib.metadata


__VERSION__ = importlib.metadata.version('ssscoring')
"""
@public
"""


