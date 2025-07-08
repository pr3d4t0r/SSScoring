# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

from geopy import distance
from ssscoring.constants import SAMPLE_RATE
from ssscoring.constants import SCORING_INTERVAL
from ssscoring.datatypes import JumpResults
from ssscoring.notebook import SPEED_COLORS
from ssscoring.notebook import convertHexColorToRGB

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


def _resolveMaxScoreTimeFrom(jumpResult: JumpResults) -> float:
    scoreTime = jumpResult.scores[jumpResult.score]
    workData = jumpResult.data.reset_index(drop=True).copy()
    ref = workData.index[workData.plotTime == scoreTime][0]+round(SCORING_INTERVAL/SAMPLE_RATE/2.0)-1
    return workData.iloc[ref].plotTime


def _resolveMaxSpeedTimeFrom(jumpResult: JumpResults) -> float:
    rowIndex = jumpResult.data.vKMh.idxmax()
    plotTime = jumpResult.data.loc[rowIndex, 'plotTime']
    return plotTime


def speedJumpTrajectory(jumpResult: JumpResults,
                        displayScorePoint: bool=True) -> pdk.Deck:
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
    if jumpResult.data is not None and jumpResult.score != None and jumpResult.scores != None:
        workData = jumpResult.data.copy()
        scoresData = pd.DataFrame(list(jumpResult.scores.items()), columns=[ 'score', 'plotTime', ])
        workData = pd.merge(workData, scoresData, on='plotTime', how='left')
        workData.vKMh = workData.vKMh.apply(lambda x: round(x, 2))
        workData.speedAngle = workData.speedAngle.apply(lambda x: round(x, 2))
        if displayScorePoint:
            maxValueTime = _resolveMaxScoreTimeFrom(jumpResult)
            maxColorOuter = [ 0, 255, 0, ]
            maxCollorDot = [ 0, 128, 0, ]
        else:
            maxValueTime = _resolveMaxSpeedTimeFrom(jumpResult)
            maxColorOuter = [ 255, 0, 0, 255, ]  # red
            maxCollorDot = [ 255, 255, 0, 255, ]  # yellow
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
                data=workData[workData.plotTime == maxValueTime],
                get_color=maxColorOuter,
                get_position=[ 'longitude', 'latitude', ],
                get_radius=12),
            pdk.Layer(
                'ScatterplotLayer',
                data=workData,
                get_color=[ 0x64, 0x95, 0xed, 255 ],
                get_position=[ 'longitude', 'latitude', ],
                get_radius=2,
                pickable=True),
            pdk.Layer(
                'ScatterplotLayer',
                data=workData[workData.plotTime == maxValueTime],
                get_color=maxCollorDot,
                get_position=[ 'longitude', 'latitude', ],
                get_radius=4),
        ]
        viewBox = viewPointBox(workData)
        tooltip = {
            # TODO:  Figure out how to plot the score @ plotTime here.
            # 'html': '<b>plotTime:</b> {plotTime} s<br><b>Score:</b> {score} km/h<br><b>Speed:</b> {vKMh} km/h<br><b>speedAngle:</b> {speedAngle}º',
            'html': '<b>plotTime:</b> {plotTime} s<br><b>Speed:</b> {vKMh} km/h<br><b>speedAngle:</b> {speedAngle}º',
            'style': {
                'backgroundColor': 'steelblue',
                'color': 'white',
            },
            'cursor': 'default',
        }
        deck = pdk.Deck(
            map_style = None,
            layers=layers,
            initial_view_state=pdk.data_utils.compute_view(viewBox[['longitude', 'latitude',]]),
            tooltip=tooltip,
        )
        return deck


def multipleSpeedJumpsTrajectories(jumpResults):
    """
    Build all the layers for a PyDeck map showing the trajectories of every jump
    in the results set.

    Arguments
    ---------
        jumpResults
    A dictionary of all the jump results after processing.

    Returns
    -------
    A PyDeck `deck` instance ready for rendering using PyDeck or Streamlit
    mapping facilities.

    See
    ---
    `st.pydeck_chart`
    `st.map`
    """
    mapLayers = list()
    mixColor = 0
    resultTags = sorted(list(jumpResults.keys()), reverse=True)
    for tag in resultTags:
        result = jumpResults[tag]
        if result.scores != None:
            workData = result.data.copy()
            exitPointData = workData.head(1)
            exitPointData['label'] = tag
            maxScoreTime = _resolveMaxScoreTimeFrom(result)
            mixColor = (mixColor+1)%len(SPEED_COLORS)
            layers = [
                pdk.Layer(
                    'ScatterplotLayer',
                    data=exitPointData,
                    get_color=[ 255, 126, 0, 255 ],
                    get_position=[ 'longitude', 'latitude', ],
                    pickable=True,
                    get_radius=8),
                pdk.Layer(
                    'TextLayer',
                    data=exitPointData,
                    get_position=[ 'longitude', 'latitude', ],
                    get_text='label',
                    # get_color=convertHexColorToRGB(SPEED_COLORS[mixColor]),
                    get_color=[ 255, 255, 255, 255, ],
                    get_background_color=[ 0, 0, 0, 255, ],
                    background=True,
                    get_size=12,
                ),
                pdk.Layer(
                    'ScatterplotLayer',
                    data=workData.tail(1),
                    get_color=[ 0, 192, 0, 160 ],
                    get_position=[ 'longitude', 'latitude', ],
                    get_radius=8),
                pdk.Layer(
                    'ScatterplotLayer',
                    data=workData[workData.plotTime == maxScoreTime],
                    get_color=[ 0, 255, 0, ],
                    get_position=[ 'longitude', 'latitude', ],
                    get_radius=12),
                pdk.Layer(
                    'ScatterplotLayer',
                    data=workData,
                    get_color = convertHexColorToRGB(SPEED_COLORS[mixColor]),
                    get_position=[ 'longitude', 'latitude', ],
                    get_radius=2),
                pdk.Layer(
                    'ScatterplotLayer',
                    data=workData[workData.plotTime == maxScoreTime],
                    get_color=[ 0, 128, 0, ],
                    get_position=[ 'longitude', 'latitude', ],
                    get_radius=4),
            ]
            mapLayers += layers
    viewBox = viewPointBox(workData)
    deck = pdk.Deck(
        map_style = None,
        initial_view_state=pdk.data_utils.compute_view(viewBox[['longitude', 'latitude',]]),
        layers=mapLayers,
    )
    return deck

