# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

"""
Functions and logic for analyzing and manipulating FlySight dataframes.
"""


from io import BytesIO
from io import StringIO
from pathlib import Path

from haversine import haversine
from haversine import Unit

from ssscoring.constants import BREAKOFF_ALTITUDE
from ssscoring.constants import DEG_IN_RADIANS
from ssscoring.constants import EXIT_SPEED
from ssscoring.constants import FLYSIGHT_FILE_ENCODING
from ssscoring.constants import FT_IN_M
from ssscoring.constants import KMH_AS_MS
from ssscoring.constants import LAST_TIME_TRANCHE
from ssscoring.constants import MAX_ALTITUDE_METERS
from ssscoring.constants import SPEED_ACCURACY_THRESHOLD
from ssscoring.constants import MPS_2_KMH
from ssscoring.constants import PERFORMANCE_WINDOW_LENGTH
from ssscoring.constants import SCORING_INTERVAL
from ssscoring.constants import TABLE_INTERVAL
from ssscoring.constants import VALIDATION_WINDOW_LENGTH
from ssscoring.datatypes import JumpResults
from ssscoring.datatypes import JumpStatus
from ssscoring.datatypes import PerformanceWindow
from ssscoring.errors import SSScoringError
from ssscoring.flysight import FlySightVersion
from ssscoring.flysight import detectFlySightFileVersionOf

import math

import numpy as np
import pandas as pd


# +++ functions +++

def isValidMinimumAltitude(altitude: float) -> bool:
    """
    Reports whether an `altitude` is below the IPC and USPA valid parameters,
    or within `BREAKOFF_ALTITUDE` and `PERFORMACE_WINDOW_LENGTH`.  In invalid
    altitude doesn't invalidate a FlySight data file.  This function can be used
    for generating warnings.  The stock FlySightViewer scores a speed jump even
    if the exit was below the minimum altitude.

    See:  FAI Competition Rules Speed Skydiving section 5.3 for details.

    Arguments
    ---------
        altitude
    An altitude in meters, calculated as data.hMSL - DZ altitude.

    Returns
    -------
    `True` if the altitude is valid.
    """
    if not isinstance(altitude, float):
        altitude = float(altitude)
    minAltitude = BREAKOFF_ALTITUDE+PERFORMANCE_WINDOW_LENGTH
    return altitude >= minAltitude


def isValidMaximumAltitude(altitude: float) -> bool:
    """
    Reports whether an `altitude` is above the maximum altitude allowed by the
    rules.

    See:  FAI Competition Rules Speed Skydiving section 5.3 for details.

    Arguments
    ---------
        altitude
    An altitude in meters, calculated as data.hMSL - DZ altitude.

    Returns
    -------
    `True` if the altitude is valid.

    See
    ---
    `ssscoring.constants.MAX_ALTITUDE_FT`
    `ssscoring.constants.MAX_ALTITUDE_METERS`
    """
    if not isinstance(altitude, float):
        altitude = float(altitude)
    return altitude <= MAX_ALTITUDE_METERS


