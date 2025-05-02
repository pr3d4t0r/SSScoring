# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt


# from ssscoring.appcommon import initFileUploaderState
from ssscoring.appcommon import DZ_DIRECTORY
from ssscoring.appcommon import STREAMLIT_SIG_KEY
from ssscoring.appcommon import STREAMLIT_SIG_VALUE
from ssscoring.appcommon import initDropZonesFromResource
from ssscoring.appcommon import interpretJumpResult
from ssscoring.appcommon import isStreamlitHostedApp
from ssscoring.calc import convertFlySight2SSScoring
from ssscoring.calc import processJump
from ssscoring.datatypes import JumpStatus
from ssscoring.errors import SSScoringError

import warnings
import os
import pathlib

import pandas as pd
import pytest


# +++ constants +++

TEST_FLYSIGHT_DATA_LAKE = './resources/test-tracks'
TEST_FLYSIGHT_DATA = pathlib.Path(TEST_FLYSIGHT_DATA_LAKE) / 'FS1' / 'test-data-00.csv'
TEST_FLYSIGHT_DATA_V1_EXCEEDS_ISC_THRESHOLD = pathlib.Path(TEST_FLYSIGHT_DATA_LAKE) / 'FS1' / 'test-data-07-BAD-ISC.CSV'
TEST_FLYSIGHT_DATA_V1_WARM_UP = pathlib.Path(TEST_FLYSIGHT_DATA_LAKE) / 'FS1' / 'test-data-05-warm-up.csv'


# *** tests ***

warnings.filterwarnings('ignore')


def test_isStreamlitHostedApp():
    assert not isStreamlitHostedApp()

    os.environ[STREAMLIT_SIG_KEY] = STREAMLIT_SIG_VALUE
    assert isStreamlitHostedApp()

    del os.environ[STREAMLIT_SIG_KEY]


def test_initDropZonesFromResource():
    d = initDropZonesFromResource(DZ_DIRECTORY)
    assert isinstance(d, pd.DataFrame)
    assert 'dropZone' in d.columns
    with pytest.raises(SSScoringError):
        initDropZonesFromResource('bogus.CSV')


def test_initFileUploaderState():
    pass


def test_interpretJumpResult():
    rawData = pd.read_csv(TEST_FLYSIGHT_DATA, skiprows = (1,1))
    jumpResult = processJump(convertFlySight2SSScoring(rawData, altitudeDZMeters = 42.0))
    jumpStatusInfo,\
    scoringInfo,\
    badJumpLegend,\
    jumpStatus = interpretJumpResult('test1', jumpResult, False)
    assert jumpResult.status == JumpStatus.OK

    rawData = pd.read_csv(TEST_FLYSIGHT_DATA_V1_WARM_UP, skiprows = (1,1))
    jumpResult = processJump(convertFlySight2SSScoring(rawData, altitudeDZMeters = 42.0))
    jumpStatusInfo,\
    scoringInfo,\
    badJumpLegend,\
    jumpStatus = interpretJumpResult('test1', jumpResult, False)
    assert jumpResult.status == JumpStatus.WARM_UP_FILE
    jumpResult = processJump(convertFlySight2SSScoring(rawData, altitudeDZMeters = 42.0))
    jumpStatusInfo,\
    scoringInfo,\
    badJumpLegend,\
    jumpStatus = interpretJumpResult('test1', jumpResult, True)
    assert jumpResult.status == JumpStatus.WARM_UP_FILE

    # TODO:  Get a file that's guaranteed to have ISC max elevation errors!
#     rawData = pd.read_csv(TEST_FLYSIGHT_DATA_V1_EXCEEDS_ISC_THRESHOLD, skiprows = (1,1))
#     jumpResult = processJump(convertFlySight2SSScoring(rawData, altitudeDZMeters = 3.0))
#     jumpStatusInfo,\
#     scoringInfo,\
#     badJumpLegend,\
#     jumpStatus = interpretJumpResult('test1', jumpResult, False)
#     assert jumpResult.status == JumpStatus.SPEED_ACCURACY_EXCEEDS_LIMIT


# test_interpretJumpResult()

