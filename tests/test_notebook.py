# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt


from ssscoring import convertFlySight2SSScoring
from ssscoring.notebook import processJump

import pandas as pd


# +++ constants ***

TEST_FLYSIGHT_DATA = './resources/test-data.csv'


# +++ tests +++

def test_processJump():
    data = convertFlySight2SSScoring(pd.read_csv(TEST_FLYSIGHT_DATA, skiprows = (1,1)))

    jumpResults = processJump(data)

    assert '{0:,.2f}'.format(jumpResults.score) == '443.07'
    assert jumpResults.maxSpeed == 448.524
    assert 'valid' in jumpResults.result

