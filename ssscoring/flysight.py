# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

"""
Functions and logic for detecting, validating and manipulating
FlySight CSV files, including detection in the file system.  The functions in
this module assume that a data lake exists somewhere in the file system (whether
local or cloud-based).
"""


from collections import OrderedDict
from io import StringIO
from pathlib import Path

from ssscoring.constants import FLYSIGHT_1_HEADER
from ssscoring.constants import FLYSIGHT_2_HEADER
from ssscoring.constants import FLYSIGHT_FILE_ENCODING
from ssscoring.constants import INSIGHT_1_HEADER
from ssscoring.constants import IGNORE_LIST
from ssscoring.constants import MIN_JUMP_FILE_SIZE
from ssscoring.datatypes import FlySightVersion
from ssscoring.errors import SSScoringError

import csv
import os
import shutil
import tempfile

import pandas as pd


# +++ functions +++

def _isInsightHeader(header: list) -> bool:
    return INSIGHT_1_HEADER.issubset(set(header)) and 'cAcc' not in header


def isCRMangledCSV(fileThing) -> bool:
    """
    Tests if `fileThing` is an Excel or Dropbox DOS file with lines terminated
    in CRCRLF.  These occur when someone opens the file with Excel or some other
    tool in a Windows system and saves the file back to the file system,
    mangling the original format.

    Arguments
    ---------
        fileThing
    A string or `pathlib.Path` object associated with what looks like a FlySight
    CR mangled file.

    Returns
    -------
    `True` if the file has one or more lines ending in CRCRLF within the first
    512 bytes of data.
    """
    with open (fileThing, 'rb') as file:
        rawData = file.read()
        return b'\r\r\n' in rawData


def fixCRMangledCSV(fileThing):
    """
    Open the file associated with `fileThing` and repleace all`\r\r\b` with
    `\r\n` EOL markers.

    Arguments
    ---------
        fileThing
    A string or `pathlib.Path` object associated with what looks like a FlySight
    CR mangled file.

    See
    ---
    `ssscoring.flysight.isCRMangledCSV`
    """
    with open(fileThing, 'rb') as inputFile:
        fileContents = inputFile.read()
    fileContents = fileContents.replace(b'\r\r\n', b'\r\n')
    with tempfile.NamedTemporaryFile(delete = False) as outputFile:
        outputFile.write(fileContents)
        tempFileName = outputFile.name
    shutil.copy(tempFileName, fileThing)
    os.unlink(tempFileName)


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


def validFlySightHeaderIn(fileThingCSV) -> bool:
    """
    Checks if a file is a CSV in FlySight 1 or FlySight 2 formats.  The checks
    include:

    - Whether the file is a CSV, using a comma delimiter
    - Checks for the presence of all the documented FlySight 1 headers
    - Checks for the presence of the FlySight 2 line 1 identifier

    Arguments
    ---------
        fileThingCSV
    A file thing to verify as a valid FlySight file; can be a string, an
    instance of `libpath.Path`, or a buffer of `bytes`.

    Returns
    -------
    `True` if `fileThingCSV` is a FlySight CSV file, otherwise `False`.
    """
    delimiters = [',']

    if isinstance(fileThingCSV, bytes):
        stream = StringIO(fileThingCSV.decode(FLYSIGHT_FILE_ENCODING))
    else:
        stream = open(fileThingCSV, 'r')

    with stream:
        try:
            dialect = csv.Sniffer().sniff(stream.readline(), delimiters=delimiters)
        except csv.Error:
            return False

        if dialect.delimiter not in delimiters:
            return False
        stream.seek(0)
        try:
            header = next(csv.reader(stream))
        except StopIteration:
            return False
    return header[0] == '$FLYS' or FLYSIGHT_1_HEADER.issubset(header) or _isInsightHeader(header)


