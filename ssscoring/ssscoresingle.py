# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

"""
Streamlit-based application.

Issue deploying to Streamlit.io:
https://discuss.streamlit.io/t/pythonpath-issue-modulenotfounderror-in-same-package-where-app-is-defined/91170
"""

from ssscoring import __VERSION__
from ssscoring.appcommon import DZ_DIRECTORY
from ssscoring.appcommon import displayJumpDataIn
from ssscoring.appcommon import displayTrackOnMap
from ssscoring.appcommon import initDropZonesFromResource
from ssscoring.appcommon import initFileUploaderState
from ssscoring.appcommon import interpretJumpResult
from ssscoring.appcommon import isStreamlitHostedApp
from ssscoring.appcommon import plotJumpResult
from ssscoring.calc import convertFlySight2SSScoring
from ssscoring.calc import dropNonSkydiveDataFrom
from ssscoring.calc import getFlySightDataFromCSVBuffer
from ssscoring.calc import processJump
from ssscoring.constants import M_2_FT
from ssscoring.constants import SPEED_ACCURACY_THRESHOLD
from ssscoring.datatypes import JumpStatus
from ssscoring.datatypes import PerformanceWindow
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
    st.sidebar.title('1️⃣  SSScore %s' % __VERSION__)
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
    st.sidebar.link_button('Report missing DZ', 'https://github.com/pr3d4t0r/SSScoring/issues/new?template=report-missing-dz.md', icon=':material/breaking_news_alt_1:')
    st.sidebar.link_button('Feature request or bug report', 'https://github.com/pr3d4t0r/SSScoring/issues/new?template=Blank+issue', icon=':material/breaking_news_alt_1:')


def _getJumpDataFrom(trackFileBuffer: str) -> pd.DataFrame:
    dropZoneAltMSLMeters = 0.0 if st.session_state.elevation == None else st.session_state.elevation
    data = None
    tag = None
    if dropZoneAltMSLMeters is not None:
        rawData, tag = getFlySightDataFromCSVBuffer(trackFileBuffer, st.session_state.trackFile.name)
        data = convertFlySight2SSScoring(rawData, altitudeDZMeters=dropZoneAltMSLMeters)
    return data, tag


def _displayAllJumpDataIn(data: pd.DataFrame):
    columns = [ 'plotTime' ] + [ column for column in data.columns if column != 'plotTime' and column != 'timeUnix' ]
    st.html('<h3>All rows of jump data</h3>')
    st.dataframe(data,
        column_order=columns,
        # TODO:  Decide if we apply the same format to all columns
        column_config={
            'plotTime': st.column_config.NumberColumn(format='%.02f'),
            'speedAngle': st.column_config.NumberColumn(format='%.02f'),
            'speedAccuracyISC': st.column_config.NumberColumn(format='%.02f'),
        },
        hide_index=True)


def _displayScoresIn(rawData: dict):
    st.html('<h3>Scores</h3>')
    data = pd.DataFrame.from_dict({ 'time': rawData.values(), 'score': rawData.keys(), })
    data.time = data.time.apply(lambda x: '%.2f' % x)
    st.dataframe(data, hide_index=True)


def _displayBadRowsISCAccuracyExceeded(data: pd.DataFrame, window: PerformanceWindow):
    badRows = data[data.speedAccuracyISC >= SPEED_ACCURACY_THRESHOLD]
    badRows = dropNonSkydiveDataFrom(badRows)
    times = pd.to_datetime(badRows.timeUnix, unit='s').dt.strftime('%Y-%m-%d %H:%M:%S.%f').str[:-4]
    badRows.insert(0, 'time', times)
    badRows.drop(columns = [
        'timeUnix',
        'altitudeMSL',
        'altitudeMSLFt',
        'speedAccuracy',
        'hMetersPerSecond',
        'hKMh',
        'speedAngle',
        'latitude',
        'longitude',
        'verticalAccuracy', ], inplace=True)
    st.html('<h3>Performance window:<br>start = %.2f m (%.2f ft)<br>end = %.2f m (%.2f ft)<br>validation start = %.2f m (%.2f ft)</h3>' % \
                    (window.start, M_2_FT*window.start, window.end, M_2_FT*window.end, window.validationStart, M_2_FT*window.validationStart))
    st.html('<h3>%d track rows where the ISC speed accuracy threshold was exceeded during the speed run:</h3>' % len(badRows))
    st.dataframe(badRows, hide_index=True)


    workData = data.copy()
    workData = dropNonSkydiveDataFrom(workData)
    times = pd.to_datetime(workData.timeUnix, unit='s').dt.strftime('%Y-%m-%d %H:%M:%S.%f').str[:-4]
    workData.insert(0, 'time', times)
    st.html('<h3>Full speed run data (%d rows)</h3>' % len(workData))
    st.dataframe(workData, hide_index=True)


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
        if (st.session_state.processBadJump and jumpStatus != JumpStatus.OK) or jumpStatus == JumpStatus.OK:
            with col0:
                displayJumpDataIn(jumpResult.table)
                _displayAllJumpDataIn(jumpResult.data)
                _displayScoresIn(jumpResult.scores)
            with col1:
                plotJumpResult(tag, jumpResult)
                displayTrackOnMap(speedJumpTrajectory(jumpResult))
        elif jumpStatus == JumpStatus.SPEED_ACCURACY_EXCEEDS_LIMIT:
            with col0:
                _displayBadRowsISCAccuracyExceeded(data, jumpResult.window)


if '__main__' == __name__:
    main()

