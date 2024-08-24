# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

"""
Functions and logic for detecting, validating, analyzing, and manipulating
FlySight 1 CSV files, including detection in the file system.  The functions in
this module assume that a data lake exists somewhere in the file system (whether
local or cloud-based).
"""


from ssscoring.constants import BREAKOFF_ALTITUDE
from ssscoring.constants import DEG_IN_RADIANS
from ssscoring.constants import EXIT_SPEED
from ssscoring.constants import FLYSIGHT_1_HEADER
from ssscoring.constants import FT_IN_M
from ssscoring.constants import IGNORE_LIST
from ssscoring.constants import LAST_TIME_TRANCHE
from ssscoring.constants import MAX_SPEED_ACCURACY
from ssscoring.constants import MIN_JUMP_FILE_SIZE
from ssscoring.constants import PERFORMANCE_WINDOW_LENGTH
from ssscoring.constants import VALIDATION_WINDOW_LENGTH
from ssscoring.datatypes import JumpResults
from ssscoring.datatypes import PerformanceWindow
from ssscoring.errors import SSScoringError

import csv
import math
import os

import pandas as pd


# +++ functions +++

def validFlySightHeaderIn(fileCSV: str) -> bool:
    """
    Checks if a file is a CSV in FlySight 1 format.  The checks include:

    - Whether the file is a CSV, using a comma delimiter
    - Checks for the presence of all the documented FlySight headers

    Arguments
    ---------
        fileCSV
    A file name to verify as a valid FlySight file

    Returns
    -------
    `True` if `fileCSV` is a FlySight CSV file, otherwise `False`.
    """
    delimiters =  [',', ]
    hasAllHeaders = False
    with open(fileCSV, 'r') as inputFile:
        try:
            dialect = csv.Sniffer().sniff(inputFile.readline(), delimiters = delimiters)
        except:
            return False
        if dialect.delimiter in delimiters:
            inputFile.seek(0)
            header = next(csv.reader(inputFile))
        else:
            return False
        hasAllHeaders = FLYSIGHT_1_HEADER.issubset(header)
    return hasAllHeaders


def isValidMinimumAltitude(altitude: float) -> bool:
    """
    Reports whether an `altitude` is within the IPC and USPA valid parameters,
    or within `BREAKOFF_ALTITUDE` and `PERFORMACE_WINDOW_LENGTH`.  In invalid
    altitude doesn't invalidate a FlySight data file.  This function can be used
    for generating warnings.  The stock FlySightViewer scores a speed jump even
    if the exit was below the minimum altitude.

    Arguments
    ---------
        altitude
    An altitude in meters, often calculated as data.hMSL - DZ altitude.

    Returns
    -------
    `True` if the altitude is valid.
    """
    minAltitude = BREAKOFF_ALTITUDE+PERFORMANCE_WINDOW_LENGTH
    return altitude >= minAltitude


def getAllSpeedJumpFilesFrom(dataLake: str) -> list:
    """
    Get a list of all the speed jump files from a data lake, where data lake is
    defined as a reachable path that contains one or more FlySight CSV files.
    This function tests each file to ensure that it's a speed skydive FlySight
    file in a valid format and length.

    Arguments
    ---------
        dataLake: str
    A valid (absolute or relative) path name to the top level directory where
    the data lake starts.

    Returns
    -------
    A list of speed jump file names for later SSScoring processing.
    """
    jumpFiles = list()
    for root, dirs, files in os.walk(dataLake):
        if any(name in root for name in IGNORE_LIST):
            continue
        for fileName in files:
            if 'CSV' in fileName:
                jumpFileName = os.path.join(root, fileName)
                stat = os.stat(jumpFileName)
                data = pd.read_csv(jumpFileName, skiprows = (1, 1))
                if stat.st_size >= MIN_JUMP_FILE_SIZE and validFlySightHeaderIn(jumpFileName) and isValidMinimumAltitude(data.hMSL.max()):
                    jumpFiles.append(jumpFileName)
    return jumpFiles


