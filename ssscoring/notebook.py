# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

"""
## Utility reusable code for notebooks.
"""

from ssscoring.calc import forwardLateralDisplacement
from ssscoring.calc import jumpRunBearing
from ssscoring.constants import DEFAULT_PLOT_MAX_V_SCALE
from ssscoring.constants import DEFAULT_SPEED_ACCURACY_SCALE
from ssscoring.constants import MAX_ALTITUDE_FT
from ssscoring.constants import MAX_HORIZONTAL_DISTANCE
from ssscoring.constants import SAFE_HORIZONTAL_COLOR
from ssscoring.constants import SAFE_HORIZONTAL_DISTANCE
from ssscoring.constants import SPEED_ACCURACY_THRESHOLD
from ssscoring.constants import UNSAFE_HORIZONTAL_COLOR
from ssscoring.datatypes import PerformanceWindow
from ssscoring.errors import SSScoringError

import pandas as pd
import plotly.graph_objects as go


# *** constants ***

DEFAULT_AXIS_COLOR = 'lightsteelblue'
"""
CSS color name for the axis colors used in notebooks and Streamlit with Plotly.
"""


# Ref:  https://www.w3schools.com/colors/colors_groups.asp
SPEED_COLORS = colors = ('#32cd32', '#0000ff', '#ff6347', '#40e0d0', '#00bfff', '#22b822', '#ff7f50', '#008b8b',)
"""
Colors used for tracking the lines in a multi-jump plot, so that each track is
associated with a different color and easier to visualize.  8 distinct colors,
corresponding to each jump in a competition.
"""

COLOR_FASTEST = '#32cd32'
"""Limegreen — fastest jump track color in aggregate displays; matches the table's max-score highlight."""

COLOR_SLOWEST = '#ff4500'
"""Orangered — slowest jump track color in aggregate displays; matches the table's min-score highlight."""

COLORS_OTHERS = (
    '#1e90ff',
    '#4169e1',
    '#0000cd',
    '#00bfff',
    '#6495ed',
    '#4682b4',
)
"""Six distinct blue shades for all non-fastest, non-slowest jumps in aggregate displays."""


# Map Bokeh-era named ranges to Plotly y-axis IDs.  Preserves the rangeName
# kwarg API on graphAltitude/graphAngle/graphAcceleration callers.
_Y_AXIS_MAP = {
    'speed':         'y',     # default — vKMh, hKMh, score scatter
    'altitudeFt':    'y2',
    'angle':         'y3',
    'vAccelMS2':     'y4',
    'speedAccuracy': 'y5',
}


# *** functions ***

def initializePlot(jumpTitle: str,
                   height=500,
                   width=900,
                   xLabel='seconds from exit',
                   yLabel='km/h',
                   xMax=35.0,
                   yMax=DEFAULT_PLOT_MAX_V_SCALE,
                   backgroundColorName='#1a1a1a',
                   colorName=DEFAULT_AXIS_COLOR):
    """
    Initialize a Plotly figure for SSScoring jump plots, configured with the
    main speed (km/h) Y axis.  Extra Y axes for altitude / angle / acceleration /
    speed-accuracy are added by initializeExtraYRanges().

    Returns
    -------
    A `plotly.graph_objects.Figure`.
    """
    figure = go.Figure()
    figure.update_layout(
        title=dict(text=jumpTitle, font=dict(color=colorName)),
        height=height,
        autosize=True,
        plot_bgcolor=backgroundColorName,
        paper_bgcolor=backgroundColorName,
        font=dict(color=colorName),
        hovermode='x unified',
        showlegend=True,
        legend=dict(font=dict(color=colorName)),
        xaxis=dict(
            title=dict(text=xLabel, font=dict(color=colorName)),
            autorange=True,
            color=colorName,
            tickfont=dict(color=colorName),
            showgrid=True,                              # ← changed
            gridcolor='rgba(255,255,255,0.08)',         # ← added — subtle grid on dark bg
            showline=True,                              # ← added — visible axis line
            linecolor=colorName,                        # ← added
            zeroline=False,
        ),
        yaxis=dict(
            title=dict(text=yLabel, font=dict(color=colorName)),
            autorange=True,
            color=colorName,
            tickfont=dict(color=colorName),
            anchor='x',
            side='left',
            showgrid=True,                              # ← changed
            gridcolor='rgba(255,255,255,0.08)',         # ← added
            showline=True,                              # ← added
            linecolor=colorName,                        # ← added
            zeroline=False,
        ),
    )
    return figure


