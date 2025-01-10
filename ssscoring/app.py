# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

"""
Streamlit-based application.
"""

from pathlib import Path

from ssscoring import __VERSION__
from ssscoring.calc import convertFlySight2SSScoring
from ssscoring.calc import getFlySightDataFromCSVFileName
from ssscoring.calc import isValidMaximumAltitude
from ssscoring.calc import isValidMinimumAltitude
from ssscoring.calc import processJump
from ssscoring.datatypes import JumpStatus

import os
import psutil

import pandas as pd
import streamlit as st


# *** constants ***

DEFAULT_DATA_LAKE = './data'
DZ_DIRECTORY = './resources/drop-zones-loc-elev.csv'


# *** globals ***

_session = st.session_state


# *** implementation ***


def _init():
    global _session

    if 'dataLake' not in _session:
        _session.dataLake = Path(DEFAULT_DATA_LAKE)


@st.cache_data
def _initDropZonesFrom(fileName: str) -> pd.DataFrame:
    dropZones = pd.read_csv(fileName, sep=',')
    return dropZones


def _setSideBarAndMain():
    dropZones = _initDropZonesFrom(DZ_DIRECTORY)
    st.sidebar.title('SSScoring %s α' % __VERSION__)
    dropZone = st.sidebar.selectbox('Select drop zone:', dropZones.dropZone, index=None)
    if dropZone:
        elevation = dropZones[dropZones.dropZone == dropZone ].iloc[0].elevation
        st.session_state.elevation = elevation
    else:
        elevation = 0.0
        st.session_state.elevation = None
    st.sidebar.metric('Elevation', value='%.1f m' % elevation)
    trackFile = st.sidebar.file_uploader('SMD file', [ 'CSV' ], disabled=(st.session_state.elevation == None))
    return trackFile


def _getJumpDataFrom(trackFile: str) -> pd.DataFrame:
    dropZoneAltMSLMeters = st.session_state.elevation
    data = None
    tag = None
    if dropZoneAltMSLMeters:
        rawData, tag = getFlySightDataFromCSVFileName(trackFile)
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


def main():
    st.set_page_config(layout = 'wide')
    _init()
    trackFile = _setSideBarAndMain()

    if trackFile:
        trackFileName = trackFile.name
        data, tag = _getJumpDataFrom(DEFAULT_DATA_LAKE+'/'+trackFileName)
        jumpResult = processJump(data)
        if jumpResult.status == JumpStatus.OK:
            validJumpStatus = '<hr><h1><span style="color: %s">%s jump - %s - score = %.01f km/h</span></h1>' % ('green', tag, 'VALID', jumpResult.score)
        maxSpeed = jumpResult.maxSpeed
        window = jumpResult.window
        if jumpResult.status == JumpStatus.OK:
            belowMaxAltitude = isValidMaximumAltitude(jumpResult.data.altitudeAGL.max())
            badJumpLegend = None
            if not isValidMinimumAltitude(jumpResult.data.altitudeAGL.max()):
                badJumpLegend = '<h3><span style="color: yellow"><span style="font-weight: bold">Warning:</span> exit altitude AGL was lower than the minimum scoring altitude according to IPC and USPA.</h3>'
            if not belowMaxAltitude:
                badJumpLegend = '<h3><span style="color: red"><span style="font-weight: bold">RE-JUMP:</span> exit altitude AGL exceeds the maximum altitude according to IPC and USPA.</h3>'
                validJumpStatus = '<hr><h1><span style="color: %s">%s jump - %s - %s</span></h1>' % ('red', tag, 'INVALID', JumpStatus.ALTITUDE_EXCEEDS_MAXIMUM)
            st.html(validJumpStatus)
            st.html('<h3>Max speed = {0:,.0f}; '.format(maxSpeed)+('exit at %d m (%d ft), end scoring window at %d m (%d ft)</h3?'%(window.start, 3.2808*window.start, window.end, 3.2808*window.end)))
            if badJumpLegend:
                st.html(badJumpLegend)
            _displayJumpDataIn(jumpResult.table)
    if st.sidebar.button('Exit'):
        _closeWindow()
        processID = os.getpid()
        p = psutil.Process(processID)
        p.terminate()


if '__main__' == __name__:
    main()

