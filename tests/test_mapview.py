# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt


from ssscoring.calc import convertFlySight2SSScoring
from ssscoring.calc import getFlySightDataFromCSVFileName
from ssscoring.calc import processJump
from ssscoring.mapview import DISTANCE_FROM_MIDDLE
from ssscoring.mapview import speedJumpTrajectory
from ssscoring.mapview import viewPointBox

import haversine as hs
import pandas as pd
import pydeck as pdk


TEST_JUMP_DATA = convertFlySight2SSScoring(getFlySightDataFromCSVFileName('./resources/test-tracks/FS1/test-data-00.CSV')[0], altitudeDZMeters = 19.0)


# +++ tests +++

def test_speedJumpTrajectory():
    jumpResult = processJump(TEST_JUMP_DATA)
    deck = speedJumpTrajectory(jumpResult)
    assert isinstance(deck, pdk.Deck)


def test_viewPointBox():
    box = viewPointBox(TEST_JUMP_DATA)
    loc0 = (box.iloc[0].latitude, box.iloc[0].longitude)
    loc1 = (box.iloc[1].latitude, box.iloc[1].longitude)
    distance = round(hs.haversine(loc0, loc1, unit=hs.Unit.METERS), 0)
    assert isinstance(box, pd.DataFrame)
    assert distance == round(2.0*DISTANCE_FROM_MIDDLE)


# test_speedJumpTrajectory()
# test_viewPointBox()

