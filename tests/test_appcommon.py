# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt


from ssscoring.appcommon import DZ_DIRECTORY
from ssscoring.appcommon import STREAMLIT_SIG_KEY
from ssscoring.appcommon import STREAMLIT_SIG_VALUE
from ssscoring.appcommon import initDropZonesFromResource
from ssscoring.appcommon import initFileUploaderState
from ssscoring.appcommon import isStreamlitHostedApp
from ssscoring.errors import SSScoringError

import logging
import warnings
import os

import pandas as pd
import pytest


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
