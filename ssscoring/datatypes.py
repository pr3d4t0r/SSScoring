# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt


"""
SSScoring custom type definitions for easier symbolic manipuation.
"""

from collections import namedtuple
from enum import Enum


# +++ implementation +++

class FlySightVersion(Enum):
    """
    Symbols for handling device version.
    """
    V1 = 1000
    INSIGHT = 1100
    V2 = 2000


class JumpStatus(Enum):
    OK = 0
    ALTITUDE_EXCEEDS_MINIMUM = 100
    ALTITUDE_EXCEEDS_MAXIMUM = 110
    INVALID_SPEED_FILE = 120
    SPEED_ACCURACY_EXCEEDS_LIMIT = 200
    WARM_UP_FILE = 300
    UNSUPPORTED_PLD_FORMAT = 400


JumpResults = namedtuple(
    'JumpResults',
    'data maxSpeed score scores table window status backFall backFallOnset forwardReversalM lateralReversalM',
    defaults=(False, None, 0.0, 0.0),
)
"""
A named tuple containing the score, maximum speed, scores throught the
performance window, the results table for a jump, the output color for the
result, and the result information string.

Attributes
----------
- `data` - dataframe containing all the data points for plotting and
           calculations
- `maxSpeed` - maximum absolute speed registered during a skydive
- `score` - maximum mean speed during a 3-second window during the skydive
- `scores` - a dictionary with all the scored ruding the sliding 3-sec window
             for the speed run
- `table` - summary table of results of the speed run
- `window` - the scoring window data, an instance of `PerformanceWindow`
- `status` - An instance of `ssscoring.datatypes.JumpStatus`
- `backFall` - `True` if a back-fall was detected within the performance window
- `backFallOnset` - `plotTime` (seconds from exit) at back-fall onset, or `None`
- `forwardReversalM` - metres of reversed ground travel along the jump run axis
- `lateralReversalM` - metres of reversed ground travel on the lateral axis
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

