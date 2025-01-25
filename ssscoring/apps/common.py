# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

"""
Common functions, classes, and objects to all Streamlit apps in the SSScoring
package.
"""

from importlib_resources import files
from io import StringIO

from ssscoring.constants import FLYSIGHT_FILE_ENCODING
from ssscoring.dzdir import DROP_ZONES_LIST
from ssscoring.errors import SSScoringError

import os

import pandas as pd
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


def initDropZonesFromObject() -> pd.DataFrame:
    return pd.DataFrame(DROP_ZONES_LIST)


def displayJumpDataIn(resultsTable: pd.DataFrame):
    """
    TODO:  Documentation
    """
    table = resultsTable.copy()
    table.vKMh = table.vKMh.apply(round)
    table.hKMh = table.hKMh.apply(round)
    table['altitude (ft)'] = table['altitude (ft)'].apply(round)
    table.netVectorKMh = table.netVectorKMh.apply(round)
    table.index = ['']*len(table)
    st.dataframe(table, hide_index=True)



