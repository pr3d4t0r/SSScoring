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
EXIT_SPEED = 2*9.81
FLYSIGHT_HEADER = set([ 'time', 'lat', 'lon', 'hMSL', 'velN', 'velE', 'velD', 'hAcc', 'vAcc', 'sAcc', 'heading', 'cAcc', 'gpsFix', 'numSV', ])
FT_IN_M = 3.2808
IGNORE_LIST = [ '.ipynb_checkpoints', ]
LAST_TIME_TRANCHE = 25.0
MAX_ALTITUDE_FT = 15500
MAX_ALTITUDE_METERS = MAX_ALTITUDE_FT/3.28
MAX_SPEED_ACCURACY = 3.0
MIN_JUMP_FILE_SIZE = 1024*512
PERFORMANCE_WINDOW_LENGTH = 2256.0
VALIDATION_WINDOW_LENGTH = 1006.0

