# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txtl

"""
## Experimental

Process a group of jumps uploaded from a file uploader.
"""

from ssscoring.appcommon import fetchResource
from ssscoring.appcommon import setSideBarDeprecated
from ssscoring.constants import SSSCORE_MOVED_DOMAIN_MD

import bokeh.plotting as bp
import streamlit as st


# +++ implementation +++

def _selectDZState(*args, **kwargs):
    if st.session_state.elevation:
        st.session_state.uploaderKey += 1
        st.session_state.trackFiles = None


def main():
    st.set_page_config(layout = 'wide')
    setSideBarDeprecated('🔢')
    st.write(fetchResource(SSSCORE_MOVED_DOMAIN_MD).read(), unsafe_allow_html=True)


if '__main__' == __name__:
    main()

