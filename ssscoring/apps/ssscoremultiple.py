# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

"""
## Experimental

Process a group of jumps uploaded from a file uploader.
"""

from ssscoring import __VERSION__
from ssscoring.apps.common import displayJumpDataIn
from ssscoring.apps.common import initDropZonesFromObject
from ssscoring.apps.common import interpretJumpResult
from ssscoring.apps.common import isStreamlitHostedApp
from ssscoring.apps.common import plotJumpResult
from ssscoring.calc import aggregateResults
from ssscoring.calc import processAllJumpFiles
from ssscoring.calc import totalResultsFrom
from ssscoring.datatypes import JumpStatus
from ssscoring.notebook import SPEED_COLORS

import streamlit as st
import bokeh.models as bm


# +++ implementation +++

def _setSideBarAndMain():
    dropZones = initDropZonesFromObject()
    st.sidebar.title('🔢 SSScore %s α' % __VERSION__)
    st.session_state.processBadJump = st.sidebar.checkbox('Process bad jumps', value=True, help='Display results from invalid jumps')
    dropZone = st.sidebar.selectbox('Select drop zone:', dropZones.dropZone, index=None)
    if dropZone:
        st.session_state.elevation = dropZones[dropZones.dropZone == dropZone ].iloc[0].elevation
    else:
        st.session_state.elevation = None
        st.session_state.trackFiles = None
    st.sidebar.metric('Elevation', value='%.1f m' % (0.0 if st.session_state.elevation == None else st.session_state.elevation))
    st.session_state.trackFiles = st.sidebar.file_uploader(
        'Track files',
        [ 'CSV' ],
        disabled=st.session_state.elevation == None,
        accept_multiple_files=True
    )
    st.sidebar.html("<a href='https://github.com/pr3d4t0r/SSScoring/issues/new?template=Blank+issue' target='_blank'>Make a bug report or feature request</a>")


def main():
    if not isStreamlitHostedApp():
        st.set_page_config(layout = 'wide')
    _setSideBarAndMain()

    col0, col1 = st.columns([0.5, 0.5, ])
    if st.session_state.trackFiles:
        jumpResults = processAllJumpFiles(st.session_state.trackFiles, altitudeDZMeters=st.session_state.elevation)
        with col0:
            aggregate = aggregateResults(jumpResults)
            st.html('<h2>Jumps in this set</h2>')
            st.write(aggregate)
            st.html('<h2>Summary</h2>')
            st.dataframe(totalResultsFrom(aggregate), hide_index = True)
        with col1:
            for tag in sorted(list(jumpResults.keys())):
                jumpResult = jumpResults[tag]
                jumpStatusInfo,\
                scoringInfo,\
                badJumpLegend,\
                jumpStatus = interpretJumpResult(tag, jumpResult, st.session_state.processBadJump)
                st.html('<hr><h3>'+jumpStatusInfo+scoringInfo+(badJumpLegend if badJumpLegend else '')+'</h3>')
                if jumpStatus == JumpStatus.OK:
                    displayJumpDataIn(jumpResult.table)
                    plotJumpResult(tag, jumpResult)


if '__main__' == __name__:
    main()