def _graphSegment(figure,
                  x0=0.0,
                  y0=0.0,
                  x1=0.0,
                  y1=0.0,
                  lineWidth=1,
                  color='black'):
    """
    Draw a line segment annotation on the plot's main axes.  Plotly equivalent
    of Bokeh's plot.segment().
    """
    figure.add_shape(
        type='line',
        x0=x0, y0=y0,
        x1=x1, y1=y1,
        line=dict(color=color, width=lineWidth),
        xref='x', yref='y',
    )


def initializeExtraYRanges(figure,
                           startY: float = 0.0,
                           endY: float = MAX_ALTITUDE_FT,
                           maxSpeedAccuracy: float | None = None):
    """
    Configure additional Y axes on the plot for altitude (ft), angle, vertical
    acceleration, and speed accuracy traces.  Plotly equivalent of Bokeh's
    extra_y_ranges + LinearAxis layout.
    """
    LEFT_MARGIN = 0.24
    AXIS_SPACING = 0.06
    POSITIONS = [n*AXIS_SPACING for n in range(4)]  # 0.00, 0.06, 0.12, 0.18

    speedAccuracyEnd = DEFAULT_SPEED_ACCURACY_SCALE
    if maxSpeedAccuracy is not None and maxSpeedAccuracy >= SPEED_ACCURACY_THRESHOLD:
        speedAccuracyEnd = maxSpeedAccuracy * 1.1

    color = DEFAULT_AXIS_COLOR

    figure.update_xaxes(domain=(LEFT_MARGIN, 1.0))

    mainYTitle = (figure.layout.yaxis.title.text or 'km/h')
    figure.update_yaxes(title=None)

    figure.update_layout(
        yaxis2=dict(
            autorange=True,
            anchor='free', overlaying='y', side='left', position=POSITIONS[0],
            color=color, tickfont=dict(color=color),
            showline=True, linecolor=color,
            showgrid=False, zeroline=False,
        ),
        yaxis3=dict(
            autorange=True,
            anchor='free', overlaying='y', side='left', position=POSITIONS[1],
            color=color, tickfont=dict(color=color),
            showline=True, linecolor=color,
            showgrid=False, zeroline=False,
        ),
        yaxis4=dict(
            autorange=True,
            anchor='free', overlaying='y', side='left', position=POSITIONS[2],
            color=color, tickfont=dict(color=color),
            showline=True, linecolor=color,
            showgrid=False, zeroline=False,
        ),
        yaxis5=dict(
            range=(0.0, speedAccuracyEnd),
            anchor='free', overlaying='y', side='left', position=POSITIONS[3],
            color=color, tickfont=dict(color=color),
            showline=True, linecolor=color,
            showgrid=False, zeroline=False,
        ),
    )

    titles = [
        (POSITIONS[0], 'Alt (ft)'),
        (POSITIONS[1], 'angle'),
        (POSITIONS[2], 'Vertical acceleration m/s²'),
        (POSITIONS[3], 'Speed accuracy ISC'),
        (LEFT_MARGIN,  mainYTitle),
    ]
    for pos, text in titles:
        figure.add_annotation(
            xref='paper', yref='paper',
            x=pos + 0.012, y=0.5,
            text=text,
            showarrow=False,
            textangle=-90,
            font=dict(color=color, size=11),
            xanchor='center', yanchor='middle',
        )

    return figure


def validationWindowDataFrom(data: pd.DataFrame, window: PerformanceWindow) -> pd.DataFrame:
    """
    Generate the validation window dataset for plotting the ISC speed accuracy
    values.  Subset defined from the end of the scoring window to the
    validation start.

    NOTE: return type changed from bokeh.models.ColumnDataSource (Bokeh era) to
    pd.DataFrame as part of the Plotly migration.  Columns: 'x', 'y'.
    """
    validationData = data[data.altitudeAGL <= window.validationStart]
    return pd.DataFrame({
        'x': validationData.plotTime.values,
        'y': validationData.speedAccuracyISC.values,
    })


