# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt


from pathlib import Path

from ssscoring.constants import BREAKOFF_ALTITUDE
from ssscoring.constants import FLYSIGHT_2_HEADER
from ssscoring.errors import SSScoringError
from ssscoring.flysight import FlySightVersion
from ssscoring.flysight import detectFlySightFileVersionOf
from ssscoring.flysight import getAllSpeedJumpFilesFrom
from ssscoring.flysight import skipOverFS2MetadataRowsIn
from ssscoring.flysight import validFlySightHeaderIn



import os
import pytest

import pandas as pd


# +++ constants ***

TEST_FLYSIGHT_DATA_LAKE = './resources/test-tracks'
TEST_FLYSIGHT_1_DATA = Path(TEST_FLYSIGHT_DATA_LAKE) / 'FS1' / 'test-data-00.CSV'
TEST_FLYSIGHT_2_DATA = Path(TEST_FLYSIGHT_DATA_LAKE) / 'FS2' / '01-00-00' / 'TRACK.CSV'


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
    yield fileName
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


def test_getAllSpeedJumpFilesFrom(_tooSmallCSV):
    files = getAllSpeedJumpFilesFrom(TEST_FLYSIGHT_DATA_LAKE)
    # Manual ./ because path.resolve(strict = False) resolves to the full path
    # vs implementation that uses os.walk() uses the relative path.
    testFiles = [ TEST_FLYSIGHT_1_DATA, TEST_FLYSIGHT_2_DATA ]
    assert len(files) >= 1
    assert set(testFiles).issubset(set(files.keys()))
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