def isValidJumpISC(data: pd.DataFrame,
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
    if len(data) > 0:
        accuracy = data[data.altitudeAGL <= window.validationStart].speedAccuracyISC.max()
        return accuracy < SPEED_ACCURACY_THRESHOLD
    else:
        return False


def calculateDistance(start: tuple, end: tuple) -> float:
    """
    Calculate the distance between two terrestrial coordinates points.

    Arguments
    ---------
        start
    A latitude, longitude tuple of floating point numbers.

        end
    A latitude, longitude tuple of floating point numbers.

    Returns
    -------
    The distance, in meters, between both points.
    """
    return haversine(start, end, unit = Unit.METERS)


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
    - speedAccuracy (ignore; see ISC documentation)
    - hMetersPerSecond
    - hKMh
    - latitude
    - longitude
    - verticalAccuracy
    - speedAccuracyISC

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
    data['timeUnix'] = np.round(data['time'].apply(lambda t: pd.Timestamp(t).timestamp()), decimals = 2)
    data['hMetersPerSecond'] = (data.velE**2.0+data.velN**2.0)**0.5
    speedAngle = data['hMetersPerSecond']/data['velD']
    speedAngle = np.round(90.0-speedAngle.apply(math.atan)/DEG_IN_RADIANS, decimals = 2)
    speedAccuracyISC = np.round(data.vAcc.apply(lambda a: (2.0**0.5)*a/3.0), decimals = 2)

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
        'latitude': data.lat,
        'longitude': data.lon,
        'verticalAccuracy': data.vAcc,
        'speedAccuracyISC': speedAccuracyISC,
    })

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

    Warm up FlySight files and non-speed skydiving files may return invalid
    values:

    - `None` for the `PerformanceWindow` instance
    - `data`, most likely empty
    """
    if len(data):
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

    if len(data) > 0:
        exitTime = data[data.vMetersPerSecond > EXIT_SPEED].head(1).timeUnix.iat[0]
        data = data[data.timeUnix >= exitTime]
        data = data[data.altitudeAGL >= BREAKOFF_ALTITUDE]

        windowStart = data.iloc[0].altitudeAGL
        windowEnd = windowStart-PERFORMANCE_WINDOW_LENGTH
        if windowEnd < BREAKOFF_ALTITUDE:
            windowEnd = BREAKOFF_ALTITUDE

        validationWindowStart = windowEnd+VALIDATION_WINDOW_LENGTH
        data = data[data.altitudeAGL >= windowEnd]

        return PerformanceWindow(windowStart, windowEnd, validationWindowStart), data
    else:
        return None, data


def _verticalAcceleration(vKMh: pd.Series, time: pd.Series, interval=TABLE_INTERVAL) -> pd.Series:
    vAcc = ((vKMh/KMH_AS_MS).diff()/time.diff()).fillna(vKMh/KMH_AS_MS/interval)
    return vAcc


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
    distanceStart = (data.iloc[0].latitude, data.iloc[0].longitude)
    for column in pd.Series([ 5.0, 10.0, 15.0, 20.0, 25.0, ]):
        for interval in range(int(column)*10, 10*(int(column)+1)):
            # Use the next 0.1 sec interval if the current interval tranche has
            # NaN values.
            columnRef = interval/10.0
            timeOffset = data.iloc[0].timeUnix+columnRef
            tranche = data.query('timeUnix == %f' % timeOffset).copy()
            tranche['time'] = [ column, ]
            currentPosition = (tranche.iloc[0].latitude, tranche.iloc[0].longitude)
            tranche['distanceFromExit'] = [ round(calculateDistance(distanceStart, currentPosition), 2), ]
            if not tranche.isnull().any().any():
                break

        if pd.isna(tranche.iloc[-1].vKMh):
            tranche = data.tail(1).copy()
            currentPosition = (tranche.iloc[0].latitude, tranche.iloc[0].longitude)
            tranche['time'] = tranche.timeUnix-data.iloc[0].timeUnix
            tranche['distanceFromExit'] = [ round(calculateDistance(distanceStart, currentPosition), 2), ]

        if table is not None:
            table = pd.concat([ table, tranche, ])
        else:
            table = tranche
    table = pd.DataFrame({
                'time': table.time,
                'vKMh': table.vKMh,
                'deltaV': table.vKMh.diff().fillna(table.vKMh),
                'vAccel m/s²': _verticalAcceleration(table.vKMh, table.time),
                'speedAngle': table.speedAngle,
                'angularVel º/s': (table.speedAngle.diff()/table.time.diff()).fillna(table.speedAngle/TABLE_INTERVAL),
                'deltaAngle': table.speedAngle.diff().fillna(table.speedAngle),
                'hKMh': table.hKMh,
                'distanceFromExit (m)': table.distanceFromExit,
                'altitude (ft)': table.altitudeAGLFt,
            })
    return table


def dropNonSkydiveDataFrom(data: pd.DataFrame) -> pd.DataFrame:
    """
    Discards all data rows before maximum altitude, and all "negative" altitude
    rows because we don't skydive underground (FlySight bug?).

    This is a more accurate mean velocity calculation from a physics point of
    view, but it differs from the ISC definition using in scoring - which, if we
    get technical, is the one that counts.

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


