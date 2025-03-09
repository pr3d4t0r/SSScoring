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

DEFAULT_SPEED_ACCURACY_SCALE = 5.0
"""
Default speed accuracy scale set to 5, to make it visible in plots.  This value
was chosen because the valid threshold is accuracy < 3.0, and this makes most
values visible without intefering with other curves in the same plot.

See
===
    ssscoring.notebook
    ssscoring.appcommon
"""

DEG_IN_RADIANS = math.pi/180.0
"""
π/180º
"""

EXIT_SPEED = 10.0
"""
Guesstimate of the exit speed; ~g
"""

FLYSIGHT_1_HEADER = set([ 'time', 'lat', 'lon', 'hMSL', 'velN', 'velE', 'velD', 'hAcc', 'vAcc', 'sAcc', 'heading', 'cAcc', 'gpsFix', 'numSV', ])
"""
FlySight v1 CSV file headers.
"""

FLYSIGHT_2_HEADER = ('GNSS', 'time', 'lat', 'lon', 'hMSL', 'velN', 'velE', 'velD', 'hAcc', 'vAcc', 'sAcc', 'numSV', )
"""
FlySight v1 CSV file headers.  Unlike other constants, this is a `tuple` instead
of a `set` because the code manipulates the headers/columns during file ingress.
"""


FLYSIGHT_FILE_ENCODING = 'utf-8'
"""
File encoding as it comes raw from the FlySight device.
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


KMH_AS_MS = 3.6
"""
km/h as m/s
"""


LAST_TIME_TRANCHE = 25.0
"""
Times > 25 s are irrelevant because it means that the speed skydiver flew at
vSpeed < 400 km/h.
"""


MAX_ALTITUDE_FT = 14000.0
"""
Maximum exit altitude AGL according to FAI Competition Rules Speed Skydiving
section 5.3.
"""

MAX_ALTITUDE_METERS = MAX_ALTITUDE_FT/3.28
"""
See
---
Maximum exit altitude AGL according to FAI Competition Rules Speed Skydiving
section 5.3.
"""


M_2_FT = 3.28084
"""
Meters to feet conversion factor.
"""


SPEED_ACCURACY_THRESHOLD = 3.0
"""
Speed accuracy for the FlySight device.
"""


MIN_JUMP_FILE_SIZE = 1024*512
MIN_JUMP_FILE_SIZE = 1024*64
"""
FlySight v1 files smaller than `MIN_JUMP_FILE_SIZE` are ignored because they
lack the minimum number of data points to contain a valid speed skydive.
"""


MPS_2_KMH = 3.6
"""
m/s to km/h conversion factor:

```python
s = mps * 60 * 60 / 1000
  = mps * 3600 / 1000
  = mps * 3.6
```
"""


PERFORMANCE_WINDOW_LENGTH = 2256.0
"""
Performance window length as defined by ISSA/IPC/USPA.
"""


SCORING_INTERVAL = 3.0
"""
Scoring is based on the maximum speed the jumper attained within the `VALIDATION_WINDOW_LENGTH`
as the average speed during a sliding window of SCORING_INTERVAL seconds.  The
value is set by governing bodies like ISC and USPA.
"""


SKYTRAX_1_HEADER = set([ 'time', 'lat', 'lon', 'hMSL', 'velN', 'velE', 'velD', 'hAcc', 'vAcc', 'sAcc', 'heading', 'cAcc', 'gpsFix', 'numSV', ])
"""
SkyTraX GPS + barometric SMD v1 CSV file headers.
"""


TABLE_INTERVAL = 5.0
"""
Speed run table interval.
"""


VALIDATION_WINDOW_LENGTH = 1006.0
"""
The validation window length as defined in the competition rules.
"""

