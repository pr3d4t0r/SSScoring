# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

"""
## Utility reusable code for notebooks.
"""

from ssscoring.constants import DEFAULT_PLOT_MAX_V_SCALE
from ssscoring.constants import DEFAULT_SPEED_ACCURACY_SCALE
from ssscoring.constants import MAX_ALTITUDE_FT
from ssscoring.constants import SPEED_ACCURACY_THRESHOLD
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
    fig = go.Figure()
    fig.update_layout(
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
    return fig


def _graphSegment(fig,
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
    fig.add_shape(
        type='line',
        x0=x0, y0=y0,
        x1=x1, y1=y1,
        line=dict(color=color, width=lineWidth),
        xref='x', yref='y',
    )


def initializeExtraYRanges(fig,
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

    fig.update_xaxes(domain=(LEFT_MARGIN, 1.0))

    mainYTitle = (fig.layout.yaxis.title.text or 'km/h')
    fig.update_yaxes(title=None)

    fig.update_layout(
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
        fig.add_annotation(
            xref='paper', yref='paper',
            x=pos + 0.012, y=0.5,
            text=text,
            showarrow=False,
            textangle=-90,
            font=dict(color=color, size=11),
            xanchor='center', yanchor='middle',
        )

    return fig


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


def _plotSpeedAccuracy(fig, data, window):
    accuracyData = validationWindowDataFrom(data, window)
    fig.add_trace(go.Scatter(
        x=accuracyData['x'],
        y=accuracyData['y'],
        mode='lines',
        name='Speed accuracy ISC',
        line=dict(color='lime', width=5.0),
        yaxis='y5',
        hovertemplate='accuracy: %{y:.2f}<extra></extra>',
    ))
    validationData = data[data.altitudeAGL <= window.validationStart]
    fig.add_trace(go.Scatter(
        x=validationData.plotTime,
        y=[SPEED_ACCURACY_THRESHOLD] * len(validationData),
        mode='lines',
        line=dict(color='lime', width=1.0, dash='dash'),
        yaxis='y5',
        showlegend=False,
        hoverinfo='skip',
    ))


def graphJumpResult(fig,
                    jumpResult,
                    lineColor='green',
                    legend='speed',
                    showIt=True,
                    showAccuracy=True):
    """
    Graph the jump results onto the initialized Plotly figure.

    Arguments
    ---------
        fig
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
    graphJumpResult(fig, result)
    st.plotly_chart(fig, use_container_width=True)
```
    """
    # TODO: Fix this in the documentation ⬆️
    if jumpResult.data is not None:
        data = jumpResult.data
        scores = jumpResult.scores
        score = jumpResult.score

        # Main speed line
        fig.add_trace(go.Scatter(
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
            t = data[data.vKMh == maxSpeed].iloc[0].plotTime

            # Horizontal speed
            fig.add_trace(go.Scatter(
                x=data.plotTime,
                y=data.hKMh,
                mode='lines',
                name='H-speed',
                line=dict(color='red', width=2),
                yaxis='y',
                hovertemplate='h: %{y:.2f} km/h<extra></extra>',
            ))

            _plotSpeedAccuracy(fig, data, jumpResult.window)

            if scores is not None:
                # Score window brackets
                _graphSegment(fig, scores[score]+3.0, 0.0, scores[score]+3.0, score, 1, 'darkseagreen')
                _graphSegment(fig, scores[score],     0.0, scores[score],     score, 1, 'darkseagreen')
                # Score marker
                fig.add_trace(go.Scatter(
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
                fig.add_trace(go.Scatter(
                    x=[t],
                    y=[maxSpeed],
                    mode='markers',
                    marker=dict(symbol='diamond-dot', size=20,
                                line=dict(color='yellow', width=2),
                                color='red'),
                    name='max speed',
                    yaxis='y',
                    hovertemplate='max: %{y:.2f} km/h<extra></extra>',
                ))


def graphAltitude(fig,
                  jumpResult,
                  label='Alt (ft)',
                  lineColor='palegoldenrod',
                  rangeName='altitudeFt'):
    """
    Graph altitude trace on the dedicated altitudeFt Y axis.
    """
    data = jumpResult.data
    yaxis = _Y_AXIS_MAP[rangeName]
    fig.add_trace(go.Scatter(
        x=data.plotTime,
        y=data.altitudeAGLFt,
        mode='lines',
        name=label,
        line=dict(color=lineColor, width=2),
        yaxis=yaxis,
        hovertemplate='alt: %{y:.0f} ft<extra></extra>',
    ))


def graphAngle(fig,
               jumpResult,
               label='angle',
               lineColor='deepskyblue',
               rangeName='angle'):
    """
    Graph the flight angle trace on the dedicated angle Y axis.
    """
    data = jumpResult.data
    yaxis = _Y_AXIS_MAP[rangeName]
    fig.add_trace(go.Scatter(
        x=data.plotTime,
        y=data.speedAngle,
        mode='lines',
        name=label,
        line=dict(color=lineColor, width=2),
        yaxis=yaxis,
        hovertemplate='angle: %{y:.2f}°<extra></extra>',
    ))


def graphAcceleration(fig,
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
    fig.add_trace(go.Scatter(
        x=data.plotTime,
        y=data.vAccelMS2,
        mode='lines',
        name=label,
        line=dict(color='dimgrey', width=2),
        yaxis=yaxis,
        hovertemplate='a: %{y:.2f} m/s²<extra></extra>',
    ))
    fig.add_trace(go.Scatter(
        x=data.plotTime,
        y=data.vAccelEMA,
        mode='lines',
        name=label + ' (EMA)',
        line=dict(color=lineColor, width=2),
        yaxis=yaxis,
        hovertemplate='a (EMA): %{y:.2f} m/s²<extra></extra>',
    ))


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
    result = [int(color[x:x+2], 16) for x in range(0, len(color), 2)]
    return result