def calcScoreMeanVelocity(data: pd.DataFrame) -> tuple:
    """
    Calculates the speeds over a 3-second interval as the mean of all the speeds
    recorded within that 3-second window and resolves the maximum speed.

    Arguments
    ---------
        data
    A `pd.dataframe` with speed run data.

    Returns
    -------
    A `tuple` with the best score throughout the speed run, and a dicitionary
    of the meanVSpeed:spotInTime used in determining the exact scoring speed
    at every datat point during the speed run.

    Notes
    -----
    This implementation uses iteration instead of binning/factorization because
    some implementers may be unfamiliar with data manipulation in dataframes
    and this is a critical function that may be under heavy review.  Future
    versions may revert to dataframe and series/np.array factorization.
    """
    scores = dict()
    for spot in data.plotTime[::1]:
        subset = data[(data.plotTime <= spot) & (data.plotTime >= (spot-SCORING_INTERVAL))]
        scores[np.round(subset.vKMh.mean(), decimals = 2)] = spot
    return (max(scores), scores)


def calcScoreISC(data: pd.DataFrame) -> tuple:
    """
    Calculates the speeds over a 3-second interval as the ds/dt and dt is the
    is a 3-second sliding interval from exit.  The window slider moves along the
    `plotTime` axis in the dataframe.

    Arguments
    ---------
        data
    A `pd.dataframe` with speed run data.

    Returns
    -------
    A `tuple` with the best score throughout the speed run, and a dicitionary
    of the meanVSpeed:spotInTime used in determining the exact scoring speed
    at every datat point during the speed run.
    """
    scores = dict()
    step = data.plotTime.diff().dropna().mode().iloc[0]
    end = data.plotTime[-1:].iloc[0]-SCORING_INTERVAL
    for spot in np.arange(0.0, end, step):
        intervalStart = np.round(spot, decimals = 2)
        intervalEnd = np.round(intervalStart+SCORING_INTERVAL, decimals = 2)
        try:
            h1 = data[data.plotTime == intervalStart].altitudeAGL.iloc[0]
            h2 = data[data.plotTime == intervalEnd].altitudeAGL.iloc[0]
        except IndexError:
            # TODO: Decide whether to log the missing FlySight samples.
            continue
        intervalScore = np.round(MPS_2_KMH*abs(h1-h2)/SCORING_INTERVAL, decimals = 2)
        scores[intervalScore] = intervalStart
    return (max(scores), scores)


def processJump(data: pd.DataFrame) -> JumpResults:
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
    workData = data.copy()
    workData = dropNonSkydiveDataFrom(workData)
    window, workData = getSpeedSkydiveFrom(workData)
    if workData.empty and not window:
        workData = None
        maxSpeed = -1.0
        score = -1.0
        scores = None
        table = None
        window = None
        jumpStatus = JumpStatus.WARM_UP_FILE
    else:
        validJump = isValidJumpISC(workData, window)
        jumpStatus = JumpStatus.OK
        score = None
        scores = None
        table = None
        if validJump:
            table = None
            table = jumpAnalysisTable(workData)
            maxSpeed = data.vKMh.max()
            baseTime = workData.iloc[0].timeUnix
            workData['plotTime'] = round(workData.timeUnix-baseTime, 2)
            score, scores = calcScoreISC(workData)
        else:
            maxSpeed = -1
            if len(workData):
                jumpStatus = JumpStatus.SPEED_ACCURACY_EXCEEDS_LIMIT
            else:
                jumpStatus = JumpStatus.INVALID_SPEED_FILE
    return JumpResults(workData, maxSpeed, score, scores, table, window, jumpStatus)


def _readVersion1CSV(fileThing: str) -> pd.DataFrame:
    return pd.read_csv(fileThing, skiprows = (1, 1), index_col = False)


def _tagVersion1From(fileThing: str) -> str:
    return fileThing.replace('.CSV', '').replace('.csv', '').replace('/data', '').replace('/', ' ').strip()+':v1'


def _tagVersion2From(fileThing: str) -> str:
    if '/' in fileThing:
        return fileThing.split('/')[-2]+':v2'
    else:
        return fileThing.replace('.CSV', '').replace('.csv', '')+':v2'



