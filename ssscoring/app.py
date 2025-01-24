# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

"""
Streamlit-based application.

Issue deploying to Streamlit.io:
https://discuss.streamlit.io/t/pythonpath-issue-modulenotfounderror-in-same-package-where-app-is-defined/91170
"""

from importlib_resources import files
from io import StringIO

from ssscoring import __VERSION__
from ssscoring.calc import convertFlySight2SSScoring
from ssscoring.calc import getFlySightDataFromCSVBuffer
from ssscoring.calc import isValidMaximumAltitude
from ssscoring.calc import isValidMinimumAltitude
from ssscoring.calc import processJump
from ssscoring.constants import FLYSIGHT_FILE_ENCODING
from ssscoring.datatypes import JumpStatus
from ssscoring.dzdir import DROP_ZONES_LIST
from ssscoring.mapview import speedJumpTrajectory
from ssscoring.notebook import SPEED_COLORS
from ssscoring.notebook import graphAltitude
from ssscoring.notebook import graphAngle
from ssscoring.notebook import graphJumpResult
from ssscoring.notebook import initializeExtraYRanges
from ssscoring.notebook import initializePlot

import os
import psutil

import bokeh.models as bm
import pandas as pd
import streamlit as st


# *** constants ***

DEFAULT_DATA_LAKE = './data'
DZ_DIRECTORY = 'drop-zones-loc-elev.csv'
RESOURCES = 'ssscoring.resources'
STREAMLIT_SIG_KEY = 'HOSTNAME'
STREAMLIT_SIG_VALUE = 'streamlit'


# *** implementation ***

def _isStreamlitHostedApp() -> bool:
    keys = tuple(os.environ.keys())
    if STREAMLIT_SIG_KEY not in keys:
        return False
    if os.environ[STREAMLIT_SIG_KEY] == STREAMLIT_SIG_VALUE:
        return True
    return False


@st.cache_data
def _initDropZonesFromResource(resourceName: str) -> pd.DataFrame:
    buffer = StringIO(files(RESOURCES).joinpath(resourceName).read_bytes().decode(FLYSIGHT_FILE_ENCODING))
    dropZones = pd.read_csv(buffer, sep=',')
    return dropZones


def _initDropZonesFromObject() -> pd.DataFrame:
    return pd.DataFrame(DROP_ZONES_LIST)


def _setSideBarAndMain():
    # TODO:  Resolve this for Streamlit.io - why can't it use package resources?
    #        https://discuss.streamlit.io/t/package-resources-result-in-filenotfounderror-under-streamlit-io/91243/1
    # dropZones = _initDropZonesFromResource(DZ_DIRECTORY)
    dropZones = _initDropZonesFromObject()
    st.sidebar.title('SSScoring %s α' % __VERSION__)
    st.session_state.processBadJump = st.sidebar.checkbox('Process bad jump', value=True, help='Display results from invalid jumps')
    dropZone = st.sidebar.selectbox('Select drop zone:', dropZones.dropZone, index=None)
    if dropZone:
        st.session_state.elevation = dropZones[dropZones.dropZone == dropZone ].iloc[0].elevation
    else:
        st.session_state.elevation = None
        st.session_state.trackFile = None
    st.sidebar.metric('Elevation', value='%.1f m' % (0.0 if st.session_state.elevation == None else st.session_state.elevation))
    st.session_state.trackFile = st.sidebar.file_uploader('Track file', [ 'CSV' ], disabled=st.session_state.elevation == None)
    st.sidebar.html("<a href='https://github.com/pr3d4t0r/SSScoring/issues/new?template=Blank+issue' target='_blank'>Make a bug report or feature request</a>")


def _getJumpDataFrom(trackFileBuffer: str) -> pd.DataFrame:
    dropZoneAltMSLMeters = 0.0 if st.session_state.elevation == None else st.session_state.elevation
    data = None
    tag = None
    if dropZoneAltMSLMeters is not None:
        rawData, tag = getFlySightDataFromCSVBuffer(trackFileBuffer, st.session_state.trackFile.name)
        data = convertFlySight2SSScoring(rawData, altitudeDZMeters=dropZoneAltMSLMeters)
    return data, tag


def _displayJumpDataIn(resultsTable: pd.DataFrame):
    table = resultsTable.copy()
    table.vKMh = table.vKMh.apply(round)
    table.hKMh = table.hKMh.apply(round)
    table['altitude (ft)'] = table['altitude (ft)'].apply(round)
    table.netVectorKMh = table.netVectorKMh.apply(round)
    table.index = ['']*len(table)
    st.dataframe(table, hide_index=True)


def _closeWindow():
    js = 'window.open("", "_self").close();'
    temp = """
    <script>
    {%s}
    </script>
    """ % js
    st.html(temp)
    processID = os.getpid()
    p = psutil.Process(processID)
    p.terminate()


def main():
    if not _isStreamlitHostedApp():
        st.set_page_config(layout = 'wide')
    _setSideBarAndMain()

    col0, col1 = st.columns([ 0.4, 0.6, ])
    if st.session_state.trackFile:
        data, tag = _getJumpDataFrom(st.session_state.trackFile.getvalue())
        jumpResult = processJump(data)
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
        with col0:
            st.html('<h3>'+jumpStatusInfo+scoringInfo+(badJumpLegend if badJumpLegend else '')+'</h3>')
        if jumpStatus == JumpStatus.OK:
            with col0:
                _displayJumpDataIn(jumpResult.table)
            with col1:
                plot = initializePlot(tag)
                plot = initializeExtraYRanges(plot, startY=min(jumpResult.data.altitudeAGLFt)-500.0, endY=max(jumpResult.data.altitudeAGLFt)+500.0)
                graphAltitude(plot, jumpResult)
                graphAngle(plot, jumpResult)
                hoverValue = bm.HoverTool(tooltips=[('Y-val', '@y{0.00}',),])
                plot.add_tools(hoverValue)
                graphJumpResult(plot, jumpResult, lineColor=SPEED_COLORS[0])
                st.bokeh_chart(plot, use_container_width=True)
                st.write('Brightest point corresponds to the max speed')
                st.pydeck_chart(speedJumpTrajectory(jumpResult))

    if not _isStreamlitHostedApp():
        if st.sidebar.button('Exit'):
            _closeWindow()


if '__main__' == __name__:
    main()
