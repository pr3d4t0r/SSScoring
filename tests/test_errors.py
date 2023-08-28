# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt


from ssscoring.errors import SSScoringError

import json


# *** tests ***

def test_SSScoringError():
    e = SSScoringError("error message", 42)

    error = str(e)
    error = json.loads(error)

    assert error['SSScoringError'] == "error message"
    assert error['errno'] == 42

