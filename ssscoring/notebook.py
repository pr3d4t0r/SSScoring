# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt
"""
## Utility reusable code for notebooks.
"""


from collections import namedtuple

from ssscoring import dropNonSkydiveDataFrom
from ssscoring import getSpeedSkydiveFrom
from ssscoring import isValidJump
from ssscoring import jumpAnalysisTable

import pandas as pd


# *** type definitions ***

JumpResults = namedtuple("JumpResults", "score maxSpeed scores data window table color result")


# *** functions ***

def processJump(data: pd.DataFrame):
    """
    Take a dataframe in SSScoring format and process it for display.  It
    serializes all the steps that would be taken from the ssscoring module, but
    includes some text/HTML data in the output.

    Arguments
    ---------
        data: pd.DataFrame
    A dataframe in SSScoring format

    Returns
    -------
    A `JumpResults` named tuple with these items:

    - `score` speed score
    - `maxSpeed` maximum speed during the jump
    - `scores` a Series of every 3-second window scores from exit to breakoff
    - `data` an updated SSScoring dataframe `plotTime`, where 0 = exit, used
      for plotting
    - `window` a named tuple with the exit, breakoff, and validation window
      altitudes
    - `table` a dataframe featuring the speeds and altitudes at 5-sec intervals
    - `color` a string that defines the color for the jump result; possible
      values are _green_ for valid jump, _red_ for invalid jump, per ISC rules
    - `result` a string with the legend of _valid_ or _invalid_ jump
    """
    data = data.copy()
    data = dropNonSkydiveDataFrom(data)
    window, data = getSpeedSkydiveFrom(data)
    validJump = isValidJump(data, window)
    score = 0.0

    if validJump:
        maxSpeed, table = jumpAnalysisTable(data)
        color = '#0f0'
        result = '🟢 valid'
        baseTime = data.iloc[0].timeUnix
        data['plotTime'] = data.timeUnix-baseTime

        scores = dict()
        for spot in data.plotTime:
            r0 = data[data.plotTime == spot]
            r1 = data[data.plotTime == spot+3.0]

            if not r1.empty:
                scores[0.5*(float(r0.vKMh.iloc[0])+float(r1.vKMh.iloc[0]))] = spot
        score = max(scores)

    else:
        color = '#f00'
        result = '🔴 invalid'

    return JumpResults(score, maxSpeed, scores, data, window, table, color, result)

