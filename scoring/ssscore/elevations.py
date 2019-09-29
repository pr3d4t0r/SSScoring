# vim: set fileencoding=utf-8:

# BSD 3-Clause License -- see ../../LICENSE for details.


from enum import Enum
from enum import unique


# Drop zone name, altitude in meters

@unique
class DZElevations(Enum):
    BAY_AREA_SKYDIVING           =   23.90
    CHICAGOLAND_SKYDIVING_CENTER =  238.00
    SKYDANCE_SKYDIVING           =   30.48
    SKYDIVE_ALGARVE              =    2.00
    SKYDIVE_ARIZONA              =  460.60
    SKYDIVE_BUZZ                 =  256.00
    SKYDIVE_BUZZ                 = 253.00
    SKYDIVE_FANO                 =   54.00
    SKYDIVE_FLANDERS_ZWARTBERG   =   85.00
    SKYDIVE_SAULGAU              =  581.00
    SKYDIVE_TAFT                 =  266.70
    SKYDIVE_UTAH                 = 1317.04

