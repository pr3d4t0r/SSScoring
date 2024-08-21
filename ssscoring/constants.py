# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

"""
Constants module and definitions.

**All measurements are expressed in meters unless noted otherwise.**
"""

import math


# +++ implementation +++

BREAKOFF_ALTITUDE = 1707.0
"""
Breakoff altitude or hard deck.
"""

DEG_IN_RADIANS = math.pi/180.0
"""
π/180º
"""

EXIT_SPEED = 2*9.81
"""
Guesstimate of the exit speed; 2*g
"""

FLYSIGHT_1_HEADER = set([ 'time', 'lat', 'lon', 'hMSL', 'velN', 'velE', 'velD', 'hAcc', 'vAcc', 'sAcc', 'heading', 'cAcc', 'gpsFix', 'numSV', ])
"""
FlySight v1 CSV file headers.
"""

FT_IN_M = 3.2808
"""
Number of feet in a meter.
"""

IGNORE_LIST = [ '.ipynb_checkpoints', ]
"""
Internal use - list of files to be ignored during bulk file processing in the
data lake (e.g. `./data`).
"""

LAST_TIME_TRANCHE = 25.0
"""
Times > 25 s are irrelevant because it means that the speed skydiver flew at
vSpeed < 400 km/h.
"""

MAX_ALTITUDE_FT = 15500
"""
Maximum suggested altitude but irrelevant in general.  Max altitude without
oxygen is 15,500 ft AGL at most DZs.  A jumnp from a higher altitude would
require oxygen and would be scored 3,000 ft higher than the hard deck.
"""

MAX_ALTITUDE_METERS = MAX_ALTITUDE_FT/3.28
"""
See
---
    ssscoring.constants.MAX_ALTITUDE_FT
"""

MAX_SPEED_ACCURACY = 3.0
"""
Speed accuracy for the FlySight device.
"""

MIN_JUMP_FILE_SIZE = 1024*512
"""
FlySight v1 files smaller than `MIN_JUMP_FILE_SIZE` are ignored because they
lack the minimum number of data points to contain a valid speed skydive.
**TODO:** Revise for FlySight v2.
"""

PERFORMANCE_WINDOW_LENGTH = 2256.0
"""
Performance window length as defined by ISSA/IPC/USPA.
"""

VALIDATION_WINDOW_LENGTH = 1006.0
"""
The validation window length as defined in the competition rules.
"""