def convertFlySight2SSScoring(rawData: pd.DataFrame,
                              altitudeDZMeters = 0.0,
                              altitudeDZFt = 0.0):
    """
    Converts a raw dataframe initialized from a FlySight CSV file into the
    SSScoring file format.  The SSScoring format uses more descriptive column
    headers, adds the altitude in feet, and uses UNIX time instead of an ISO
    string.

    If both `altitudeDZMeters` and `altitudeDZFt` are zero then hMSL is used.
    Otherwise, this function adjusts the effective altitude with the value.  If
    both meters and feet values are set this throws an error.

    Arguments
    ---------
        rawData : pd.DataFrame
    FlySight CSV input as a dataframe

        altitudeDZMeters : float
    Drop zone height above MSL

        altitudeDZFt
    Drop zone altitudde above MSL

    Returns
    -------
    A dataframe in SSScoring format, featuring these columns:

    - timeUnix
    - altitudeMSL
    - altitudeAGL
    - altitudeMSLFt
    - altitudeAGLFt
    - hMetersPerSecond
    - hKMh (km/h)
    - vMetersPerSecond
    - vKMh (km/h)
    - angle
    - speedAccuracy

    Errors
    ------
    `SSScoringError` if the DZ altitude is set in both meters and feet.
    """
    if not isinstance(rawData, pd.DataFrame):
        raise SSScoringError('convertFlySight2SSScoring input must be a FlySight CSV dataframe')

    if altitudeDZMeters and altitudeDZFt:
        raise SSScoringError('Cannot set altitude in meters and feet; pick one')

    if altitudeDZMeters:
        altitudeDZFt = FT_IN_M*altitudeDZMeters
    if altitudeDZFt:
        altitudeDZMeters = altitudeDZFt/FT_IN_M

    data = rawData.copy()

    data['altitudeMSLFt'] = data['hMSL'].apply(lambda h: FT_IN_M*h)
    data['altitudeAGL'] = data.hMSL-altitudeDZMeters
    data['altitudeAGLFt'] = data.altitudeMSLFt-altitudeDZFt
    data['timeUnix'] = data['time'].apply(lambda t: pd.Timestamp(t).timestamp())
    data['hMetersPerSecond'] = (data.velE**2.0+data.velN**2.0)**0.5
    speedAngle = data['hMetersPerSecond']/data['velD']
    speedAngle = round(90.0-speedAngle.apply(math.atan)/DEG_IN_RADIANS, 1)

    data = pd.DataFrame(data = {
        'timeUnix': data.timeUnix,
        'altitudeMSL': data.hMSL,
        'altitudeAGL': data.altitudeAGL,
        'altitudeMSLFt': data.altitudeMSLFt,
        'altitudeAGLFt': data.altitudeAGLFt,
        'vMetersPerSecond': data.velD,
        'vKMh': 3.6*data.velD,
        'speedAngle': speedAngle,
        'speedAccuracy': data.sAcc,
        'hMetersPerSecond': data.hMetersPerSecond,
        'hKMh': 3.6*data.hMetersPerSecond,
    })

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
    timeMaxAlt = data[data.altitudeAGL == data.altitudeAGL.max()].timeUnix.iloc[0]
    data = data[data.timeUnix > timeMaxAlt]

    data = data[data.altitudeAGL > 0]

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
    MIN_DATA_POINTS = 100 # heuristic
    MIN_MAX_SPEED = 200 # km/h, heuristic; slower ::= no free fall
    for group in range(groups):
        subset = data[data.group == group]
        if len(subset) >= MIN_DATA_POINTS and subset.vKMh.max() >= MIN_MAX_SPEED:
            freeFallGroup = group

    data = data[data.group == freeFallGroup]
    data = data.drop('group', axis = 1).drop('positive', axis = 1)

    # Speed ~= 9.81 m/s; subtract 1 second for actual exit.
    exitTime = data[data.vMetersPerSecond > EXIT_SPEED].head(1).timeUnix.iat[0]-2.0
    # TODO:  Delete this as the upper bounds the next time you see this note.
    # data = data[data.vMetersPerSecond > EXIT_SPEED]
    data = data[data.timeUnix >= exitTime]
    data = data[data.altitudeAGL >= BREAKOFF_ALTITUDE]

    windowStart = data.iloc[0].altitudeAGL
    windowEnd = windowStart-PERFORMANCE_WINDOW_LENGTH
    if windowEnd < BREAKOFF_ALTITUDE:
        windowEnd = BREAKOFF_ALTITUDE

    validationWindowStart = windowEnd+VALIDATION_WINDOW_LENGTH
    data = data[data.altitudeAGL >= windowEnd]

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
    accuracy = data[data.altitudeAGL < window.validationStart].speedAccuracy.max()
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
        for interval in range(int(column)*10, 10*(int(column)+1)):
            # Use the next 0.1 sec interval if the current interval tranche has
            # NaN values.
            columnRef = interval/10.0
            timeOffset = data.iloc[0].timeUnix+columnRef
            tranche = data.query('timeUnix == %f' % timeOffset).copy()
            tranche['time'] = [ column, ]
            if not tranche.isnull().any().any():
                break

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
                'hKMh': table.hKMh,
                'speedAngle': table.speedAngle,
                'netVectorKMh': (table.vKMh**2+table.hKMh**2)**0.5,
                'altitude (ft)': table.altitudeAGLFt, })

    return (data.vKMh.max(), table)


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
    scores = dict()
    table = None

    if validJump:
        maxSpeed, table = jumpAnalysisTable(data)
        color = '#0f0'
        result = '🟢 valid'
        baseTime = data.iloc[0].timeUnix
        data['plotTime'] = data.timeUnix-baseTime

        for spot in data.plotTime:
            r0 = data[data.plotTime == spot]
            r1 = data[data.plotTime == spot+3.0]

            if not r1.empty:
                scores[0.5*(float(r0.vKMh.iloc[0])+float(r1.vKMh.iloc[0]))] = spot
        score = max(scores)

    else:
        color = '#f00'
        maxSpeed = -1
        score = 0
        result = '🔴 invalid'

    return JumpResults(color, data, maxSpeed, result, score, scores, table, window)



