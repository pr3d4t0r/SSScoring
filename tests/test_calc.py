# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

from ssscoring.calc import aggregateResults
from ssscoring.calc import calcScoreISC
from ssscoring.calc import calcScoreMeanVelocity
from ssscoring.calc import calculateDistance
from ssscoring.calc import convertFlySight2SSScoring
from ssscoring.calc import dropNonSkydiveDataFrom
from ssscoring.calc import getFlySightDataFromCSV
from ssscoring.calc import getSpeedSkydiveFrom
from ssscoring.calc import isValidJump
from ssscoring.calc import isValidMinimumAltitude
from ssscoring.calc import jumpAnalysisTable
from ssscoring.calc import processAllJumpFiles
from ssscoring.calc import processJump
from ssscoring.calc import roundedAggregateResults
from ssscoring.calc import totalResultsFrom
from ssscoring.constants import BREAKOFF_ALTITUDE
from ssscoring.constants import FT_IN_M
from ssscoring.errors import SSScoringError
from ssscoring.flysight import getAllSpeedJumpFilesFrom

import os
import pathlib
import pytest
import tempfile

import numpy as np
import pandas as pd


# +++ constants ***

TEST_FLYSIGHT_DATA_LAKE = './resources/test-tracks'
TEST_FLYSIGHT_DATA = pathlib.Path(TEST_FLYSIGHT_DATA_LAKE) / 'FS1' / 'test-data-00.csv'
TEST_FLYSIGHT_DATA_V1 = pathlib.Path(TEST_FLYSIGHT_DATA_LAKE) / 'FS1' / 'test-data-02.csv'
TEST_FLYSIGHT_DATA_BAD_HEADERS = pathlib.Path(TEST_FLYSIGHT_DATA_LAKE) / 'FS1' / 'test-data-03.csv'


# +++ globals +++

_data = None
_jumpResults = None
_window = None
_speeds = None


# +++ tests +++

@pytest.fixture
def _invalidMaxAltitude(tmp_path_factory):
    fileName = tmp_path_factory.mktemp('data')/'bogus.CSV'
    data = pd.read_csv(TEST_FLYSIGHT_DATA)
    data.hMSL = BREAKOFF_ALTITUDE-100.0
    data.to_csv(fileName, sep = ',')
    yield fileName.as_posix()
    os.unlink(fileName.as_posix())


def test_isValidMinimumAltitude(_invalidMaxAltitude):
    d = pd.read_csv(_invalidMaxAltitude, skiprows = (1, 1))
    assert not isValidMinimumAltitude(d.hMSL.max())
    d = pd.read_csv(TEST_FLYSIGHT_DATA, skiprows = (1, 1))
    assert isValidMinimumAltitude(d.hMSL.max())


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
    assert 'altitudeAGL' in _data.columns
    assert 'altitudeAGLFt' in _data.columns
    assert 'hMetersPerSecond' in _data.columns
    assert 'hKMh' in _data.columns
    assert 'speedAngle' in _data.columns
    assert _data.altitudeAGL.iloc[0] == rawData.hMSL.iloc[0]-altDZ
    assert _data.altitudeAGLFt.iloc[0] == FT_IN_M*rawData.hMSL.iloc[0]-altDZFt


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
    assert _data.iloc[-1].altitudeAGL >= _window.end


def test_isValidJump():
    bogus = pd.DataFrame( { 'altitudeAGL': (2800, ), 'speedAccuracy': (42.0, ), } )
    assert isValidJump(_data, _window)
    assert not isValidJump(bogus, _window)


def test_calculateDistance():
    start = (37.8329426, -121.64040112)
    end = (37.8285883, -121.6356015)

    result = '%3.4f' % calculateDistance(start, end)
    assert result == '641.9585'


def test_jumpAnalysisTable():
    maxSpeed, table = jumpAnalysisTable(_data)

    assert maxSpeed > 400.0
    assert 'time' in table.columns
    assert 'vKMh' in table.columns
    assert 'altitude (ft)' in table.columns
    assert 'speedAngle' in table.columns
    assert 'netVectorKMh' in table.columns


def test_calcScoreMeanVelocity():
    data = _data.copy()
    baseTime = data.iloc[0].timeUnix
    data['plotTime'] = np.round(data.timeUnix-baseTime, decimals = 2)

    score, scores = calcScoreMeanVelocity(data)
    assert score == 443.47
    assert score in scores
    assert len(scores) > 0
    assert type(scores) == dict


def test_calcScoreISC():
    data = _data.copy()
    baseTime = data.iloc[0].timeUnix
    data['plotTime'] = np.round(data.timeUnix-baseTime, decimals = 2)

    score, scores = calcScoreISC(data)
    assert score == 444.61
    assert score in scores
    assert len(scores) > 0
    assert type(scores) == dict


def test_processJump():
    data = convertFlySight2SSScoring(pd.read_csv(TEST_FLYSIGHT_DATA_V1, skiprows = (1,1)))

    jumpResults = processJump(data)

    assert '{0:,.2f}'.format(jumpResults.score) == '451.86'
    assert jumpResults.maxSpeed == 452.664
    assert 'valid' in jumpResults.result


def test_getFlySightDataFromCSV():
    rawData = None
    tag = None
    rawData, tag = getFlySightDataFromCSV(TEST_FLYSIGHT_DATA)
    assert isinstance(rawData, pd.DataFrame)
    assert 'v1' in tag
    with pytest.raises(SSScoringError):
        rawData, tag = getFlySightDataFromCSV(TEST_FLYSIGHT_DATA_BAD_HEADERS)


def test_processAllJumpFiles():
    global _jumpResults
    jumpFiles = getAllSpeedJumpFilesFrom(TEST_FLYSIGHT_DATA_LAKE)
    _jumpResults = processAllJumpFiles(jumpFiles)
    assert _jumpResults
    assert '01-00-00:v2' in list(_jumpResults.keys())

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

    _speeds = roundedAggregateResults(aggregateResults(_jumpResults))
    assert len(_speeds)
    assert _speeds.iloc[0].score
    assert 'maxSpeed' in _speeds.columns

    speeds = roundedAggregateResults(pd.DataFrame())
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


# For symbolic debugger:

# test_convertFlySight2SSScoring()
# test_dropNonSkydiveDataFrom()
# test_getSpeedSkydiveFrom()
# test_jumpAnalysisTable()
# test_isValidMinimumAltitude(_invalidAltFileName)
# test_calcScoreMeanVelocity()
# test_calcScoreISC()

# test_getFlySightDataFromCSV()
# test_processJump()
# test_processAllJumpFiles()
# test_aggregateResults()
# test_roundedAggregateResults()