def _plotSpeedAccuracy(figure, data, window):
    accuracyData = validationWindowDataFrom(data, window)
    figure.add_trace(go.Scatter(
        x=accuracyData['x'],
        y=accuracyData['y'],
        mode='lines',
        name='Speed accuracy ISC',
        line=dict(color='lime', width=5.0),
        yaxis='y5',
        hovertemplate='accuracy: %{y:.2f}<extra></extra>',
    ))
    validationData = data[data.altitudeAGL <= window.validationStart]
    figure.add_trace(go.Scatter(
        x=validationData.plotTime,
        y=[SPEED_ACCURACY_THRESHOLD] * len(validationData),
        mode='lines',
        line=dict(color='lime', width=1.0, dash='dash'),
        yaxis='y5',
        showlegend=False,
        hoverinfo='skip',
    ))


def graphJumpResult(figure,
                    jumpResult,
                    lineColor='green',
                    legend='speed',
                    showIt=True,
                    showAccuracy=True):
    """
    Graph the jump results onto the initialized Plotly figure.

    Arguments
    ---------
        figure
    A Plotly Figure where to render the plot.

        jumpResult: ssscoring.JumpResults
    A jump results named tuple with score, max speed, scores, data, etc.

        lineColor: str
    A valid CSS color name or hex string.  See SPEED_COLORS for the 8 distinct
    colors used in multi-jump plots.

        legend: str
    Legend label for the main speed trace.

        showIt: bool
    If True, render the max speed marker, horizontal speed, and score brackets.
    Used to discriminate between single-jump plots and aggregate competition
    overlays.

    Streamlit usage:

```python
    graphJumpResult(figure, jumpResult)
    st.plotly_chart(figure, width='stretch')
```
    """
    if jumpResult.data is not None:
        data = jumpResult.data
        scores = jumpResult.scores
        score = jumpResult.score

        # Main speed line
        figure.add_trace(go.Scatter(
            x=data.plotTime,
            y=data.vKMh,
            mode='lines',
            name=legend,
            line=dict(color=lineColor, width=2),
            yaxis='y',
            hovertemplate='v: %{y:.2f} km/h<extra></extra>',
        ))

        if showIt:
            maxSpeed = data.vKMh.max()
            peakSpeedTime = data[data.vKMh == maxSpeed].iloc[0].plotTime

            # Horizontal speed
            figure.add_trace(go.Scatter(
                x=data.plotTime,
                y=data.hKMh,
                mode='lines',
                name='H-speed',
                line=dict(color='red', width=2),
                yaxis='y',
                hovertemplate='h: %{y:.2f} km/h<extra></extra>',
            ))

            _plotSpeedAccuracy(figure, data, jumpResult.window)

            if scores is not None:
                # Score window brackets
                _graphSegment(figure, scores[score]+3.0, 0.0, scores[score]+3.0, score, 1, 'darkseagreen')
                _graphSegment(figure, scores[score],     0.0, scores[score],     score, 1, 'darkseagreen')
                # Score marker
                figure.add_trace(go.Scatter(
                    x=[scores[score]+1.5],
                    y=[score],
                    mode='markers',
                    marker=dict(symbol='circle-cross', size=15,
                                line=dict(color='limegreen', width=2),
                                color='darkgreen'),
                    name='score',
                    yaxis='y',
                    hovertemplate='score: %{y:.2f} km/h<extra></extra>',
                ))
                # Max-speed marker
                figure.add_trace(go.Scatter(
                    x=[peakSpeedTime],
                    y=[maxSpeed],
                    mode='markers',
                    marker=dict(symbol='diamond-dot', size=20,
                                line=dict(color='yellow', width=2),
                                color='red'),
                    name='max speed',
                    yaxis='y',
                    hovertemplate='max: %{y:.2f} km/h<extra></extra>',
                ))


def graphAltitude(figure,
                  jumpResult,
                  label='Alt (ft)',
                  lineColor='palegoldenrod',
                  rangeName='altitudeFt'):
    """
    Graph altitude trace on the dedicated altitudeFt Y axis.
    """
    data = jumpResult.data
    yaxis = _Y_AXIS_MAP[rangeName]
    figure.add_trace(go.Scatter(
        x=data.plotTime,
        y=data.altitudeAGLFt,
        mode='lines',
        name=label,
        line=dict(color=lineColor, width=2),
        yaxis=yaxis,
        hovertemplate='alt: %{y:.0f} ft<extra></extra>',
    ))


def graphAngle(figure,
               jumpResult,
               label='angle',
               lineColor='deepskyblue',
               rangeName='angle'):
    """
    Graph the flight angle trace on the dedicated angle Y axis.
    """
    data = jumpResult.data
    yaxis = _Y_AXIS_MAP[rangeName]
    figure.add_trace(go.Scatter(
        x=data.plotTime,
        y=data.speedAngle,
        mode='lines',
        name=label,
        line=dict(color=lineColor, width=2),
        yaxis=yaxis,
        hovertemplate='angle: %{y:.2f}°<extra></extra>',
    ))