def processAllJumpFiles(jumpFiles: list, altitudeDZMeters = 0.0) -> dict:
    """
    Process all jump files in a list of valid FlySight files.  Returns a
    dictionary of jump results with a human-readable version of the file name.
    The `jumpFiles` list can be generated by hand or the output of the
    `ssscoring.getAllSpeedJumpFilesFrom` called to operate on a data lake.

    Arguments
    ---------
        jumpFiles
    A list of relative or absolute path names to individual FlySight CSV files.

        altitudeDZMeters : float
    Drop zone height above MSL

        dict
    A dictionary of jump results.  The key is a human-readable version of a
    `jumpFile` name with the extension, path, and extraneous spaces eliminated
    or replaced by appropriate characters.  File names use Unicode, so accents
    and non-ANSI characters are allowed in file names.
    """
    jumpResults = dict()
    for jumpFile in jumpFiles:
        jumpResult = processJump(
            convertFlySight2SSScoring(pd.read_csv(jumpFile, skiprows = (1, 1)),
            altitudeDZMeters = altitudeDZMeters))
        tag = jumpFile.replace('CSV', '').replace('.', '').replace('/data', '').replace('/', ' ').strip()
        if 'valid' in jumpResult.result:
            jumpResults[tag] = jumpResult
    return jumpResults


def aggregateResults(jumpResults: dict) -> pd.DataFrame:
    """
    Aggregate all the results in a table fashioned after Marco Hepp's and Nklas
    Daniel's score tracking data.

    Arguments
    ---------
        jumpResults: dict
    A dictionary of jump results, in which each result corresponds to a FlySight
    file name.  See `ssscoring.processAllJumpFiles` for details.

    Returns
    -------
    A dataframe featuring these columns:

    - Score
    - Speeds at 5, 10, 15, 20, and 25 second tranches
    - Final time contemplated in the analysis
    - Max speed

    The dataframe rows are identified by the human readable jump file name.
    """
    speeds = pd.DataFrame()
    for jumpResultIndex in sorted(list(jumpResults.keys())):
        jumpResult = jumpResults[jumpResultIndex]
        if jumpResult.score > 0.0:
            t = jumpResult.table
            finalTime = t.iloc[-1].time
            t.iloc[-1].time = LAST_TIME_TRANCHE
            t = pd.pivot_table(t, columns = t.time)
            t.drop(['altitude (ft)'], inplace = True)
            d = pd.DataFrame([ jumpResult.score, ], index = [ jumpResultIndex, ], columns = [ 'score', ], dtype = object)
            for column in t.columns:
                d[column] = t[column].iloc[3]
            d['finalTime'] = [ finalTime, ]
            d['maxSpeed'] = jumpResult.maxSpeed

            if speeds.empty:
                speeds = d.copy()
            else:
                speeds = pd.concat([ speeds, d, ])
    return speeds.sort_index()


def roundedAggregateResults(jumpResults: dict) -> pd.DataFrame:
    """
    Aggregate all the results in a table fashioned after Marco Hepp's and Nklas
    Daniel's score tracking data.  All speed results are rounded at `n > x.5`
    for any value.

    Arguments
    ---------
        jumpResults: dict
    A dictionary of jump results, in which each result corresponds to a FlySight
    file name.  See `ssscoring.processAllJumpFiles` for details.

    Returns
    -------
    A dataframe featuring the **rounded values** for these columns:

    - Score
    - Speeds at 5, 10, 15, 20, and 25 second tranches
    - Max speed

    The `finalTime` column is ignored.

    The dataframe rows are identified by the human readable jump file name.

    This is a less precise version of the `ssscoring.aggregateResults`
    dataframe, useful during training to keep rounded results available for
    review.
    """
    aggregate = aggregateResults(jumpResults)
    for column in [col for col in aggregate.columns if 'Time' not in str(col)]:
        aggregate[column] = aggregate[column].apply(round)

    return aggregate


def totalResultsFrom(aggregate: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the total and mean speeds for an aggregation of speed jumps.

    Arguments
    ---------
        aggregate: pd.DataFrame
    The aggregate results dataframe resulting from calling `ssscoring.aggregateResults`
    with valid results.

    Returns
    -------
    A dataframe with one row and two columns:

    - totalSpeed ::= the sum of all speeds in the aggregated results
    - meanSpeed ::= the mean of all speeds
    - maxScore ::= the max score among all the speed scores

    Raises
    ------
    `AttributeError` if aggregate is an empty dataframe or `None`, or if the
    `aggregate` dataframe doesn't conform to the output of `ssscoring.aggregateResults`.
    """
    totals = pd.DataFrame({ 'totalSpeed': [ aggregate.score.sum(), ], 'meanSpeed': [ aggregate.score.mean(), ], 'maxScore': [ aggregate.score.max(), ], }, index = [ 'totalSpeed'],)

    return totals


