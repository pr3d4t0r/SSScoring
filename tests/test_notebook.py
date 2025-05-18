# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt


from ssscoring.calc import convertFlySight2SSScoring
from ssscoring.calc import getFlySightDataFromCSVFileName
from ssscoring.calc import processJump
from ssscoring.errors import SSScoringError
from ssscoring.notebook import convertHexColorToRGB
from ssscoring.notebook import graphJumpResult
from ssscoring.notebook import initializePlot
from ssscoring.notebook import validationWindowDataFrom

import pathlib

import bokeh.models as bm
import pytest


# +++ constants ***

TEST_FLYSIGHT_DATA_LAKE = './resources/test-tracks'
TEST_FLYSIGHT_DATA = pathlib.Path(TEST_FLYSIGHT_DATA_LAKE) / 'FS1' / 'test-data-00.csv'


# *** globals ***

_data = None


# +++ tests +++

def test_initializePlot():
    initializePlot('bogus')

    with pytest.raises(Exception):
        initializePlot()


@pytest.mark.skip('Unable to validate in standalone modules, requires notebook')
def test_graphJumpResult():
    pass


def test_validationWindowDataFrom():
    global _data

    rawData, tag = getFlySightDataFromCSVFileName(TEST_FLYSIGHT_DATA)
    _data = convertFlySight2SSScoring(rawData, altitudeDZMeters=19.0)
    jumpResult = processJump(_data)
    windowData = validationWindowDataFrom(jumpResult.data, jumpResult.window)
    assert isinstance(windowData, bm.ColumnDataSource)
    assert len(windowData.data['x'])


def test_convertHexColorToRGB():
    color = '#1041f0'
    v = convertHexColorToRGB(color)
    assert v == [ 16, 65, 240, ]

    with pytest.raises(SSScoringError):
        convertHexColorToRGB('1234568')

    with pytest.raises(ValueError):
        convertHexColorToRGB('#1041g0')

    with pytest.raises(TypeError):
        convertHexColorToRGB(42)


# test_validationWindowDataFrom()
# test_convertHexColorToRGB()