def _readVersion2CSV(jumpFile: str) -> pd.DataFrame:
    from ssscoring.constants import FLYSIGHT_2_HEADER
    from ssscoring.flysight import skipOverFS2MetadataRowsIn

    rawData = pd.read_csv(jumpFile, names = FLYSIGHT_2_HEADER, skiprows = 6, index_col = False)
    rawData = skipOverFS2MetadataRowsIn(rawData)
    rawData.drop('GNSS', inplace = True, axis = 1)
    return rawData


def getFlySightDataFromCSVBuffer(buffer:bytes, bufferName:str) -> tuple:
    """
    Ingress a buffer with known FlySight or SkyTrax file data for SSScoring
    processing.

    Arguments
    ---------
        buffer
    A binary data buffer, bag of bytes, containing a known FlySight track file.

        bufferName
    An arbitrary name for the buffer of type `str`.  It's used for constructing
    the full buffer tag value for human identification.

    Returns
    -------
    A `tuple` with two items:
        - `rawData` - a dataframe representation of the CSV with the original
          headers but without the data type header
        - `tag` - a string with an identifying tag derived from the path name
          and file version in the form `some name:vX`.  It uses the current
          path as metadata to infer the name.  There's no semantics enforcement.

    Raises
    ------
    `SSScoringError` if the CSV file is invalid in any way.
    """
    if not isinstance(buffer, bytes):
        raise SSScoringError('buffer must be an instance of bytes, a bytes buffer')
    try:
        stringIO = StringIO(buffer.decode(FLYSIGHT_FILE_ENCODING))
    except Exception as e:
        raise SSScoringError('invalid buffer endcoding - %s' % str(e))
    version = detectFlySightFileVersionOf(buffer)
    if version == FlySightVersion.V1:
        rawData = _readVersion1CSV(stringIO)
        tag = _tagVersion1From(bufferName)
    elif version == FlySightVersion.V2:
        rawData = _readVersion2CSV(stringIO)
        tag = _tagVersion2From(bufferName)
    return (rawData, tag)


def getFlySightDataFromCSVFileName(jumpFile) -> tuple:
    """
    Ingress a known FlySight or SkyTrax file into memory for SSScoring
    processing.

    Arguments
    ---------
        jumpFile
    A string or `pathlib.Path` object; can be a relative or an asbolute path.

    Returns
    -------
    A `tuple` with two items:
        - `rawData` - a dataframe representation of the CSV with the original
          headers but without the data type header
        - `tag` - a string with an identifying tag derived from the path name
          and file version in the form `some name:vX`.  It uses the current
          path as metadata to infer the name.  There's no semantics enforcement.

    Raises
    ------
    `SSScoringError` if the CSV file is invalid in any way.
    """
    from ssscoring.flysight import validFlySightHeaderIn

    if isinstance(jumpFile, Path):
        jumpFile = jumpFile.as_posix()
    elif isinstance(jumpFile, str):
        pass
    else:
        raise SSScoringError('jumpFile must be a string or a Path object')
    if not validFlySightHeaderIn(jumpFile):
        raise SSScoringError('%s is an invalid speed skydiving file')
    version = detectFlySightFileVersionOf(jumpFile)
    if version == FlySightVersion.V1:
        rawData = _readVersion1CSV(jumpFile)
        tag = _tagVersion1From(jumpFile)
    elif version == FlySightVersion.V2:
        rawData = _readVersion2CSV(jumpFile)
        tag = _tagVersion2From(jumpFile)
    return (rawData, tag)


