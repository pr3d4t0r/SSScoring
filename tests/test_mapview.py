# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt


from ssscoring.calc import convertFlySight2SSScoring
from ssscoring.calc import getFlySightDataFromCSVFileName
from ssscoring.calc import processJump
from ssscoring.mapview import DISTANCE_FROM_MIDDLE
from ssscoring.mapview import _resolveMaxScoreTimeFrom
from ssscoring.mapview import _resolveMaxSpeedTimeFrom
from ssscoring.mapview import speedJumpTrajectory
from ssscoring.mapview import viewPointBox

import haversine as hs
import pandas as pd
import pydeck as pdk


# *** constants ***

TEST_JUMP_DATA = convertFlySight2SSScoring(getFlySightDataFromCSVFileName('./resources/test-tracks/FS1/test-data-00.CSV')[0], altitudeDZMeters = 19.0)


# *** globals ***

_jumpResult = None


# +++ tests +++

def test_speedJumpTrajectory():
    global _jumpResult

    _jumpResult = processJump(TEST_JUMP_DATA)
    deck = speedJumpTrajectory(_jumpResult)
    assert isinstance(deck, pdk.Deck)


def test_viewPointBox():
    box = viewPointBox(TEST_JUMP_DATA)
    loc0 = (box.iloc[0].latitude, box.iloc[0].longitude)
    loc1 = (box.iloc[1].latitude, box.iloc[1].longitude)
    distance = round(hs.haversine(loc0, loc1, unit=hs.Unit.METERS), 0)
    assert isinstance(box, pd.DataFrame)
    assert distance == round(2.0*DISTANCE_FROM_MIDDLE)


def test__resolveMaxScoreTimeFrom():
    x = _resolveMaxScoreTimeFrom(_jumpResult)
    assert x == 22.0


def test__resolveMaxSpeedTimeFrom():
    x = _resolveMaxSpeedTimeFrom(_jumpResult)
    assert x == 23.9


# test_speedJumpTrajectory()
# test_viewPointBox()
# test__resolveMaxScoreTimeFrom()
# test__resolveMaxSpeedTimeFrom()