def graphAcceleration(figure,
                      jumpResult,
                      label='V-accel m/s²',
                      lineColor='magenta',
                      rangeName='vAccelMS2'):
    """
    Graph the flight vertical acceleration curve and its EMA-smoothed companion
    on the dedicated vAccelMS2 Y axis.
    """
    data = jumpResult.data
    data['vAccelEMA'] = data.vAccelMS2.ewm(span=20, adjust=False).mean()
    yaxis = _Y_AXIS_MAP[rangeName]
    figure.add_trace(go.Scatter(
        x=data.plotTime,
        y=data.vAccelMS2,
        mode='lines',
        name=label,
        line=dict(color='dimgrey', width=2),
        yaxis=yaxis,
        hovertemplate='a: %{y:.2f} m/s²<extra></extra>',
    ))
    figure.add_trace(go.Scatter(
        x=data.plotTime,
        y=data.vAccelEMA,
        mode='lines',
        name=label + ' (EMA)',
        line=dict(color=lineColor, width=2),
        yaxis=yaxis,
        hovertemplate='a (EMA): %{y:.2f} m/s²<extra></extra>',
    ))


def initializeGroundTrackPlot(jumpTitle: str,
                              height=450,
                              backgroundColorName='#1a1a1a',
                              colorName=DEFAULT_AXIS_COLOR):
    """
    Initialize a Plotly figure for the ground-track plot, configured with equal
    axis scaling so that forward and lateral distances are not distorted.

    X axis: metres forward along the jump run from exit.
    Y axis: metres lateral (left = positive, right = negative).

    Unlike initializePlot(), no extra Y ranges are added — this canvas is
    dedicated to spatial displacement only.

    Arguments
    ---------
        jumpTitle: str
    Figure title, usually the jump tag.

        height: int
    Plot height in pixels.  Default 450 — shorter than the main plot since
    this is a companion chart.

        backgroundColorName: str
    CSS colour name or hex string for the plot and paper background.

        colorName: str
    CSS colour name or hex string for axes, tick labels, and title text.

    Returns
    -------
    A `plotly.graph_objects.Figure` ready to receive graphGroundTrack() traces.
    """
    figure = go.Figure()
    figure.update_layout(
        title=dict(text=jumpTitle, font=dict(color=colorName)),
        height=height,
        autosize=True,
        plot_bgcolor=backgroundColorName,
        paper_bgcolor=backgroundColorName,
        font=dict(color=colorName),
        hovermode='closest',
        showlegend=True,
        legend=dict(font=dict(color=colorName)),
        xaxis=dict(
            title=dict(text='forward (m)', font=dict(color=colorName)),
            autorange=True,
            color=colorName,
            tickfont=dict(color=colorName),
            showgrid=True,
            gridcolor='rgba(255,255,255,0.08)',
            showline=True,
            linecolor=colorName,
            zeroline=True,
            zerolinecolor='rgba(255,255,255,0.25)',
            zerolinewidth=1,
        ),
        yaxis=dict(
            title=dict(text='lateral (m)', font=dict(color=colorName)),
            autorange=True,
            color=colorName,
            tickfont=dict(color=colorName),
            showgrid=True,
            gridcolor='rgba(255,255,255,0.08)',
            showline=True,
            linecolor=colorName,
            zeroline=True,
            zerolinecolor='rgba(255,255,255,0.25)',
            zerolinewidth=1,
            scaleanchor='x',
            scaleratio=1,
        ),
    )
    return figure