def getAllSpeedJumpFilesFrom(dataLake: Path) -> dict:
    """
    Get a list of all the speed jump files from a data lake, where data lake is
    defined as a reachable path that contains one or more FlySight CSV files.
    This function tests each file to ensure that it's a speed skydive FlySight
    file in a valid format and length.  It doesn't validate data like versions
    prior to 1.9.0.

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
    jumpFiles = OrderedDict()
    for root, dirs, files in os.walk(dataLake):
        if any(name in root for name in IGNORE_LIST):
            continue
        for fileName in files:
            data = None
            if '.swp' in fileName: # Ignore Vim, other editors swap file
                continue
            if '.CSV' in fileName.upper():
                version = '1'
                jumpFileName = Path(root) / fileName
                stat = os.stat(jumpFileName)
                if all(x not in fileName for x in ('EVENT', 'SENSOR', 'TRACK')):
                    # FlySight 1 or Insight track format
                    data = pd.read_csv(jumpFileName, skiprows = (1, 1), index_col = False)
                    if data is not None and 'headAcc' in data.columns:
                        version = 'i'
                elif 'TRACK' in fileName:
                    # FlySight 2 track custom format
                    data = pd.read_csv(jumpFileName, names = FLYSIGHT_2_HEADER, skiprows = 6, index_col = False, na_values = ['NA', ])
                    data = skipOverFS2MetadataRowsIn(data)
                    data.drop('GNSS', inplace = True, axis = 1)
                    version = '2'
                if data is not None and stat.st_size >= MIN_JUMP_FILE_SIZE and validFlySightHeaderIn(jumpFileName):
                    # explicit because `not data` is ambiguous for dataframes
                    jumpFiles[jumpFileName] = version
    jumpFiles = OrderedDict(sorted(jumpFiles.items()))
    return jumpFiles


def detectFlySightFileVersionOf(fileThing) -> FlySightVersion:
    """
    Detects the FlySight file version based on its file name and format.

    Arguments
    ---------
        fileThing
    A string, `bytes` buffer or `pathlib.Path` object corresponding to track
    file.  If string or `pathlib.Path`, it'll be treated as a file.

    Returns
    -------
    An instance of `ssscoring.flysight.FlySightVersion` with a valid version
    symbolic value.

    Errors
    ------
    `ssscoring.errors.SSScoringError` if the file is not a CSV and it's some
    other invalid format.
    """
    match fileThing:
        case Path():
            fileName = fileThing.as_posix()
        case str():
            fileName = fileThing
            fileThing = Path(fileThing)
        case bytes():
            fileName = '00-00-00.CSV'
        case _:
            raise SSScoringError('fileThing must be a Path, str, or bytes')

    delimiters =  [',', ]
    stream = None
    if not '.CSV' in fileName.upper():
        raise SSScoringError('Invalid file extension type')
    if any(x in fileName for x in ('EVENT.CSV', 'SENSOR.CSV')):
        raise SSScoringError('Only TRACK.CSV v2 files can be processed at this time')
    if isinstance(fileThing, Path) or isinstance(fileThing, str):
        if not fileThing.is_file():
            raise SSScoringError('%s - file not found in data lake' % fileName)
        if not validFlySightHeaderIn(fileName):
            raise SSScoringError('CSV is not a valid FlySight file')
        stream = open(fileName, 'r')
    elif isinstance(fileThing, bytes):
        stream = StringIO(fileThing.decode(FLYSIGHT_FILE_ENCODING))

    try:
        dialect = csv.Sniffer().sniff(stream.readline(), delimiters = delimiters)
    except:
        raise SSScoringError('Error while trying to validate %s file format' % fileName)
    if dialect.delimiter in delimiters:
        stream.seek(0)
        header = next(csv.reader(stream))
    else:
        raise SSScoringError('CSV uses a different delimiter from FlySigh')
    if header[0] == '$FLYS':
        return FlySightVersion.V2
    elif FLYSIGHT_1_HEADER.issubset(header):
        return FlySightVersion.V1
    elif _isInsightHeader(header):
        return FlySightVersion.INSIGHT
    else:
        raise SSScoringError('%s file is not a FlySight v1 or v2 file')


def readVersion1CSV(fileThing: object) -> pd.DataFrame:
    """
    Read a FlySight file version 1 into a dataframe.  It scrubes blank rows that
    get in the way of correct parsing.

    Arguments
    ---------
        fileThing
    A string or a `pathlib.Path` object.  It can be a relative or an absolute
    path.

    Returns
    -------
    A FlySight dataframe with the original column names, normalized for
    manipulation as a dataframe instead of a file or CSV object.
    """
    return pd.read_csv(fileThing, skiprows = (1, 1), index_col = False)


def _tagVersion1From(fileThing: str) -> str:
    return fileThing.replace('.CSV', '').replace('.csv', '').replace('/data', '').replace('/', ' ').strip()+':v1'


def _tagFromFirstTimestampIn(rawData: pd.DataFrame, suffix: str) -> str:
    firstTimestamp = str(rawData.iloc[0]['time'])
    return firstTimestamp.split('T')[1].split('.')[0].replace(':', '-')+':'+suffix


def _tagVersion2From(rawData: pd.DataFrame) -> str:
    return _tagFromFirstTimestampIn(rawData, 'v2')


def _tagInsightFrom(rawData: pd.DataFrame) -> str:
    return _tagFromFirstTimestampIn(rawData, 'i')


def readInsightCSV(fileThing: object) -> pd.DataFrame:
    rawData = pd.read_csv(fileThing, skiprows=(1, 1), index_col=False)
    rawData.drop('headAcc', inplace=True, axis=1)
    return rawData


def readVersion2CSV(jumpFile: str) -> pd.DataFrame:
    """
    Read a FlySight file version 2 into a dataframe.  It scrubes blank rows that
    get in the way of correct parsing and drops the `GNSS` column because it
    just makes dataframe management murkier.

    Arguments
    ---------
        fileThing
    A string or a `pathlib.Path` object.  It can be a relative or an absolute
    path.

    Returns
    -------
    A FlySight dataframe with the original column names, normalized for
    manipulation as a dataframe instead of a file or CSV object.
    """

    rawData = pd.read_csv(jumpFile, names = FLYSIGHT_2_HEADER, skiprows = 6, index_col = False, na_values=['NA',])
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
    An arbitrary name for the buffer of type `str`.  Used to construct the tag
    for FlySight 1 buffers; ignored for FlySight 2 and Insight buffers, whose
    tags are derived from the first row's timestamp.

    Returns
    -------
    A `tuple` with two items:
        - `rawData` - a dataframe representation of the CSV with the original
          headers but without the data type header
        - `tag` - an identifying string for the track.  Shape depends on the
          device:
            - FlySight 1: `<bufferName>:v1` - derived from `bufferName`
            - FlySight 2: `HH-MM-ss:v2` - derived from the first GNSS row's
              timestamp
            - Insight: `HH-MM-ss:i` - derived from the first row's timestamp
          Invalid files produce `<bufferName>:INVALID`.

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
    try:
        version = detectFlySightFileVersionOf(buffer)
    except Exception:
        tag = '%s:INVALID' % bufferName
        rawData = None
    else:
        if version == FlySightVersion.V1:
            rawData = readVersion1CSV(stringIO)
            tag = _tagVersion1From(bufferName)
        elif version == FlySightVersion.V2:
            rawData = readVersion2CSV(stringIO)
            tag = _tagVersion2From(rawData)
        elif version == FlySightVersion.INSIGHT:
            rawData = readInsightCSV(stringIO)
            tag = _tagInsightFrom(rawData)
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
        - `tag` - an identifying string for the track.  Shape depends on the
          device:
            - FlySight 1: `<path slug>:v1` - derived from the file path
            - FlySight 2: `HH-MM-ss:v2` - derived from the first GNSS row's
              timestamp
            - Insight: `HH-MM-ss:i` - derived from the first row's timestamp
          `'NA'` if version detection fails.

    Raises
    ------
    `SSScoringError` if the CSV file is invalid in any way.
    """
    if isinstance(jumpFile, Path):
        jumpFile = jumpFile.as_posix()
    elif isinstance(jumpFile, str):
        pass
    else:
        raise SSScoringError('jumpFile must be a string or a Path object')
    if not validFlySightHeaderIn(jumpFile):
        raise SSScoringError('%s is an invalid speed skydiving file')
    try:
        version = detectFlySightFileVersionOf(jumpFile)
    except Exception:
        tag = 'NA'
        rawData = None
    else:
        if version == FlySightVersion.V1:
            rawData = readVersion1CSV(jumpFile)
            tag = _tagVersion1From(jumpFile)
        elif version == FlySightVersion.V2:
            rawData = readVersion2CSV(jumpFile)
            tag = _tagVersion2From(rawData)
        elif version == FlySightVersion.INSIGHT:
            rawData = readInsightCSV(jumpFile)
            tag = _tagInsightFrom(rawData)
    return (rawData, tag)

