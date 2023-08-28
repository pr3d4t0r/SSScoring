# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt


__VERSION__ = '1.2.0'


from collections import namedtuple

from ssscoring.errors import SSScoringError

import pandas as pd


# +++ constants +++

# All measurements expressed in meters unless noted
BREAKOFF_ALTITUDE = 1707.0
EXIT_SPEED = 9.0
MAX_SPEED_ACCURACY = 3.0
PERFORMANCE_WINDOW_LENGTH = 2256.0
VALIDATION_WINDOW_LENGTH = 1006.0


# +++ type definitions +++

PerformanceWindow = namedtuple("PerformanceWindow", "start end validationStart")


# +++ functions +++

def convertFlySight2SSScoring(rawData: pd.DataFrame):
    """
    Converts a raw dataframe initialized from a FlySight CSV file into the
    SSScoring file format.  The SSScoring format uses more descriptive column
    headers, adds the altitude in feet, and uses UNIX time instead of an ISO
    string.

    Arguments
    ---------
        rawData : pd.DataFrame
    FlySight CSV input as a dataframe

    Returns
    -------
    A dataframe in SSScoring format, featuring these columns:

    - timeUnix
    - heightMSL
    - heightFt
    - vMetersPerSecond
    - vKMh (km/h)
    - speedAccuracy
    """
    if not isinstance(rawData, pd.DataFrame):
        raise SSScoringError('convertFlySight2SSScoring input must be a FlySight CSV dataframe')

    data = rawData.copy()

    data['heightFt'] = data['hMSL'].apply(lambda h: 3.2808*h)
    data['timeUnix'] = data['time'].apply(lambda t: pd.Timestamp(t).timestamp())

    data = pd.DataFrame(data = {
        'timeUnix': data.timeUnix,
        'heightMSL': data.hMSL,
        'heightFt': data.heightFt,
        'vMetersPerSecond': data.velD,
        'vKMh': data.velD*3.6,
        'speedAccuracy': data.sAcc, })

    return data


def dropNonSkydiveDataFrom(data: pd.DataFrame) -> pd.DataFrame:
    """
    Discards all data rows before maximum altitude, and all "negative" altitude
    rows because we don't skydive underground (FlySight bug?).

    Arguments
    ---------
        data : pd.DataFrame
    Jump data in SSScoring format (headers differ from FlySight format)

    Returns
    -------
    The jump data for the skydive
    """
    timeMaxAlt = data[data.heightMSL == data.heightMSL.max()].timeUnix.iloc[0]
    data = data[data.timeUnix > timeMaxAlt]

    data = data[data.heightMSL > 0]

    return data


def _dataGroups(data):
    data_ = data.copy()
    data_['positive'] = (data_.vMetersPerSecond > 0)
    data_['group'] = (data_.positive != data_.positive.shift(1)).astype(int).cumsum()-1

    return data_


def getSpeedSkydiveFrom(data: pd.DataFrame) -> tuple:
    """
    Take the skydive dataframe and get the speed skydiving data:

    - Exit
    - Speed skydiving window
    - Drops data before exit and below breakoff altitude

    Arguments
    ---------
        data : pd.DataFrame
    Jump data in SSScoring format

    Returns
    -------
    A tuple of two elements:

    - A named tuple with performance and validation window data
    - A dataframe featuring only speed skydiving data
    """
    data = _dataGroups(data)
    groups = data.group.max()+1

    freeFallGroup = -1
    dataPoints = -1
    for group in range(groups):
        subset = data[data.group == group]
        if len(subset) > dataPoints:
            freeFallGroup = group
            dataPoints = len(subset)

    data = data[data.group == freeFallGroup]
    data = data.drop('group', axis = 1).drop('positive', axis = 1)

    data = data[data.vMetersPerSecond > EXIT_SPEED]
    data = data[data.heightMSL >= BREAKOFF_ALTITUDE]

    windowStart = data.iloc[0].heightMSL
    windowEnd = windowStart-PERFORMANCE_WINDOW_LENGTH
    if windowEnd < BREAKOFF_ALTITUDE:
        windowEnd = BREAKOFF_ALTITUDE

    validationWindowStart = windowEnd+VALIDATION_WINDOW_LENGTH
    data = data[data.heightMSL >= windowEnd]

    return PerformanceWindow(windowStart, windowEnd, validationWindowStart), data


def isValidJump(data: pd.DataFrame,
                window: PerformanceWindow) -> bool:
    """
    Validates the jump according to ISC/FAI/USPA competition rules.  A jump is
    valid when the speed accuracy parameter is less than 3 m/s for the whole
    validation window duration.

    Arguments
    ---------
        data : pd.DataFramce
    Jumnp data in SSScoring format
        window : ssscoring.PerformanceWindow
    Performance window start, end values in named tuple format

    Returns
    -------
    `True` if the jump is valid according to ISC/FAI/USPA rules.
    """
    accuracy = data[data.heightMSL < window.validationStart].speedAccuracy.max()
    return accuracy < MAX_SPEED_ACCURACY


def jumpAnalysisTable(data: pd.DataFrame) -> pd.DataFrame:
    """
    Generates the HCD jump analysis table, with speed data at 5-second intervals
    after exit.

    Arguments
    ---------
        data : pd.DataFrame
    Jump data in SSScoring format

    Returns
    -------
    A tuple with a pd.DataFrame and the max speed recorded for the jump:

    - A table dataframe with time and speed
    - a floating point number
    """
    table = None

    for column in pd.Series([ 5.0, 10.0, 15.0, 20.0, 25.0, ]):
        timeOffset = data.iloc[0].timeUnix+column
        tranche = data.query('timeUnix == %f' % timeOffset).copy()
        tranche['time'] = [ column, ]

        if pd.isna(tranche.iloc[-1].vKMh):
            tranche = data.tail(1).copy()
            tranche['time'] = tranche.timeUnix-data.iloc[0].timeUnix

        if table is not None:
            table = pd.concat([ table, tranche, ])
        else:
            table = tranche

    table = pd.DataFrame({
                'time': table.time,
                'vKMh': table.vKMh,
                'altitude (ft)': table.heightFt, })

    return (data.vKMh.max(), table)