def processAllJumpFiles(jumpFiles: list, altitudeDZMeters = 0.0) -> dict:
    """
    Process all jump files in a list of valid FlySight files.  Returns a
    dictionary of jump results with a human-readable version of the file name.
    The `jumpFiles` list can be generated by hand or the output of the
    `ssscoring.fs1.getAllSpeedJumpFilesFrom` called to operate on a data lake.

    Arguments
    ---------
        jumpFiles
    A list of file things that could represent one of these:
    - file things relative or absolute path names to individual FlySight CSV
      files.
    - A specialization of BytesIO, such as the bags of bytes that Streamlit.io
      generates after uploading and reading a file into the Streamlit
      environment

        altitudeDZMeters : float
    Drop zone height above MSL

    Returns
    -------
        dict
    A dictionary of jump results.  The key is a human-readable version of a
    `jumpFile` name with the extension, path, and extraneous spaces eliminated
    or replaced by appropriate characters.  File names use Unicode, so accents
    and non-ANSI characters are allowed in file names.

    Raises
    ------
    `SSScoringError` if the jumpFiles object is empty, or if the individual
    objects in the list aren't `BytesIO`, file name strings, or `Path`
    instances.
    """
    jumpResults = dict()
    if not len(jumpFiles):
        raise SSScoringError('jumpFiles must have at least one element')
    if not isinstance(jumpFiles, dict) and not isinstance(jumpFiles, list):
        raise SSScoringError('dict with jump file names and FS versions or list of byte bags expected')
    if isinstance(jumpFiles, dict):
        objectsList = sorted(list(jumpFiles.keys()))
    elif isinstance(jumpFiles, list):
        objectsList = jumpFiles
    obj = objectsList[0]
    if not isinstance(obj, Path) and not isinstance(obj, str) and not isinstance(obj, BytesIO):
        raise SSScoringError('jumpFiles must contain file-like things or BytesIO objects')
    for jumpFile in objectsList:
        if isinstance(jumpFile, BytesIO):
            rawData, tag = getFlySightDataFromCSVBuffer(jumpFile.getvalue(), jumpFile.name)
        else:
            rawData, tag = getFlySightDataFromCSVFileName(jumpFile)
        jumpResult = processJump(convertFlySight2SSScoring(rawData, altitudeDZMeters = altitudeDZMeters))
        if JumpStatus.OK == jumpResult.status:
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
        # TODO: if jumpResult.score > 0.0:
        if jumpResult.status == JumpStatus.OK:
            t = jumpResult.table
            finalTime = t.iloc[-1].time
            t.iloc[-1].time = LAST_TIME_TRANCHE
            t = pd.pivot_table(t, columns = t.time)
            t.drop(['altitude (ft)'], inplace = True)
            d = pd.DataFrame([ jumpResult.score, ], index = [ jumpResultIndex, ], columns = [ 'score', ], dtype = object)
            for column in t.columns:
                # d[column] = t[column].iloc[2]
                d[column] = t[column].vKMh
            d['finalTime'] = [ finalTime, ]
            d['maxSpeed'] = jumpResult.maxSpeed

            if speeds.empty:
                speeds = d.copy()
            else:
                speeds = pd.concat([ speeds, d, ])
    return speeds.sort_index()


def roundedAggregateResults(aggregate: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate all the results in a table fashioned after Marco Hepp's and Nklas
    Daniel's score tracking data.  All speed results are rounded at `n > x.5`
    for any value.

    Arguments
    ---------
        aggregate: pd.DataFrame
    A dataframe output of `ssscoring.fs1.aggregateResults`.

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
    - maxSpeed := the absolute max speed over the speed runs set
    - meanSpeedSTD := scored speeds standar deviation
    - maxScore ::= the max score among all the speed scores
    - maxScoreSTD := the max scores standard deviation

    Raises
    ------
    `AttributeError` if aggregate is an empty dataframe or `None`, or if the
    `aggregate` dataframe doesn't conform to the output of `ssscoring.aggregateResults`.
    """
    if aggregate is None:
        raise AttributeError('aggregate dataframe is empty')
    elif isinstance(aggregate, pd.DataFrame) and not len(aggregate):
        raise AttributeError('aggregate dataframe is empty')

    totals = pd.DataFrame({
        'totalScore': [ round(aggregate.score.sum(), 2), ],
        'mean': [ round(aggregate.score.mean(), 2), ],
        'deviation': [ round(aggregate.score.std(), 2), ],
        'maxScore': [ round(aggregate.score.max(), 2), ],
        'absMaxSpeed': [ round(aggregate.maxSpeed.max(), 2), ], }, index = [ 'totalSpeed'],)
    return totals

