# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

"""
Functions and logic for detecting, validating and manipulating
FlySight CSV files, including detection in the file system.  The functions in
this module assume that a data lake exists somewhere in the file system (whether
local or cloud-based).
"""


from enum import Enum

from ssscoring.constants import FLYSIGHT_1_HEADER
from ssscoring.constants import IGNORE_LIST
from ssscoring.constants import MIN_JUMP_FILE_SIZE
from ssscoring.errors import SSScoringError

import csv
import os

import pandas as pd


# +++ constants +++

FS2_COLUMNS = ('GNSS', 'time', 'lat', 'lon', 'hMSL', 'velN', 'velE', 'velD', 'hAcc', 'vAcc', 'sAcc', 'numSV', )


# --- classes and objects ---

class FlySightVersion(Enum):
    V1 = 1000
    V2 = 2000



# +++ functions +++


def skipOverFS2MetadataRowsIn(data: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a clean dataframe on which any metadata rows within the first 100
    are skipped.  This function uses the `time` column to detect valid rows.  A
    `time == NaN` is considered invalid and skipped.

    Arguments
    ---------
        data
    A FlySight 2 dataframe suspected of having dirty N first rows with metadata

    Returns
    -------
    A FlySight 2 clean dataframe without any leading metadata rows.
    """
    for ref in range(0,100):
        if pd.notnull(data.iloc[ref].time):
            break
    return data.iloc[ref:]


def validFlySightHeaderIn(fileCSV: str) -> bool:
    """
    Checks if a file is a CSV in FlySight 1 or FlySight 2 formats.  The checks
    include:

    - Whether the file is a CSV, using a comma delimiter
    - Checks for the presence of all the documented FlySight 1 headers
    - Checks for the presence of the FlySight 2 line 1 identifier

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
        hasAllHeaders = True if header[0] == '$FLYS' else FLYSIGHT_1_HEADER.issubset(header)
    return hasAllHeaders


def getAllSpeedJumpFilesFrom(dataLake: str) -> dict:
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
    A dictionary of speed jump file names for later SSScoring processing:
        - keys are the file names
        - values are a FlySight version string tag
    """
    from ssscoring.calc import isValidMinimumAltitude # skirt circular dependency

    jumpFiles = dict()
    for root, dirs, files in os.walk(dataLake):
        if any(name in root for name in IGNORE_LIST):
            continue
        for fileName in files:
            data = None
            if '.swp' in fileName: # Ignore Vim, other editors swap file
                continue
            if '.CSV' in fileName:
                version = '1'
                jumpFileName = os.path.join(root, fileName)
                stat = os.stat(jumpFileName)
                if all(x not in fileName for x in ('EVENT', 'SENSOR', 'TRACK')):
                    # FlySight 1 track format
                    data = pd.read_csv(jumpFileName, skiprows = (1, 1))
                elif 'TRACK' in fileName:
                    # FlySight 2 track custom format
                    data = pd.read_csv(jumpFileName, names = FS2_COLUMNS, skiprows = 6)
                    data = skipOverFS2MetadataRowsIn(data)
                    data.drop('GNSS', inplace = True, axis = 1)
                    version = '2'
                if data is not None and stat.st_size >= MIN_JUMP_FILE_SIZE and validFlySightHeaderIn(jumpFileName) and isValidMinimumAltitude(data.hMSL.max()):
                    # explicit because `not data` is ambiguous for dataframes
                    jumpFiles[jumpFileName] = version
    return jumpFiles


def detectFlySightFileVersionOf(fileName: str) -> FlySightVersion:
    """
    Detects the FlySight file version based on its file name and format.

    Arguments
    ---------
        fileName
    A string corresponding to the file name.

    Returns
    -------
    An instance of `ssscoring.flysight.FlySightVersion` with a valid version
    symbolic value.

    Errors
    ------
    `ssscoring.errors.SSScoringError` if the file is not a CSV and it's some
    other invalid format.
    """
    if not '.CSV' in fileName:
        raise SSScoringError('Invalid file extension type')
    if any(x in fileName for x in ('EVENT.CSV', 'SENSOR.CSV')):
        raise SSScoringError('Only TRACK.CSV v2 files can be processed at this time')
    if not os.path.exists(fileName):
        raise SSScoringError('%s - file not found in data lake' % fileName)
    if not validFlySightHeaderIn(fileName):
        raise SSScoringError('CSV is not a valid FlySight file')
    delimiters =  [',', ]
    with open(fileName, 'r') as inputFile:
        try:
            dialect = csv.Sniffer().sniff(inputFile.readline(), delimiters = delimiters)
        except:
            raise SSScoringError('Error while trying to validate %s file format' % fileName)
        if dialect.delimiter in delimiters:
            inputFile.seek(0)
            header = next(csv.reader(inputFile))
        else:
            raise SSScoringError('CSV uses a different delimiter from FlySigh')
    if header[0] == '$FLYS':
        return FlySightVersion.V2
    elif FLYSIGHT_1_HEADER.issubset(header):
        return FlySightVersion.V1
    else:
        raise SSScoringError('%s file is not a FlySight v1 or v2 file')
