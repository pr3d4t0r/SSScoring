# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt


from ssscoring import BREAKOFF_ALTITUDE
from ssscoring import convertFlySight2SSScoring
from ssscoring import dropNonSkydiveDataFrom
from ssscoring import getAllSpeedJumpFilesFrom
from ssscoring import getSpeedSkydiveFrom
from ssscoring import isValidJump
from ssscoring import jumpAnalysisTable
from ssscoring import validFlySightHeaderIn
from ssscoring.errors import SSScoringError

import os
import pytest

import pandas as pd


# +++ constants ***

TEST_FLYSIGHG_DATA_LAKE = './resources'
TEST_FLYSIGHT_DATA = os.path.join(TEST_FLYSIGHG_DATA_LAKE, 'test-data.csv')


# +++ globals +++

_data = None
_window = None


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
    assert not validFlySightHeaderIn(_invalidMaxAltitude)


def test_getAllSpeedJumpFilesFrom():
    assert len(getAllSpeedJumpFilesFrom(TEST_FLYSIGHG_DATA_LAKE)) >= 1
    assert not len(getAllSpeedJumpFilesFrom('./bogus'))


def test_convertFlySight2SSScoring():
    global _data

    rawData = pd.read_csv(TEST_FLYSIGHT_DATA, skiprows = (1,1))

    _data = convertFlySight2SSScoring(rawData)
    assert 'timeUnix' in _data.columns
    assert 'vKMh' in _data.columns

    with pytest.raises(SSScoringError):
        convertFlySight2SSScoring(None)

    with pytest.raises(SSScoringError):
        convertFlySight2SSScoring(TEST_FLYSIGHT_DATA)


def test_dropNonSkydiveDataFrom():
    global _data

    rowCount = len(_data)
    _data = dropNonSkydiveDataFrom(_data)
    assert len(_data) < rowCount


def test_getSpeedSkydiveFrom():
    global _data, _window

    _window, _data = getSpeedSkydiveFrom(_data)

    assert '{0:,.2f}'.format(_window.start) == '4,185.09'
    # assert '{0:,.2f}'.format(_window.start) == '4,194.12'
    # assert '{0:,.2f}'.format(_window.end) == '1,938.12'
    assert '{0:,.2f}'.format(_window.end) == '1,929.09'
    # assert '{0:,.2f}'.format(_window.validationStart) == '2,944.12'
    assert '{0:,.2f}'.format(_window.validationStart) == '2,935.09'
    assert _data.iloc[-1].heightMSL >= _window.end


def test_isValidJump():
    bogus = pd.DataFrame( { 'heightMSL': (2800, ), 'speedAccuracy': (42.0, ), } )
    assert isValidJump(_data, _window)
    assert not isValidJump(bogus, _window)


def test_jumpAnalysisTable():
    maxSpeed, table = jumpAnalysisTable(_data)

    assert maxSpeed > 400.0
    assert 'time' in table.columns
    assert 'vKMh' in table.columns
    assert 'altitude (ft)' in table.columns

