# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt


from ssscoring.constants import BREAKOFF_ALTITUDE
from ssscoring.flysight import _FS2_COLUMNS
from ssscoring.flysight import _skipOverFS2MetadataRowsIn
from ssscoring.flysight import getAllSpeedJumpFilesFrom
from ssscoring.flysight import validFlySightHeaderIn


import os
import pathlib
import pytest

import pandas as pd


# +++ constants ***

TEST_FLYSIGHT_DATA_LAKE = './resources'
TEST_FLYSIGHT_1_DATA = pathlib.Path(TEST_FLYSIGHT_DATA_LAKE, 'test-data-00.CSV')
TEST_FLYSIGHT_2_DATA = pathlib.Path(TEST_FLYSIGHT_DATA_LAKE) / 'test-data-FS2' / '01-00-00' / 'TRACK.CSV'


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
    data = pd.read_csv(TEST_FLYSIGHT_2_DATA, names = _FS2_COLUMNS, skiprows = 6).head(50)
    data.to_csv(fileName, sep = ',')
    yield fileName
    os.unlink(fileName)


def test__skipOverFS2MetadataRowsIn():
    data = pd.read_csv(TEST_FLYSIGHT_2_DATA, names = _FS2_COLUMNS, skiprows = 6).head(50)
    dataMod = _skipOverFS2MetadataRowsIn(data)
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
    testFiles = [ './'+TEST_FLYSIGHT_1_DATA.as_posix(), './'+TEST_FLYSIGHT_2_DATA.as_posix() ]
    assert len(files) >= 1
    assert set(testFiles).issubset(set(files))
    assert not len(getAllSpeedJumpFilesFrom('./bogus'))

