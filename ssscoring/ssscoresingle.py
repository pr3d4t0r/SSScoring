# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

"""
Streamlit-based application.

Issue deploying to Streamlit.io:
https://discuss.streamlit.io/t/pythonpath-issue-modulenotfounderror-in-same-package-where-app-is-defined/91170
"""

from ssscoring import __VERSION__
from ssscoring.appcommon import DZ_DIRECTORY
from ssscoring.appcommon import displayJumpDataIn
from ssscoring.appcommon import initDropZonesFromResource
from ssscoring.appcommon import initFileUploaderState
from ssscoring.appcommon import interpretJumpResult
from ssscoring.appcommon import isStreamlitHostedApp
from ssscoring.appcommon import plotJumpResult
from ssscoring.calc import convertFlySight2SSScoring
from ssscoring.calc import getFlySightDataFromCSVBuffer
from ssscoring.calc import processJump
from ssscoring.datatypes import JumpStatus
from ssscoring.mapview import speedJumpTrajectory

import pandas as pd
import streamlit as st


# *** implementation ***

def _selectDZState(*args, **kwargs):
    if st.session_state.elevation:
        st.session_state.uploaderKey += 1
        st.session_state.trackFile = None


def _setSideBarAndMain():
    dropZones = initDropZonesFromResource(DZ_DIRECTORY)
    st.sidebar.title('1️⃣  SSScore %s β' % __VERSION__)
    st.session_state.processBadJump = st.sidebar.checkbox('Process bad jump', value=True, help='Display results from invalid jumps')
    dropZone = st.sidebar.selectbox('Select drop zone:', dropZones.dropZone, index=None, on_change=_selectDZState)
    if dropZone:
        st.session_state.elevation = dropZones[dropZones.dropZone == dropZone ].iloc[0].elevation
    else:
        st.session_state.elevation = None
        st.session_state.trackFile = None
    st.sidebar.metric('Elevation', value='%.1f m' % (0.0 if st.session_state.elevation == None else st.session_state.elevation))
    trackFile = st.sidebar.file_uploader('Track file', [ 'CSV' ], disabled=st.session_state.elevation == None, key = st.session_state.uploaderKey)
    if trackFile:
        st.session_state.trackFile = trackFile
    st.sidebar.button('Clear', on_click=_selectDZState)
    st.sidebar.html("<a href='https://github.com/pr3d4t0r/SSScoring/issues/new?template=Blank+issue' target='_blank'>Make a bug report or feature request</a>")


def _getJumpDataFrom(trackFileBuffer: str) -> pd.DataFrame:
    dropZoneAltMSLMeters = 0.0 if st.session_state.elevation == None else st.session_state.elevation
    data = None
    tag = None
    if dropZoneAltMSLMeters is not None:
        rawData, tag = getFlySightDataFromCSVBuffer(trackFileBuffer, st.session_state.trackFile.name)
        data = convertFlySight2SSScoring(rawData, altitudeDZMeters=dropZoneAltMSLMeters)
    return data, tag


def main():
    if not isStreamlitHostedApp():
        st.set_page_config(layout = 'wide')
    initFileUploaderState('trackFile')
    _setSideBarAndMain()

    col0, col1 = st.columns([ 0.4, 0.6, ])
    if st.session_state.trackFile:
        data, tag = _getJumpDataFrom(st.session_state.trackFile.getvalue())
        jumpResult = processJump(data)
        jumpStatusInfo, \
        scoringInfo, \
        badJumpLegend, \
        jumpStatus = interpretJumpResult(tag, jumpResult, st.session_state.processBadJump)
        with col0:
            st.html('<h3>'+jumpStatusInfo+scoringInfo+(badJumpLegend if badJumpLegend else '')+'</h3>')
        if jumpStatus == JumpStatus.OK:
            with col0:
                displayJumpDataIn(jumpResult.table)
            with col1:
                plotJumpResult(tag, jumpResult)
                st.write('Brightest point corresponds to the max speed')
                st.pydeck_chart(speedJumpTrajectory(jumpResult))


if '__main__' == __name__:
    main()
