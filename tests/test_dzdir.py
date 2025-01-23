# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt


from ssscoring.dzdir import DROP_ZONES_LIST

import pandas as pd


def test_DROP_ZONES_LIST():
    dropZones = pd.DataFrame(DROP_ZONES_LIST)
    assert len(dropZones) > 1

    assert len(dropZones[dropZones.dropZone == 'Bay Area Skydiving'])
    assert not len(dropZones[dropZones.dropZone == 'Bogus Dingus Skydiving'])

