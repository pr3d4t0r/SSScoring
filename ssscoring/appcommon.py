# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

"""
Common functions, classes, and objects to all Streamlit apps in the SSScoring
package.
"""

from importlib_resources import files
from io import StringIO

from ssscoring.calc import isValidMaximumAltitude
from ssscoring.calc import isValidMinimumAltitude
from ssscoring.constants import FLYSIGHT_FILE_ENCODING
from ssscoring.constants import M_2_FT
from ssscoring.datatypes import JumpResults
from ssscoring.datatypes import JumpStatus
from ssscoring.errors import SSScoringError
from ssscoring.notebook import SPEED_COLORS
from ssscoring.notebook import graphAltitude
from ssscoring.notebook import graphAngle
from ssscoring.notebook import graphJumpResult
from ssscoring.notebook import initializeExtraYRanges
from ssscoring.notebook import initializePlot

import os

import bokeh.models as bm
import pandas as pd
import pydeck as pdk
import streamlit as st


# *** constants ***

DEFAULT_DATA_LAKE = './data'
"""
Default data lake directory when reading files from the local file system.
"""

DZ_DIRECTORY = 'drop-zones-loc-elev.csv'
"""
The CSV file database dump of the drop zones directory.
"""

RESOURCES = 'ssscoring.resources'
"""
The package resources in the manifest or package wheel resources.
"""

STREAMLIT_SIG_KEY = 'HOSTNAME'
"""
Environment key used by the Streamlig.app environment when running an
application.
"""

STREAMLIT_SIG_VALUE = 'streamlit'
"""
Expected value associate with the environment variable `STREAMLIT_SIG_KEY` when
running in a Streamlit.app environment.
"""


# *** implementation ***

def isStreamlitHostedApp() -> bool:
    """
    Detect if the hosting environment is a native Python system or a Streamlit
    app environment hosted by streamlit.io or Snowflake.

    Returns
    -------
    `True` if the app is running in the Streamlit app or Snoflake app
    environment, otherwise `False`.
    """
    keys = tuple(os.environ.keys())
    if STREAMLIT_SIG_KEY not in keys:
        return False
    if os.environ[STREAMLIT_SIG_KEY] == STREAMLIT_SIG_VALUE:
        return True
    return False


@st.cache_data
def initDropZonesFromResource(resourceName: str) -> pd.DataFrame:
    """
    Get the DZs directory from a CSV enclosed in the distribution package as a
    resource.  The resources package is fixed to `ssscoring.resources`, the
    default resource file is defined by `DZ_DIRECTORY` but can be anything.

    Arguments
    ---------
        resourceName
    A string representing the resource file name, usually a CSV file.

    Returns
    -------
    The global drop zones directory as a dataframe.

    Raises
    ------
    `SSScoringError` if the resource dataframe isn't the global drop zones
    directory or the file is invalid in any way.
    """
    try:
        buffer = StringIO(files(RESOURCES).joinpath(resourceName).read_bytes().decode(FLYSIGHT_FILE_ENCODING))
        dropZones = pd.read_csv(buffer, sep=',')
    except Exception as e:
        raise SSScoringError('Invalid resource - %s' % str(e))

    if 'dropZone' not in dropZones.columns:
        raise SSScoringError('dropZone object is a dataframe but not the drop zones directory')

    return dropZones


def displayJumpDataIn(resultsTable: pd.DataFrame):
    """
    Display the individual results, as a table.

    Arguments
    ---------
        resultsTable: pd.DataFrame
    The results from a speed skydiving jump.

    See
    ---
    `ssscoring.datatypes.JumpResults`
    """
    table = resultsTable.copy()
    table.vKMh = table.vKMh.apply(lambda x: round(x, 2))
    table.hKMh = table.hKMh.apply(lambda x: round(x, 2))
    table.deltaV = table.deltaV.apply(lambda x: round(x, 2))
    table.deltaAngle = table.deltaAngle.apply(lambda x: round(x, 2))
    table['altitude (ft)'] = table['altitude (ft)'].apply(lambda x: round(x, 1))
    # TODO:  Decide if we'll keep this one.  Delete after 20250401 if present.
    # table.netVectorKMh = table.netVectorKMh.apply(round)
    table.index = ['']*len(table)
    st.dataframe(table, hide_index=True)


