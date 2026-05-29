# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt


from io import StringIO
from pathlib import Path

from ssscoring.constants import BREAKOFF_ALTITUDE
from ssscoring.constants import FLYSIGHT_2_HEADER
from ssscoring.errors import SSScoringError
from ssscoring.flysight import FLYSIGHT_1_HEADER
from ssscoring.flysight import FLYSIGHT_FILE_ENCODING
from ssscoring.flysight import FlySightVersion
from ssscoring.flysight import detectFlySightFileVersionOf
from ssscoring.flysight import fixCRMangledCSV
from ssscoring.flysight import getAllSpeedJumpFilesFrom
from ssscoring.flysight import getFlySightDataFromCSVBuffer
from ssscoring.flysight import getFlySightDataFromCSVFileName
from ssscoring.flysight import isCRMangledCSV
from ssscoring.flysight import readVersion1CSV
from ssscoring.flysight import readVersion2CSV
from ssscoring.flysight import skipOverFS2MetadataRowsIn
from ssscoring.flysight import validFlySightHeaderIn

import os
import pytest
import tempfile

import pandas as pd


# +++ constants ***

TEST_FLYSIGHT_DATA_LAKE = './resources/test-tracks'
TEST_FLYSIGHT_1_DATA = Path(TEST_FLYSIGHT_DATA_LAKE) / 'FS1' / 'test-data-00.CSV'
TEST_FLYSIGHT_2_DATA = Path(TEST_FLYSIGHT_DATA_LAKE) / 'FS2' / '01-00-00' / 'TRACK.CSV'
TEST_FLYSIGHT_4_DATA = Path(TEST_FLYSIGHT_DATA_LAKE) / 'FS1' / 'test-data-04-DOS-CRLF.CSV'


# +++ tests +++


@pytest.fixture
def _badDelimitersCSV(tmp_path_factory):
    fileName = tmp_path_factory.mktemp('data')/'bogus.CSV'
    data = pd.read_csv(TEST_FLYSIGHT_1_DATA)
    data.to_csv(fileName, sep = '\t')
    yield fileName
    os.unlink(fileName.as_posix())


@pytest.fixture
def _missingColumnInCSV(tmp_path_factory):
    fileName = tmp_path_factory.mktemp('data')/'bogus.CSV'
    data = pd.read_csv(TEST_FLYSIGHT_1_DATA)
    data = data.drop('velD', axis = 1)
    data.to_csv(fileName, sep = ',')
    yield fileName.as_posix()
    os.unlink(fileName.as_posix())


@pytest.fixture
def _invalidMaxAltitude(tmp_path_factory):
    fileName = tmp_path_factory.mktemp('data')/'bogus.CSV'
    data = pd.read_csv(TEST_FLYSIGHT_1_DATA)
    data.hMSL = BREAKOFF_ALTITUDE-100.0
    data.to_csv(fileName, sep = ',')
    yield fileName.as_posix()
    os.unlink(fileName.as_posix())


@pytest.fixture
def _tooSmallCSV(tmp_path_factory):
    fileName = TEST_FLYSIGHT_2_DATA.as_posix().replace('TRACK', 'BOGUS')
    data = pd.read_csv(TEST_FLYSIGHT_2_DATA, names = FLYSIGHT_2_HEADER, skiprows = 6).head(50)
    data.to_csv(fileName, sep = ',')
    pathName = Path(fileName)
    yield pathName
    os.unlink(fileName)


def test_skipOverFS2MetadataRowsIn():
    data = pd.read_csv(TEST_FLYSIGHT_2_DATA, names = FLYSIGHT_2_HEADER, skiprows = 6).head(50)
    dataMod = skipOverFS2MetadataRowsIn(data)
    assert len(dataMod) < len(data)
    assert pd.isnull(data.iloc[0].time)
    assert pd.notnull(dataMod.iloc[0].time)


def test_validFlySightHeaderIn(_badDelimitersCSV, _missingColumnInCSV, _invalidMaxAltitude):
    assert validFlySightHeaderIn(TEST_FLYSIGHT_1_DATA)
    assert validFlySightHeaderIn(TEST_FLYSIGHT_2_DATA)
    assert not validFlySightHeaderIn(_badDelimitersCSV)
    assert not validFlySightHeaderIn(_missingColumnInCSV)
    assert validFlySightHeaderIn(_invalidMaxAltitude)
    with open(TEST_FLYSIGHT_1_DATA, 'rb') as inputFile:
        buffer = inputFile.read()
    assert validFlySightHeaderIn(buffer)


def test_getAllSpeedJumpFilesFrom(_tooSmallCSV):
    files = getAllSpeedJumpFilesFrom(TEST_FLYSIGHT_DATA_LAKE)
    assert len(files) >= 1
    assert TEST_FLYSIGHT_1_DATA in files.keys()
    assert TEST_FLYSIGHT_2_DATA in files.keys()
    assert files[TEST_FLYSIGHT_2_DATA] == '2'
    assert not any('SENSOR' in str(k) for k in files.keys())
    assert not any('EVENT' in str(k) for k in files.keys())
    assert not any('UBX' in str(k) for k in files.keys())
    assert not len(getAllSpeedJumpFilesFrom('./bogus'))


