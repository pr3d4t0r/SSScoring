# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt


# TODO: Is this for comparing the results from more than one DZ?  Figure out
#       why it's here.
from ssscoring.constants import BREAKOFF_ALTITUDE
from ssscoring.constants import FT_IN_M
from ssscoring.errors import SSScoringError
from ssscoring.fs1 import aggregateResults
from ssscoring.fs1 import convertFlySight2SSScoring
from ssscoring.fs1 import dropNonSkydiveDataFrom
from ssscoring.fs1 import getAllSpeedJumpFilesFrom
from ssscoring.fs1 import getSpeedSkydiveFrom
from ssscoring.fs1 import isValidJump
from ssscoring.fs1 import isValidMinimumAltitude
from ssscoring.fs1 import jumpAnalysisTable
from ssscoring.fs1 import processAllJumpFiles
from ssscoring.fs1 import processJump
from ssscoring.fs1 import roundedAggregateResults
from ssscoring.fs1 import totalResultsFrom
from ssscoring.fs1 import validFlySightHeaderIn

import os
import pytest
import tempfile

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


def test_isValidMinimumAltitude(_invalidMaxAltitude):
    d = pd.read_csv(_invalidMaxAltitude, skiprows = (1, 1))
    assert not isValidMinimumAltitude(d.hMSL.max())
    d = pd.read_csv(TEST_FLYSIGHT_DATA, skiprows = (1, 1))
    assert isValidMinimumAltitude(d.hMSL.max())


def test_getAllSpeedJumpFilesFrom():
    assert len(getAllSpeedJumpFilesFrom(TEST_FLYSIGHG_DATA_LAKE)) >= 1
    assert not len(getAllSpeedJumpFilesFrom('./bogus'))


def test_convertFlySight2SSScoring():
    global _data

    altDZ = 42.0
    altDZFt = altDZ*FT_IN_M

    rawData = pd.read_csv(TEST_FLYSIGHT_DATA, skiprows = (1,1))

    with pytest.raises(SSScoringError):
        convertFlySight2SSScoring(None)

    with pytest.raises(SSScoringError):
        convertFlySight2SSScoring(TEST_FLYSIGHT_DATA)

    with pytest.raises(SSScoringError):
        convertFlySight2SSScoring(rawData, altDZ, altDZFt)

    _data = convertFlySight2SSScoring(rawData, altDZ)
    assert 'timeUnix' in _data.columns
    assert 'vKMh' in _data.columns
    assert 'altitudeASL' in _data.columns
    assert 'altitudeASLFt' in _data.columns
    assert 'hMetersPerSecond' in _data.columns
    assert 'hKMh' in _data.columns
    assert 'speedAngle' in _data.columns
    assert _data.altitudeASL.iloc[0] == rawData.hMSL.iloc[0]-altDZ
    assert _data.altitudeASLFt.iloc[0] == FT_IN_M*rawData.hMSL.iloc[0]-altDZFt


def test_dropNonSkydiveDataFrom():
    global _data

    rowCount = len(_data)
    _data = dropNonSkydiveDataFrom(_data)
    assert len(_data) < rowCount


def test_getSpeedSkydiveFrom():
    global _data, _window

    _window, _data = getSpeedSkydiveFrom(_data)

    assert '{0:,.2f}'.format(_window.start) == '4,149.65'
    assert '{0:,.2f}'.format(_window.end) == '1,893.65'
    assert '{0:,.2f}'.format(_window.validationStart) == '2,899.65'
    assert _data.iloc[-1].altitudeASL >= _window.end


def test_isValidJump():
    bogus = pd.DataFrame( { 'altitudeASL': (2800, ), 'speedAccuracy': (42.0, ), } )
    assert isValidJump(_data, _window)
    assert not isValidJump(bogus, _window)


def test_jumpAnalysisTable():
    maxSpeed, table = jumpAnalysisTable(_data)

    assert maxSpeed > 400.0
    assert 'time' in table.columns
    assert 'vKMh' in table.columns
    assert 'altitude (ft)' in table.columns
    assert 'speedAngle' in table.columns
    assert 'netVectorKMh' in table.columns


def test_processJump():
    data = convertFlySight2SSScoring(pd.read_csv(TEST_FLYSIGHT_DATA_XX, skiprows = (1,1)))

    jumpResults = processJump(data)

    assert '{0:,.2f}'.format(jumpResults.score) == '450.88'
    assert jumpResults.maxSpeed == 452.664
    assert 'valid' in jumpResults.result


def test_processAllJumpFiles():
    global _jumpResults
    jumpFiles = getAllSpeedJumpFilesFrom(TEST_FLYSIGHG_DATA_LAKE)
    _jumpResults = processAllJumpFiles(jumpFiles)
    assert _jumpResults
    assert 'test-data' in list(_jumpResults.keys())[0] # first item

    bogusDataLake = tempfile.mkdtemp()
    jumpFiles = getAllSpeedJumpFilesFrom(bogusDataLake)
    jumpResults = processAllJumpFiles(jumpFiles)
    assert not jumpResults


def test_aggregateResults():
    global _speeds

    _speeds = aggregateResults(_jumpResults)
    assert len(_speeds)
    assert _speeds.iloc[0].score
    assert 'maxSpeed' in _speeds.columns

    speeds = aggregateResults(dict())
    assert not len(speeds)


def test_roundedAggregateResults():
    global _speeds

    _speeds = roundedAggregateResults(_jumpResults)
    assert len(_speeds)
    assert _speeds.iloc[0].score
    assert 'maxSpeed' in _speeds.columns

    speeds = roundedAggregateResults(dict())
    assert not len(speeds)


def test_totalResultsFrom():
    totals = totalResultsFrom(_speeds)
    assert len(totals)
    assert totals.iloc[0].totalSpeed

    with pytest.raises(AttributeError):
        totalResultsFrom(pd.DataFrame())

    with pytest.raises(AttributeError):
        totalResultsFrom(None)

    bogus = pd.DataFrame({ 'a': [ 42, 69, ], 'b': [ 99, 41, ] })
    with pytest.raises(AttributeError):
        totalResultsFrom(bogus)


# test_convertFlySight2SSScoring()
# test_dropNonSkydiveDataFrom()
# test_getSpeedSkydiveFrom()
# test_jumpAnalysisTable()
# test_isValidMinimumAltitude(_invalidAltFileName)

# test_processJump()
# test_processAllJumpFiles()
# test_aggregateResults()
# test_roundedAggregateResults()