def graphGroundTrack(figure,
                     jumpResult,
                     lineColor='deepskyblue'):
    """
    Graph the skydiver's ground track during the performance window as forward
    vs. lateral displacement from exit, with markers coloured by vertical speed.

    X axis = metres forward along the jump run (negative = reversed, i.e. back-
    fall).  Y axis = metres lateral (positive = left of jump run, negative =
    right).  Marker colour encodes vKMh so the speed progression is visible
    without a separate time axis.

    A clean belly-to-earth run produces a smooth rightward curve staying close
    to the lateral zero line.  A back-fall reverses toward the origin; the
    line literally doubles back on itself — unmistakable at a glance.

    Requires a figure initialised by initializeGroundTrackPlot() so that the
    spatial axes are equal-scaled and the zero lines are present.

    Arguments
    ---------
        figure
    A Plotly Figure initialised by initializeGroundTrackPlot().

        jumpResult: ssscoring.JumpResults
    A jump results named tuple.  jumpResult.data must contain latitude,
    longitude, plotTime, and vKMh columns (all present after processJump()).

        lineColor: str
    A valid CSS colour name or hex string for the connecting track line.

    Streamlit usage:

```python
    figure = initializeGroundTrackPlot(tag)
    graphGroundTrack(figure, jumpResult)
    st.plotly_chart(figure, width='stretch')
```
    """
    data = jumpResult.data
    exitLat = float(data.latitude.iloc[0])
    exitLon = float(data.longitude.iloc[0])
    bearing = jumpRunBearing(data)
    displacement = forwardLateralDisplacement(data, exitLat, exitLon, bearing)

    figure.add_trace(go.Scatter(
        x=displacement.forwardM,
        y=displacement.lateralM,
        mode='lines',
        name='track',
        line=dict(color='rgba(255,255,255,0.15)', width=1),
        showlegend=False,
        hoverinfo='skip',
    ))

    figure.add_trace(go.Scatter(
        x=displacement.forwardM,
        y=displacement.lateralM,
        mode='markers',
        name='fwd (m)',
        marker=dict(
            color=displacement.forwardM.clip(lower=0, upper=MAX_HORIZONTAL_DISTANCE),
            colorscale=[
                [0.0, SAFE_HORIZONTAL_COLOR],
                [SAFE_HORIZONTAL_DISTANCE / MAX_HORIZONTAL_DISTANCE, SAFE_HORIZONTAL_COLOR],
                [1.0, UNSAFE_HORIZONTAL_COLOR],
            ],
            cmin=0,
            cmax=MAX_HORIZONTAL_DISTANCE,
            cauto=False,
            size=5,
            showscale=True,
            colorbar=dict(
                title=dict(text='fwd (m)', font=dict(color=DEFAULT_AXIS_COLOR)),
                tickfont=dict(color=DEFAULT_AXIS_COLOR),
                tickvals=[0, SAFE_HORIZONTAL_DISTANCE, MAX_HORIZONTAL_DISTANCE],
                ticktext=['0', f'{int(SAFE_HORIZONTAL_DISTANCE)}m', f'{int(MAX_HORIZONTAL_DISTANCE)}m'],
                thickness=12,
                len=0.75,
            ),
        ),
        hovertemplate='fwd: %{x:.1f} m  lat: %{y:.1f} m<extra></extra>',
    ))

    figure.add_trace(go.Scatter(
        x=[displacement.forwardM.iloc[0]],
        y=[displacement.lateralM.iloc[0]],
        mode='markers',
        name='exit',
        marker=dict(symbol='circle', size=10,
                    color=SAFE_HORIZONTAL_COLOR,
                    line=dict(color='white', width=1)),
        hovertemplate='exit<extra></extra>',
    ))

    figure.add_trace(go.Scatter(
        x=[displacement.forwardM.iloc[-1]],
        y=[displacement.lateralM.iloc[-1]],
        mode='markers',
        name='end',
        marker=dict(symbol='square', size=10,
                    color=UNSAFE_HORIZONTAL_COLOR,
                    line=dict(color='white', width=1)),
        hovertemplate='end: fwd %{x:.1f} m  lat: %{y:.1f} m<extra></extra>',
    ))


