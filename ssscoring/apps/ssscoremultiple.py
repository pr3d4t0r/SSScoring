# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

"""
## Experimental

Process a group of jumps uploaded from a file uploader.
"""

from ssscoring import __VERSION__
from ssscoring.apps.common import displayJumpDataIn
from ssscoring.apps.common import initDropZonesFromObject
from ssscoring.apps.common import isStreamlitHostedApp
from ssscoring.calc import aggregateResults
from ssscoring.calc import isValidMaximumAltitude
from ssscoring.calc import isValidMinimumAltitude
from ssscoring.calc import processAllJumpFiles
from ssscoring.calc import totalResultsFrom
from ssscoring.datatypes import JumpStatus

import pandas as pd
import streamlit as st


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

    col0, col1 = st.columns([0.4, 0.6, ])
    if st.session_state.trackFiles:
        with col0:
            jumpResults = processAllJumpFiles(st.session_state.trackFiles, altitudeDZMeters=st.session_state.elevation)
            aggregate = aggregateResults(jumpResults)
            st.html('<h2>All jumps in this set</h2>')
            st.write(aggregate)
            st.html('<h2>Jumps set summary</h2>')
            st.write(totalResultsFrom(aggregate))
            for tag in jumpResults.keys():
                jumpResult = jumpResults[tag]
                maxSpeed = jumpResult.maxSpeed
                window = jumpResult.window
                jumpStatus = jumpResult.status
                if jumpResult.status == JumpStatus.WARM_UP_FILE:
                    jumpStatusInfo = ''
                    badJumpLegend = '<span style="color: red">Warm up file - nothing to do<br>'
                    scoringInfo = ''
                else:
                    scoringInfo = 'Max speed = {0:,.0f}; '.format(maxSpeed)+('exit at %d m (%d ft)<br>End scoring window at %d m (%d ft)<br>'%(window.start, 3.2808*window.start, window.end, 3.2808*window.end))
                if jumpStatus == JumpStatus.OK:
                    jumpStatusInfo = '<span style="color: %s">%s jump - %s - %.02f km/h</span><br>' % ('green', tag, 'VALID', jumpResult.score)
                    belowMaxAltitude = isValidMaximumAltitude(jumpResult.data.altitudeAGL.max())
                    badJumpLegend = None
                    if not isValidMinimumAltitude(jumpResult.data.altitudeAGL.max()):
                        badJumpLegend = '<span style="color: yellow"><span style="font-weight: bold">Warning:</span> exit altitude AGL was lower than the minimum scoring altitude<br>'
                        jumpStatus = JumpStatus.ALTITUDE_EXCEEDS_MINIMUM
                    if not belowMaxAltitude:
                        jumpStatusInfo = '<span style="color: %s">%s jump - %s - %.02f km/h</span><br>' % ('red', tag, 'INVALID', jumpResult.score)
                        badJumpLegend = '<span style="color: red"><span style="font-weight: bold">RE-JUMP:</span> exit altitude AGL exceeds the maximum altitude<br>'
                        jumpStatus = JumpStatus.ALTITUDE_EXCEEDS_MAXIMUM
                elif jumpStatus == JumpStatus.SPEED_ACCURACY_EXCEEDS_LIMIT:
                    badJumpLegend = '<span style="color: red"><span style="font-weight: bold">RE-JUMP:</span> exit altitude AGL exceeds the maximum altitude<br>'
                jumpStatus = JumpStatus.OK if jumpStatus != JumpStatus.OK and st.session_state.processBadJump and jumpStatus != JumpStatus.WARM_UP_FILE else jumpStatus
                with col1:
                    st.html('<h3>'+jumpStatusInfo+scoringInfo+(badJumpLegend if badJumpLegend else '')+'</h3>')
                if jumpStatus == JumpStatus.OK:
                    with col1:
                        displayJumpDataIn(jumpResult.table)


if '__main__' == __name__:
    main()

