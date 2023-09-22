# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt


from ssscoring.notebook import graphJumpResult
from ssscoring.notebook import initializePlot

import pytest
import pandas as pd


# +++ constants ***


# +++ tests +++

def test_initializePlot():
    initializePlot('bogus')

    with pytest.raises(Exception):
        initializePlot()


@pytest.mark.skip('Unable to validate in standalone modules, requires notebook')
def test_graphJumpResult():
    pass

