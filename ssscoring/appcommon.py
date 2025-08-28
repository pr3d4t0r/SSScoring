# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

"""
Common functions, classes, and objects to all Streamlit apps in the SSScoring
package.
"""

from importlib_resources import files
from io import StringIO

from ssscoring import __VERSION__
from ssscoring.calc import isValidMaximumAltitude
from ssscoring.calc import isValidMinimumAltitude
from ssscoring.constants import DEFAULT_PLOT_INCREMENT
from ssscoring.constants import DEFAULT_PLOT_MAX_V_SCALE
from ssscoring.constants import DZ_DIRECTORY
from ssscoring.constants import FLYSIGHT_FILE_ENCODING
from ssscoring.constants import M_2_FT
from ssscoring.constants import RESOURCES
from ssscoring.datatypes import JumpResults
from ssscoring.datatypes import JumpStatus
from ssscoring.errors import SSScoringError
from ssscoring.notebook import SPEED_COLORS
from ssscoring.notebook import graphAcceleration
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
def fetchResource(resourceName: str) -> StringIO:
    """
    Fetch a file-like resource from the `PYTHONPATH` and `resources` module
    included in the SSScore package.  Common resources include the drop zones
    list CSV and in-line documentation Markdown text.

    Arguments
    ---------
        resourceName
    A string representing the resource file name, usually a CSV file.

    Returns
    -------
    An instance of `StringIO` ready to be process as a text stream by the
    caller.

    Raises
    ------
    `SSScoringError` if the resource dataframe isn't the global drop zones
    directory or the file is invalid in any way.
    """
    try:
        return StringIO(files(RESOURCES).joinpath(resourceName).read_bytes().decode(FLYSIGHT_FILE_ENCODING))
    except Exception as e:
        raise SSScoringError('Invalid resource - %s' % str(e))


def initDropZonesFromResource() -> pd.DataFrame:
    """
    Get the DZs directory from a CSV enclosed in the distribution package as a
    resource.  The resources package is fixed to `ssscoring.resources`, the
    default resource file is defined by `DZ_DIRECTORY` but can be anything.

    Returns
    -------
    The global drop zones directory as a dataframe.

    Raises
    ------
    `SSScoringError` if the resource dataframe isn't the global drop zones
    directory or the file is invalid in any way.
    """
    try:
        buffer = fetchResource(DZ_DIRECTORY)
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
    if resultsTable is not None:
        table = resultsTable.copy()
        table.vKMh = table.vKMh.apply(lambda x: round(x, 2))
        table.hKMh = table.hKMh.apply(lambda x: round(x, 2))
        table.deltaV = table.deltaV.apply(lambda x: round(x, 2))
        table.deltaAngle = table.deltaAngle.apply(lambda x: round(x, 2))
        table['altitude (ft)'] = table['altitude (ft)'].apply(lambda x: round(x, 1))
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
        badJumpLegend = '<span style="color: red">Warm up file or SMD ran out of battery - nothing to do<br>'
        scoringInfo = ''
    elif jumpResult.status == JumpStatus.SPEED_ACCURACY_EXCEEDS_LIMIT:
        badJumpLegend = '<span style="color: red">%s - RE-JUMP: speed accuracy exceeds ISC threshold<br>' % tag
        scoringInfo = ''
    elif jumpResult.status == JumpStatus.INVALID_SPEED_FILE:
        badJumpLegend = '<span style="color: red">Invalid or corrupted FlySight file - it\'s neither version 1 nor version 2<br>'
        scoringInfo = ''
    else:
        scoringInfo = 'Max speed = {0:,.0f}; '.format(maxSpeed)+('exit at %d m (%d ft)<br>Validation window starts at %d m (%d ft)<br>End scoring window at %d m (%d ft)<br>' % \
                        (window.start, M_2_FT*window.start, window.validationStart, M_2_FT*window.validationStart, window.end, M_2_FT*window.end))
    if (processBadJump and jumpStatus != JumpStatus.OK and jumpStatus != JumpStatus.WARM_UP_FILE and jumpStatus != JumpStatus.SPEED_ACCURACY_EXCEEDS_LIMIT and jumpStatus != JumpStatus.INVALID_SPEED_FILE) or jumpStatus == JumpStatus.OK:
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
    if jumpResult.data is not None:
        try:
            yMax = DEFAULT_PLOT_MAX_V_SCALE if jumpResult.score <= DEFAULT_PLOT_MAX_V_SCALE else jumpResult.score + DEFAULT_PLOT_INCREMENT
        except TypeError:
            yMax = DEFAULT_PLOT_MAX_V_SCALE
        plot = initializePlot(tag, backgroundColorName='#2c2c2c', yMax=yMax)
        plot = initializeExtraYRanges(plot, startY=min(jumpResult.data.altitudeAGLFt)-500.0, endY=max(jumpResult.data.altitudeAGLFt)+500.0)
        graphAltitude(plot, jumpResult)
        graphAngle(plot, jumpResult)
        graphAcceleration(plot, jumpResult)
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


def displayTrackOnMap(deck: pdk.Deck,
                      displayScore=True):
    """
    Displays a track map drawn using PyDeck.

    Arguments
    ---------
        deck
    A PyDeck initialized with map layers.

        displayScore
    If `True`, display the max score point; else display the max speed point.
    """
    if deck is not None:
        label = 'score' if displayScore else 'speed'
        st.write('Brightest point shows the max **%s** point.  Exit at orange point.  Each track dot is 4 m in diameter.' % label)
        st.pydeck_chart(deck)