def test_detectFlySightFileVersionOf(_missingColumnInCSV):
    invalidFile = TEST_FLYSIGHT_2_DATA.as_posix().replace('TRACK', 'BAD_CSV_FILE')

    with pytest.raises(SSScoringError):
        detectFlySightFileVersionOf('bogus.dat')

    with pytest.raises(SSScoringError):
        detectFlySightFileVersionOf('EVENT.CSV')

    with pytest.raises(SSScoringError):
        detectFlySightFileVersionOf('bogus.CSV')

    with pytest.raises(SSScoringError):
        detectFlySightFileVersionOf(invalidFile)

    with pytest.raises(SSScoringError):
        detectFlySightFileVersionOf(_missingColumnInCSV)

    assert detectFlySightFileVersionOf(TEST_FLYSIGHT_1_DATA.as_posix()) == FlySightVersion.V1
    assert detectFlySightFileVersionOf(TEST_FLYSIGHT_2_DATA.as_posix()) == FlySightVersion.V2

    with open(TEST_FLYSIGHT_1_DATA, 'rb') as inputFile:
        buffer = inputFile.read()

    _ = detectFlySightFileVersionOf(buffer)


def test_isCRMangledCSV():
    assert isCRMangledCSV(TEST_FLYSIGHT_4_DATA)
    x = isCRMangledCSV(TEST_FLYSIGHT_1_DATA)
    assert not x


def test_fixCRMangledCSV():
    descriptor, tempFile = tempfile.mkstemp()
    with open(TEST_FLYSIGHT_4_DATA, 'rb') as inputFile:
        rawData = inputFile.read()
    with os.fdopen(descriptor, 'wb') as outputFile:
        outputFile.write(rawData)

    assert isCRMangledCSV(tempFile)
    fixCRMangledCSV(tempFile)
    assert not isCRMangledCSV(tempFile)
    os.unlink(tempFile)


def test_readVersion1CSV():
    rawData = readVersion1CSV(TEST_FLYSIGHT_1_DATA.as_posix())
    assert isinstance(rawData, pd.DataFrame)
    assert len(rawData) > 0
    assert FLYSIGHT_1_HEADER.issubset(set(rawData.columns))

    rawData = readVersion1CSV(TEST_FLYSIGHT_1_DATA)
    assert isinstance(rawData, pd.DataFrame)
    assert len(rawData) > 0

    with open(TEST_FLYSIGHT_1_DATA, 'rb') as inputFile:
        buffer = inputFile.read()
    rawData = readVersion1CSV(StringIO(buffer.decode(FLYSIGHT_FILE_ENCODING)))
    assert isinstance(rawData, pd.DataFrame)
    assert len(rawData) > 0


def test_readVersion2CSV():
    rawData = readVersion2CSV(TEST_FLYSIGHT_2_DATA.as_posix())
    assert isinstance(rawData, pd.DataFrame)
    assert len(rawData) > 0
    assert 'GNSS' not in rawData.columns
    assert pd.notnull(rawData.iloc[0].time)

    rawData = readVersion2CSV(TEST_FLYSIGHT_2_DATA)
    assert isinstance(rawData, pd.DataFrame)
    assert len(rawData) > 0
    assert 'GNSS' not in rawData.columns


def test_getFlySightDataFromCSVBuffer():
    with pytest.raises(SSScoringError):
        getFlySightDataFromCSVBuffer('not bytes', 'test')

    rawData, tag = getFlySightDataFromCSVBuffer(b'col1,col2\n1,2\n', 'bogus.CSV')
    assert rawData is None
    assert 'INVALID' in tag

    with open(TEST_FLYSIGHT_1_DATA, 'rb') as inputFile:
        buffer = inputFile.read()
    rawData, tag = getFlySightDataFromCSVBuffer(buffer, TEST_FLYSIGHT_1_DATA.name)
    assert isinstance(rawData, pd.DataFrame)
    assert tag.endswith(':v1')

    with open(TEST_FLYSIGHT_2_DATA, 'rb') as inputFile:
        buffer = inputFile.read()
    rawData, tag = getFlySightDataFromCSVBuffer(buffer, TEST_FLYSIGHT_2_DATA.name)
    assert isinstance(rawData, pd.DataFrame)
    assert tag.endswith(':v2')


def test_getFlySightDataFromCSVFileName(_missingColumnInCSV):
    with pytest.raises(SSScoringError):
        getFlySightDataFromCSVFileName(42)

    with pytest.raises(SSScoringError):
        getFlySightDataFromCSVFileName(_missingColumnInCSV)

    rawData, tag = getFlySightDataFromCSVFileName(TEST_FLYSIGHT_1_DATA.as_posix())
    assert isinstance(rawData, pd.DataFrame)
    assert tag.endswith(':v1')

    rawData, tag = getFlySightDataFromCSVFileName(TEST_FLYSIGHT_1_DATA)
    assert isinstance(rawData, pd.DataFrame)
    assert tag.endswith(':v1')

    rawData, tag = getFlySightDataFromCSVFileName(TEST_FLYSIGHT_2_DATA.as_posix())
    assert isinstance(rawData, pd.DataFrame)
    assert tag.endswith(':v2')

    rawData, tag = getFlySightDataFromCSVFileName(TEST_FLYSIGHT_2_DATA)
    assert isinstance(rawData, pd.DataFrame)
    assert tag.endswith(':v2')

