# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt


"""
SSScoring custom type definitions for easier symbolic manipuation.
"""

from collections import namedtuple


# +++ implementation +++

JumpResults = namedtuple('JumpResults', 'color data maxSpeed result score scores table window')
"""
A named tuple containing the score, maximum speed, scores throught the
performance window, the results table for a jump, the output color for the
result, and the result information string.

Attributes
----------
- `color` - a string representing a color, green if the result is valid, red
            otherwise
- `data` - dataframe containing all the data points for plotting and
           calculations
- `maxSpeed` - maximum absolute speed registered during a skydive
- `result` - dataframe of results
- `score` - maximum mean speed during a 3-second window during the skydive
- `scores` - a series with all the scored ruding the sliding 3-sec window for
             the whole speed skydive
- `table` - summary table of results of the speed run
- `window` - the scoring window data, an instance of `PerformanceWindow`
"""


PerformanceWindow = namedtuple('PerformanceWindow', 'start end validationStart')
"""
An object to handle the performance window (as defined in competition rules) as
a single object with all the properties necessary to interpret it and manipulate
it across different function or method calls.

Attributes
----------
- `start` - beginning or start of the performance window, or exit from the
            aircraft
- `end` - end of the performance window, or `start-PERFORMANCE_WINDOW_LENGTH`
- `validationStart` - end of the performance window - the `VALIDATION_WINDOW_END`

See
---
    ssscoring.constants.PERFORMANCE_WINDOW_LENGTH
    ssscoring.constants.VALIDATION_WINDOW_END
"""


