# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

from enum import Enum

from ssscoring.calc import processJump
from ssscoring.datatypes import FlySightVersion
from ssscoring.datatypes import JumpResults
from ssscoring.datatypes import JumpStatus
from ssscoring.datatypes import PerformanceWindow
from ssscoring.calc import convertFlySight2SSScoring

import pathlib
import warnings

import pandas as pd
import pytest


# +++ constants +++

TEST_FLYSIGHT_DATA_LAKE = './resources/test-tracks'
TEST_FLYSIGHT_DATA_V1 = pathlib.Path(TEST_FLYSIGHT_DATA_LAKE) / 'FS1' / 'test-data-02.csv'


# +++ tests +++

@pytest.fixture
def _validJump() -> pd.DataFrame:
    warnings.filterwarnings('ignore', category=UserWarning)
    data = convertFlySight2SSScoring(pd.read_csv(TEST_FLYSIGHT_DATA_V1, skiprows=(1, 1)))
    jumpResults = processJump(data)
    return jumpResults


def test_FlySightVersion():
    version = FlySightVersion.V1

    assert isinstance(version, Enum)
    assert isinstance(version, FlySightVersion)
    version == FlySightVersion.V1

    version = FlySightVersion.V2
    assert version == FlySightVersion.V2


def test_JumpStatus():
    status = JumpStatus.OK
    assert isinstance(status, JumpStatus)
    assert status == JumpStatus.OK

    status = JumpStatus.SPEED_ACCURACY_EXCEEDS_LIMIT
    assert status == JumpStatus.SPEED_ACCURACY_EXCEEDS_LIMIT

    status = JumpStatus.WARM_UP_FILE
    assert status == JumpStatus.WARM_UP_FILE


def test_JumpResults(_validJump):
    assert isinstance(_validJump, JumpResults)
    assert isinstance(_validJump.data, pd.DataFrame)
    assert isinstance(_validJump.maxSpeed, float)
    assert isinstance(_validJump.score, float)
    assert isinstance(_validJump.scores, dict)
    assert isinstance(_validJump.table, pd.DataFrame)
    assert isinstance(_validJump.window, PerformanceWindow)
    assert isinstance(_validJump.status, JumpStatus)


def test_PerformanceWindow(_validJump):
    window = _validJump.window
    assert isinstance(window, PerformanceWindow)
    assert isinstance(window.start, float)
    assert isinstance(window.end, float)
    assert isinstance(window.validationStart, float)

