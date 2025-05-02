# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

from geopy import distance
from ssscoring.datatypes import JumpResults

import pandas as pd
import pydeck as pdk


# *** constants ***

DISTANCE_FROM_MIDDLE = 400.0
"""
The distance in meters from the middle of the skydive to the outer bounding box
for the initial view of a new rendered map.
"""


# *** implementation ***

def viewPointBox(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the NW and SE corners of a "box" delimiting the viewport area
    `DISTANCE_FROM_MIDDLE` meters away from the middle of the speed skydive.

    Arguments
    ---------
        data
    A SSScoring dataframe with jump data.

    Returns
    -------
    The NW and SE corners of the box, as terrestrial coordinates, in a dataframe
    with these columns:

    - `latitude`
    - `lontigude`

    See
    ---
    `ssscoring.calc.convertFlySight2SSScoring`
    """
    mid = len(data)//2
    datum = data.iloc[mid]
    origin = (datum.latitude, datum.longitude)
    pointNW = distance.distance(meters=DISTANCE_FROM_MIDDLE).destination(origin, bearing=315)
    pointSE = distance.distance(meters=DISTANCE_FROM_MIDDLE).destination(origin, bearing=135)
    data = list(zip([ pointNW[0], pointSE[0], ], [ pointNW[1], pointSE[1], ]))
    result = pd.DataFrame(data, columns=[ 'latitude', 'longitude', ])
    return result


def _resolveMaxSpeedTimeFrom(jumpResult: JumpResults) -> float:
    plotTime = jumpResult.scores[jumpResult.score]

    return plotTime


def speedJumpTrajectory(jumpResult: JumpResults) -> pdk.Deck:
    # TODO:  https://en.wikipedia.org/wiki/X11_color_names
    """
    Build the layers for a PyDeck map showing a jumper's trajectory.

    Arguments
    ---------
        jumpResult
    A SSScoring `JumpResults` instance with the results of the jump.

    Returns
    -------
    A PyDeck `deck` instance ready for rendering using PyDeck or Streamlit
    mapping facilities.

    See
    ---
    `st.pydeck_chart`
    `st.map`
    """
    if jumpResult.data is not None:
        workData = jumpResult.data.copy()
        maxSpeedTime = _resolveMaxSpeedTimeFrom(jumpResult)
        layers = [
            pdk.Layer(
                'ScatterplotLayer',
                data=workData.head(1),
                get_color=[ 255, 126, 0, 255 ],
                get_position=[ 'longitude', 'latitude', ],
                get_radius=8),
            pdk.Layer(
                'ScatterplotLayer',
                data=workData.tail(1),
                get_color=[ 0, 192, 0, 160 ],
                get_position=[ 'longitude', 'latitude', ],
                get_radius=8),
            pdk.Layer(
                'ScatterplotLayer',
                data=workData[workData.plotTime == maxSpeedTime],
                get_color=[ 0, 255, 0, ],
                get_position=[ 'longitude', 'latitude', ],
                get_radius=12),
            pdk.Layer(
                'ScatterplotLayer',
                data=workData,
                # get_color=[ 0, 192, 0, 255 ],
                get_color=[ 0x64, 0x95, 0xed, 255 ],
                get_position=[ 'longitude', 'latitude', ],
                get_radius=2),
            pdk.Layer(
                'ScatterplotLayer',
                data=workData[workData.plotTime == maxSpeedTime],
                get_color=[ 0, 128, 0, ],
                get_position=[ 'longitude', 'latitude', ],
                get_radius=4),
        ]
        viewBox = viewPointBox(workData)
        deck = pdk.Deck(
            map_style = None,
            initial_view_state=pdk.data_utils.compute_view(viewBox[['longitude', 'latitude',]]),
            layers=layers
        )
        return deck


def multipleSpeedJumpsTrajectories(jumpResults):
    """
    **EXPERIMENTAL**
    """
    mapLayers = list()
    for result in jumpResults.values():
        workData = result.data.copy()
        maxSpeedTime = _resolveMaxSpeedTimeFrom(result)
        layers = [
            pdk.Layer(
                'ScatterplotLayer',
                data=workData,
                # get_color=[ 0, 160, 0, 128 ],
                get_color=[ 0, 192, 0, 255 ],
                get_position=[ 'longitude', 'latitude', ],
                t_radius=4),
            pdk.Layer(
                'ScatterplotLayer',
                data=workData.head(1),
                get_color=[ 255, 126, 0, 255 ],
                get_position=[ 'longitude', 'latitude', ],
                get_radius=8),
            pdk.Layer(
                'ScatterplotLayer',
                data=workData.tail(1),
                get_color=[ 0, 192, 0, 160 ],
                get_position=[ 'longitude', 'latitude', ],
                get_radius=8),
            pdk.Layer(
                'ScatterplotLayer',
                data=workData[workData.plotTime == maxSpeedTime],
                get_color=[ 0, 255, 0, ],
                get_position=[ 'longitude', 'latitude', ],
                get_radius=12),
        ]
        mapLayers += layers

    viewBox = viewPointBox(workData)
    deck = pdk.Deck(
        map_style = None,
        initial_view_state=pdk.data_utils.compute_view(viewBox[['longitude', 'latitude',]]),
        layers=mapLayers
    )
    return deck

