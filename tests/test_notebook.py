# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt


from ssscoring.calc import convertFlySight2SSScoring
from ssscoring.calc import getFlySightDataFromCSVFileName
from ssscoring.calc import processJump
from ssscoring.errors import SSScoringError
from ssscoring.notebook import convertHexColorToRGB
from ssscoring.notebook import graphForwardDisplacement
from ssscoring.notebook import graphGroundTrack
from ssscoring.notebook import graphJumpResult
from ssscoring.notebook import initializeGroundTrackPlot
from ssscoring.notebook import initializePlot
from ssscoring.notebook import validationWindowDataFrom

import pathlib

import pandas as pd
import plotly.graph_objects as go
import pytest


# +++ constants ***

TEST_FLYSIGHT_DATA_LAKE = './resources/test-tracks'
TEST_FLYSIGHT_DATA = pathlib.Path(TEST_FLYSIGHT_DATA_LAKE) / 'FS1' / 'test-data-00.csv'


# *** globals ***

_data = None
_jumpResult = None


# +++ tests +++

def test_initializePlot():
    initializePlot('bogus')

    with pytest.raises(Exception):
        initializePlot()


@pytest.mark.skip('Unable to validate in standalone modules, requires notebook')
def test_graphJumpResult():
    pass


# TODO: Fix this in the documentation ⬆️
# def test_validationWindowDataFrom():
#     global _data
#
#     rawData, tag = getFlySightDataFromCSVFileName(TEST_FLYSIGHT_DATA)
#     _data = convertFlySight2SSScoring(rawData, altitudeDZMeters=19.0)
#     jumpResult = processJump(_data)
#     windowData = validationWindowDataFrom(jumpResult.data, jumpResult.window)
#     assert isinstance(windowData, bm.ColumnDataSource)
#     assert len(windowData.data['x'])

def test_validationWindowDataFrom():
    global _data

    rawData, tag = getFlySightDataFromCSVFileName(TEST_FLYSIGHT_DATA)
    _data = convertFlySight2SSScoring(rawData, altitudeDZMeters=19.0)
    jumpResult = processJump(_data)
    windowData = validationWindowDataFrom(jumpResult.data, jumpResult.window)
    assert isinstance(windowData, pd.DataFrame)
    assert list(windowData.columns) == ['x', 'y']
    assert len(windowData) > 0


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


def _jumpResultFixture():
    global _jumpResult
    if _jumpResult is None:
        rawData, _ = getFlySightDataFromCSVFileName(TEST_FLYSIGHT_DATA)
        data = convertFlySight2SSScoring(rawData, altitudeDZMeters=19.0)
        _jumpResult = processJump(data)
    return _jumpResult


def test_initializeGroundTrackPlot():
    figure = initializeGroundTrackPlot('test jump')
    assert isinstance(figure, go.Figure)
    assert figure.layout.title.text == 'test jump'
    assert figure.layout.height == 450
    assert figure.layout.xaxis.title.text == 'forward (m)'
    assert figure.layout.yaxis.title.text == 'lateral (m)'
    assert figure.layout.yaxis.scaleanchor == 'x'
    assert figure.layout.yaxis.scaleratio == 1
    assert figure.layout.xaxis.zeroline is True
    assert figure.layout.yaxis.zeroline is True


def test_initializeGroundTrackPlot_customParams():
    figure = initializeGroundTrackPlot('custom', height=300, backgroundColorName='#000000', colorName='white')
    assert figure.layout.height == 300
    assert figure.layout.plot_bgcolor == '#000000'


def test_graphGroundTrack():
    jumpResult = _jumpResultFixture()
    figure = initializeGroundTrackPlot('test')
    graphGroundTrack(figure, jumpResult)
    assert len(figure.data) == 4
    names = [trace.name for trace in figure.data]
    assert 'fwd (m)' in names
    assert 'exit' in names
    assert 'end' in names


def test_graphGroundTrack_traceLengthsMatch():
    jumpResult = _jumpResultFixture()
    figure = initializeGroundTrackPlot('test')
    graphGroundTrack(figure, jumpResult)
    speedTrace = next(t for t in figure.data if t.name == 'fwd (m)')
    lineTrace = next(t for t in figure.data if t.name == 'track')
    assert len(speedTrace.x) == len(speedTrace.y)
    assert len(lineTrace.x) == len(speedTrace.x)


def test_graphGroundTrack_exitAndEndAreScalars():
    jumpResult = _jumpResultFixture()
    figure = initializeGroundTrackPlot('test')
    graphGroundTrack(figure, jumpResult)
    exitTrace = next(t for t in figure.data if t.name == 'exit')
    endTrace = next(t for t in figure.data if t.name == 'end')
    assert len(exitTrace.x) == 1
    assert len(endTrace.x) == 1


def test_graphGroundTrack_customColor():
    jumpResult = _jumpResultFixture()
    figure = initializeGroundTrackPlot('test')
    graphGroundTrack(figure, jumpResult, lineColor='orange')
    assert len(figure.data) == 4


def test_graphForwardDisplacement():
    jumpResult = _jumpResultFixture()
    figure = initializePlot('test', yLabel='forward (m)', backgroundColorName='#2c2c2c')
    graphForwardDisplacement(figure, jumpResult)
    assert len(figure.data) == 3
    displacementTrace = next(t for t in figure.data if t.name == 'fwd (m)')
    assert displacementTrace is not None
    assert len(displacementTrace.x) > 0


def test_graphForwardDisplacement_zeroReferenceBounds():
    jumpResult = _jumpResultFixture()
    figure = initializePlot('test', yLabel='forward (m)', backgroundColorName='#2c2c2c')
    graphForwardDisplacement(figure, jumpResult)
    zeroTrace = next(t for t in figure.data if len(t.x) == 2 and list(t.y) == [0.0, 0.0])
    assert list(zeroTrace.y) == [0.0, 0.0]
    assert len(zeroTrace.x) == 2


def test_graphForwardDisplacement_xAxisMatchesPlotTime():
    jumpResult = _jumpResultFixture()
    figure = initializePlot('test', yLabel='forward (m)', backgroundColorName='#2c2c2c')
    graphForwardDisplacement(figure, jumpResult)
    displacementTrace = next(t for t in figure.data if t.name == 'fwd (m)')
    assert float(displacementTrace.x[0]) == pytest.approx(float(jumpResult.data.plotTime.iloc[0]), abs=0.01)
    assert float(displacementTrace.x[-1]) == pytest.approx(float(jumpResult.data.plotTime.iloc[-1]), abs=0.01)

