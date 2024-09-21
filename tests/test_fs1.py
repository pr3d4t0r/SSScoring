# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt


from ssscoring.constants import BREAKOFF_ALTITUDE
from ssscoring.fs1 import getAllSpeedJumpFilesFrom
from ssscoring.fs1 import validFlySightHeaderIn

import os
import pytest

import pandas as pd


# +++ constants ***

TEST_FLYSIGHG_DATA_LAKE = './resources'
TEST_FLYSIGHT_DATA = os.path.join(TEST_FLYSIGHG_DATA_LAKE, 'test-data-00.csv')
TEST_FLYSIGHT_DATA_XX = os.path.join(TEST_FLYSIGHG_DATA_LAKE, 'test-data-02.csv')


# +++ globals +++

_data = None
_jumpResults = None
_window = None
_speeds = None


# +++ tests +++

@pytest.fixture
def _badDelimitersCSV(tmp_path_factory):
    fileName = tmp_path_factory.mktemp('data')/'bogus.CSV'
    data = pd.read_csv(TEST_FLYSIGHT_DATA)
    data.to_csv(fileName, sep = '\t')
    yield fileName
    os.unlink(fileName.as_posix())


@pytest.fixture
def _missingColumnInCSV(tmp_path_factory):
    fileName = tmp_path_factory.mktemp('data')/'bogus.CSV'
    data = pd.read_csv(TEST_FLYSIGHT_DATA)
    data = data.drop('velD', axis = 1)
    data.to_csv(fileName, sep = ',')
    yield fileName.as_posix()
    os.unlink(fileName.as_posix())


@pytest.fixture
def _invalidMaxAltitude(tmp_path_factory):
    fileName = tmp_path_factory.mktemp('data')/'bogus.CSV'
    data = pd.read_csv(TEST_FLYSIGHT_DATA)
    data.hMSL = BREAKOFF_ALTITUDE-100.0
    data.to_csv(fileName, sep = ',')
    yield fileName.as_posix()
    os.unlink(fileName.as_posix())


def test_validFlySightHeaderIn(_badDelimitersCSV, _missingColumnInCSV, _invalidMaxAltitude):
    assert validFlySightHeaderIn(TEST_FLYSIGHT_DATA)
    assert not validFlySightHeaderIn(_badDelimitersCSV)
    assert not validFlySightHeaderIn(_missingColumnInCSV)
    assert validFlySightHeaderIn(_invalidMaxAltitude)


def test_getAllSpeedJumpFilesFrom():
    assert len(getAllSpeedJumpFilesFrom(TEST_FLYSIGHG_DATA_LAKE)) >= 1
    assert not len(getAllSpeedJumpFilesFrom('./bogus'))


# test_convertFlySight2SSScoring()
# test_dropNonSkydiveDataFrom()
# test_getSpeedSkydiveFrom()
# test_jumpAnalysisTable()
# test_isValidMinimumAltitude(_invalidAltFileName)

# test_processJump()
# test_processAllJumpFiles()
# test_aggregateResults()
# test_roundedAggregateResults()