@st.dialog('DZ Coordinates')
def displayDZCoordinates():
    """
    Display the DZ coordinates in a dialog if one is selected in the drop zones
    selection box.  The selection is stored in the  `st.session_state.currentDropZone`
    variable.  If a valid name is available, the latitude and longitude are
    displayed.  If `None` or invalid, a notification dialog is displayed.

    The corresponding UI button is only enabled if the user selected a valid DZ,
    otherwise the button is disabled.
    """
    dropZones = initDropZonesFromResource()
    lat = float(dropZones[dropZones.dropZone == st.session_state.currentDropZone ].iloc[0].lat)
    lon = float(dropZones[dropZones.dropZone == st.session_state.currentDropZone ].iloc[0].lon)
    st.write(st.session_state.currentDropZone)
    st.write('lat, lon: %.4f, %.4f' % (lat, lon))
    if st.button('OK'):
        st.rerun()


def setSideBarAndMain(icon: str, singleTrack: bool, selectDZState):
    """
    Set all the interactive and navigational components for the app's side bar.

    Arguments
    ---------
        icon
    A meaningful Emoji associated with the the side bar's title.

        singleTrack
    A flag for allowing selection of a single or multiple track files in the
    corresponding selector component.  Determines whether the side bar is used
    for the single- or multiple selection application.

        selectDZState
    A callback for the drop zone selector selection box, affected by events in
    the main application.

    Notes
    -----
    All the aplication level values associated with the components and
    selections from the side bar are stored in `st.session_state` and visible
    across the whole application.

    **Do not** cache calls to `ssscoring.appcommon.setSideBarAndMain()` because
    this can result in unpredictable behavior since the cache may never be
    cleared until application reload.
    """
    dropZones = initDropZonesFromResource()
    st.session_state.currentDropZone = None
    elevation = None
    st.sidebar.title('%s SSScore %s' % (icon, __VERSION__))
    st.session_state.processBadJump = st.sidebar.checkbox('Process bad jumps', value=True, help='Display results from invalid jumps')
    st.session_state.currentDropZone = st.sidebar.selectbox('Select the drop zone:', dropZones.dropZone, index=None, on_change=selectDZState, disabled=(elevation != None and elevation != 0.0))
    elevation = st.sidebar.number_input('...or enter the DZ elevation in meters:', min_value=0.0, max_value=4000.0, value='min', format='%.2f', disabled=(st.session_state.currentDropZone != None), on_change=selectDZState)
    if st.session_state.currentDropZone:
        st.session_state.elevation = dropZones[dropZones.dropZone == st.session_state.currentDropZone ].iloc[0].elevation
    elif elevation != None and elevation != 0.0:
        st.session_state.elevation= elevation
    else:
        st.session_state.elevation = None
        st.session_state.trackFiles = None
    st.sidebar.metric('Elevation', value='%.1f m' % (0.0 if st.session_state.elevation == None else st.session_state.elevation))
    if singleTrack:
        trackFile = st.sidebar.file_uploader('Track file', type=[ 'csv', ], disabled=st.session_state.elevation == None, key = st.session_state.uploaderKey)
        if trackFile:
            st.session_state.trackFile = trackFile
    else:
        trackFiles = st.sidebar.file_uploader(
            'Track files',
            type=[ 'csv', ],
            disabled=st.session_state.elevation == None,
            accept_multiple_files=True,
            key = st.session_state.uploaderKey
        )
        if trackFiles:
            st.session_state.trackFiles = trackFiles
    st.sidebar.button('Clear', on_click=selectDZState)
    st.sidebar.button('Display DZ coordinates', on_click=displayDZCoordinates, disabled=(st.session_state.currentDropZone == None))
    st.sidebar.link_button('Report missing DZ', 'https://github.com/pr3d4t0r/SSScoring/issues/new?template=report-missing-dz.md', icon=':material/breaking_news_alt_1:')
    st.sidebar.link_button('Feature request or bug report', 'https://github.com/pr3d4t0r/SSScoring/issues/new?template=Blank+issue', icon=':material/breaking_news_alt_1:')


def setSideBarDeprecated(icon: str):
    """
    Set a disabled version of the sidebar to maintain UX compatibility with the
    actual app, used when the main screen is configured to display an end-user
    message like "we moved to a new domain."

    Arguments
    ---------
        icon
    A meaningful Emoji associated with the the side bar's title.
    """
    dropZones = initDropZonesFromResource()
    st.session_state.currentDropZone = None
    elevation = None
    st.sidebar.title('%s SSScore %s' % (icon, __VERSION__))
    st.session_state.processBadJump = st.sidebar.checkbox('Process bad jumps', value=True, help='Display results from invalid jumps', disabled=True)
    st.session_state.currentDropZone = st.sidebar.selectbox('Select the drop zone:', dropZones.dropZone, index=None, disabled=True)
    elevation = st.sidebar.number_input('...or enter the DZ elevation in meters:', min_value=0.0, max_value=4000.0, value='min', format='%.2f', disabled=True)
    if st.session_state.currentDropZone:
        st.session_state.elevation = dropZones[dropZones.dropZone == st.session_state.currentDropZone ].iloc[0].elevation
    elif elevation != None and elevation != 0.0:
        st.session_state.elevation= elevation
    else:
        st.session_state.elevation = None
        st.session_state.trackFiles = None
    st.sidebar.metric('Elevation', value='%.1f m' % (0.0 if st.session_state.elevation == None else st.session_state.elevation))
    st.sidebar.file_uploader('Track file', type=[ 'csv', ], disabled=True)
    st.sidebar.button('Clear', disabled=True)
    st.sidebar.button('Display DZ coordinates', disabled=True)