def graphForwardDisplacement(figure,
                             jumpResult):
    """
    Graph the forward displacement (metres along the jump run from exit) as a
    time series on the primary Y axis.

    A skydiver on a clean belly run produces a monotonically rising curve.  A
    back-fall inflects and drops — the onset time and reversal depth are
    immediately readable from the shape of the line and the zero reference.

    Markers are coloured by the same green→red gradient used in the ground
    track: SAFE_HORIZONTAL_COLOR up to SAFE_HORIZONTAL_DISTANCE, linear
    transition to UNSAFE_HORIZONTAL_COLOR at MAX_HORIZONTAL_DISTANCE, solid
    red beyond.

    Pair this with graphJumpResult() on a second figure (same plotTime X axis)
    to show the temporal relationship between displacement reversal and speed
    loss.

    Arguments
    ---------
        figure
    A Plotly Figure initialised by initializePlot() with xLabel='seconds from
    exit' and yLabel='forward (m)'.

        jumpResult: ssscoring.JumpResults
    A jump results named tuple.  jumpResult.data must contain latitude,
    longitude, and plotTime (all present after processJump()).

    Streamlit usage:

```python
    figure = initializePlot(tag, yLabel='forward (m)', backgroundColorName='#2c2c2c')
    graphForwardDisplacement(figure, jumpResult)
    st.plotly_chart(figure, width='stretch')
```
    """
    data = jumpResult.data
    exitLat = float(data.latitude.iloc[0])
    exitLon = float(data.longitude.iloc[0])
    bearing = jumpRunBearing(data)
    displacement = forwardLateralDisplacement(data, exitLat, exitLon, bearing)

    figure.add_trace(go.Scatter(
        x=displacement.plotTime,
        y=displacement.forwardM,
        mode='lines',
        line=dict(color='rgba(255,255,255,0.15)', width=1),
        showlegend=False,
        hoverinfo='skip',
    ))

    figure.add_trace(go.Scatter(
        x=displacement.plotTime,
        y=displacement.forwardM,
        mode='markers',
        name='fwd (m)',
        marker=dict(
            color=displacement.forwardM.clip(lower=0, upper=MAX_HORIZONTAL_DISTANCE),
            colorscale=[
                [0.0, SAFE_HORIZONTAL_COLOR],
                [SAFE_HORIZONTAL_DISTANCE / MAX_HORIZONTAL_DISTANCE, SAFE_HORIZONTAL_COLOR],
                [1.0, UNSAFE_HORIZONTAL_COLOR],
            ],
            cmin=0,
            cmax=MAX_HORIZONTAL_DISTANCE,
            cauto=False,
            size=4,
            showscale=True,
            colorbar=dict(
                title=dict(text='fwd (m)', font=dict(color=DEFAULT_AXIS_COLOR)),
                tickfont=dict(color=DEFAULT_AXIS_COLOR),
                tickvals=[0, SAFE_HORIZONTAL_DISTANCE, MAX_HORIZONTAL_DISTANCE],
                ticktext=['0', f'{int(SAFE_HORIZONTAL_DISTANCE)}m', f'{int(MAX_HORIZONTAL_DISTANCE)}m'],
                thickness=12,
                len=0.75,
            ),
        ),
        yaxis='y',
        hovertemplate='t: %{x:.1f} s  fwd: %{y:.1f} m<extra></extra>',
    ))

    figure.add_trace(go.Scatter(
        x=[displacement.plotTime.iloc[0], displacement.plotTime.iloc[-1]],
        y=[0.0, 0.0],
        mode='lines',
        line=dict(color='rgba(255,255,255,0.25)', width=1, dash='dot'),
        showlegend=False,
        hoverinfo='skip',
    ))


def resolveJumpColors(jumpResults: dict) -> dict:
    """
    Build a tag→hex-color mapping for a set of jump results.

    The fastest jump (highest score) gets `COLOR_FASTEST`, the slowest gets
    `COLOR_SLOWEST`, and all remaining valid jumps cycle through `COLORS_OTHERS`.
    """
    validScores = {
        tag: jumpResult.score
        for tag, jumpResult in jumpResults.items()
        if jumpResult.score is not None
    }
    if not validScores:
        return {
            tag: COLORS_OTHERS[i % len(COLORS_OTHERS)]
            for i, tag in enumerate(jumpResults)
        }
    fastestTag = max(validScores, key=validScores.get)
    slowestTag = min(validScores, key=validScores.get)
    tagColors = {}
    blueIndex = 0
    for tag in jumpResults:
        if tag == fastestTag:
            tagColors[tag] = COLOR_FASTEST
        elif tag == slowestTag:
            tagColors[tag] = COLOR_SLOWEST
        else:
            tagColors[tag] = COLORS_OTHERS[blueIndex % len(COLORS_OTHERS)]
            blueIndex += 1
    return tagColors


def convertHexColorToRGB(color: str) -> list:
    """
    Converts a color in the format `#a0b1c2` to its RGB equivalent as a list
    of three values 0-255.
    """
    if not isinstance(color, str):
        raise TypeError('Invalid color type - must be str')
    color = color.replace('#', '')
    if len(color) != 6:
        raise SSScoringError('Invalid hex value length')
    rgbValues = [int(color[byteOffset:byteOffset+2], 16) for byteOffset in range(0, len(color), 2)]
    return rgbValues

