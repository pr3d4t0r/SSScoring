# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

from streamlit.testing.v1 import AppTest

import pytest


# +++ tests +++

@pytest.mark.skip('Unable to validate in standalone modules, requires Streamlit')
def test_app():
    pass # bogus