def interpretJumpResult(tag: str,
                        jumpResult: JumpResults,
                        processBadJump: bool):
    """
    Interpret the jump results and generate the corresponding labels and
    warnings if a jump is invalid, or only "somewhat valid" according to ISC
    rules.  The caller turns results display on/off depending on training vs
    in-competition settins.  Because heuristics are a beautiful thing.

    Arguments
    ---------
        tag
    A string that identifies a specific jump and the FlySight version that
    generated the corresponding track file.  Often in the form: `HH-mm-ss:vX`
    where `X` is the FlySight hardware version.

        jumpResult
    An instance of `ssscoring.datatypes.JumpResults` with jump data.

        processBadJump
    If `True`, generate end-user warnings as part of its results processing if
    the jump is invalid because of ISC rules, but set the status to OK so that
    the jump may be displayed.

    Returns
    -------
    A `tuple` of these objects:

    - `jumpStatusInfo` - the jump status, in human-readable form
    - `scoringInfo` - Max speed, scoring window, etc.
    - `badJumpLegend` - A warning or error if the jump is invalid according to
      ISC rules
    - `jumpStatus` - An instance of `JumpStatus` that may have been overriden to
      `OK` if `processBadJump` was set to `True` and the jump was invalid.  Used
      only for display.  Use `jumpResult.status` to determine the actual result
      of the jump from a strict scoring perspective.  `jumpStatus` is  used
      for display override purposes only.
    """
    maxSpeed = jumpResult.maxSpeed
    window = jumpResult.window
    jumpStatus = jumpResult.status
    jumpStatusInfo = ''
    if jumpResult.status == JumpStatus.WARM_UP_FILE:
        badJumpLegend = '<span style="color: red">Warm up file - nothing to do<br>'
        scoringInfo = ''
    elif jumpResult.status == JumpStatus.SPEED_ACCURACY_EXCEEDS_LIMIT:
        badJumpLegend = '<span style="color: red">%s - RE-JUMP: speed accuracy exceeds ISC threshold<br>' % tag
        scoringInfo = ''
    else:
        scoringInfo = 'Max speed = {0:,.0f}; '.format(maxSpeed)+('exit at %d m (%d ft)<br>Validation window starts at %d m (%d ft)<br>End scoring window at %d m (%d ft)<br>' % \
                        (window.start, M_2_FT*window.start, window.validationStart, M_2_FT*window.validationStart, window.end, M_2_FT*window.end))
    if (processBadJump and jumpStatus != JumpStatus.OK) or jumpStatus == JumpStatus.OK:
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
    return jumpStatusInfo, scoringInfo, badJumpLegend, jumpStatus


def plotJumpResult(tag: str,
                   jumpResult: JumpResults):
    """
    Plot the jump results including altitude, horizontal speed, time, etc. for
    evaluation and interpretation.

    Arguments
    ---------
        tag
    A string that identifies a specific jump and the FlySight version that
    generated the corresponding track file.  Often in the form: `HH-mm-ss:vX`
    where `X` is the FlySight hardware version.

        jumpResult
    An instance of `ssscoring.datatypes.JumpResults` with jump data.
    """
    plot = initializePlot(tag)
    plot = initializeExtraYRanges(plot, startY=min(jumpResult.data.altitudeAGLFt)-500.0, endY=max(jumpResult.data.altitudeAGLFt)+500.0)
    graphAltitude(plot, jumpResult)
    graphAngle(plot, jumpResult)
    hoverValue = bm.HoverTool(tooltips=[('time', '@x{0.0}s'), ('y-val', '@y{0.00}')])
    plot.add_tools(hoverValue)
    graphJumpResult(plot, jumpResult, lineColor=SPEED_COLORS[0])
    st.bokeh_chart(plot, use_container_width=True)


def initFileUploaderState(filesObject:str, uploaderKey:str ='uploaderKey'):
    """
    Initialize the session state for the Streamlit app uploader so that
    selections can be cleared in callbacks later.

    **Important**: `initFileUploaderState()` __must__ be called after setting the
    page configuration (per Streamlit architecture rules) and before adding any
    widgets to the sidebars, containers, or main application.

    Argument
    --------
        filesObject
    A `str` name that is either `'trackFile'` for the single track file process
    or `'trackFiles'` for the app page that handles more than one track file at
    a time.

        uploaderKey
    A unique identifier for the uploader key component, usually set to
    `'uploaderKey'` but can be any arbitrary name.  This value must match the
    `file_uploader(..., key=uploaderKey,...)` value.

    """
    if filesObject not in st.session_state:
        st.session_state[filesObject] = None
    if uploaderKey not in st.session_state:
        st.session_state[uploaderKey] = 0


def displayTrackOnMap(deck: pdk.Deck):
    st.write('Brightest point corresponds to the max speed score')
    st.pydeck_chart(deck)

