# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

"""
Functions and logic for detecting, validating and manipulating
FlySight 1 CSV files, including detection in the file system.  The functions in
this module assume that a data lake exists somewhere in the file system (whether
local or cloud-based).
"""


from ssscoring.calc import isValidMinimumAltitude
from ssscoring.constants import FLYSIGHT_1_HEADER
from ssscoring.constants import IGNORE_LIST
from ssscoring.constants import MIN_JUMP_FILE_SIZE

import csv
import os

import pandas as pd


# +++ functions +++

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

