# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

"""
## Utility reusable code for notebooks.
"""


from ssscoring.constants import DEFAULT_SPEED_ACCURACY_SCALE
from ssscoring.constants import MAX_ALTITUDE_FT
from ssscoring.constants import SPEED_ACCURACY_THRESHOLD
from ssscoring.datatypes import PerformanceWindow

import bokeh.io as bi
import bokeh.models as bm
import bokeh.plotting as bp
import pandas as pd


# *** constants ***

DEFAULT_AXIS_COLOR_BOKEH = 'lightsteelblue'
"""
CSS color name for the axis colors used in notebooks and Streamlit
with Bokeh.
"""


SPEED_COLORS = colors = ('limegreen', 'blue', 'tomato', 'turquoise', 'deepskyblue', 'forestgreen', 'coral', 'darkcyan',)
"""
Colors used for tracking the lines in a multi-jump plot, so that each track is
associated with a different color and easier to visualize.  8 distinct colors,
corresponding to each jump in a competition.
"""


# *** global initialization ***

# bp.output_notebook(hide_banner = True)
bp.output_file('/dev/null', mode='inline')
# TODO: make this configurable:
bi.curdoc().theme = 'dark_minimal'


# *** functions ***

def initializePlot(jumpTitle: str,
                   height=500,
                   width=900,
                   xLabel='seconds from exit',
                   yLabel='km/h',
                   xMax=35.0,
                   yMax=550.0,
                   backgroundColorName='#1a1a1a',
                   colorName=DEFAULT_AXIS_COLOR_BOKEH):
    """
    Initiialize a plotting area for notebook output.

    Arguments
    ---------
        jumpTitle: str
    A title to identify the plot.

        height: int
    Height of the plot in pixels.  Default = 500.

        width: int
    Width of the plot in pixels.  Default = 900.

        xLabel: str
    X axis label.  Default:  `'seconds from exit'`

        yLabel: str
    Y axis label.  Default:  `'km/h'`

        xMax: float
    The maximum rnage for the X axis.  Default = 40.0

        yMax: float
    The maximum range for the Y axis.  Default = 550

        backgroundColorName
    A string with the CSS RGB value of the background color or its CSS color
    string name.

        colorName
    A valid CSS color string.
    """
    bi.curdoc().theme = 'dark_minimal'
    plot = bp.figure(title=jumpTitle,
                     height=height,
                     width=width,
                     x_axis_label=xLabel,
                     y_axis_label=yLabel,
                     x_range=(0.0, xMax),
                     y_range=(0.0, yMax),
                     background_fill_color=backgroundColorName,
                     border_fill_color=backgroundColorName)
    plot.xaxis.axis_label_text_color=colorName
    plot.xaxis.major_label_text_color=colorName
    plot.xaxis.axis_line_color=colorName
    plot.xaxis.major_tick_line_color=colorName
    plot.xaxis.minor_tick_line_color=colorName
    plot.yaxis.axis_label_text_color=colorName
    plot.yaxis.major_label_text_color=colorName
    plot.yaxis.axis_line_color=colorName
    plot.yaxis.major_tick_line_color=colorName
    plot.yaxis.minor_tick_line_color=colorName
    plot.title.text_color = colorName
    return plot


def _graphSegment(plot,
                  x0=0.0,
                  y0=0.0,
                  x1=0.0,
                  y1=0.0,
                  lineWidth=1,
                  color='black'):
    plot.segment(x0=[ x0, ],
                 y0=[ y0, ],
                 x1=[ x1, ],
                 y1=[ y1, ],
                 line_width=lineWidth,
                 color=color)


def _initLinearAxis(label: str,
                    rangeName: str,
                    colorName: str=DEFAULT_AXIS_COLOR_BOKEH) -> bm.LinearAxis:
    """
    Make a linear initialized to use standard colors with Bokeh plots.

    Arguments
    ---------

        label: str
    The axis label, text string.

        rangeName
    The range name, often used for specifying the measurment units.

        colorName
    A valid CSS color string.

    Return
    ------
    An instance of `bokeh.models.LinearAxis`.
    """
    linearAxis = bm.LinearAxis(
            axis_label = label,
            axis_label_text_color = colorName,
            axis_line_color = colorName,
            major_label_text_color = colorName,
            major_tick_line_color=colorName,
            minor_tick_line_color=colorName,
            y_range_name = rangeName,
    )
    return linearAxis


def initializeExtraYRanges(plot,
                           startY: float = 0.0,
                           endY: float = MAX_ALTITUDE_FT,
                           maxSpeedAccuracy: float | None = None):
    """
    Initialize an extra Y range for reporting other data trend (e.g. altitude)
    in the plot.

    Arguments
    ---------
        plot
    A valid instance of `bp.figure` with an existing plot defined for it

        startY: float
    The Y range starting value

        endY: float
    The Y range ending value

        maxSpeedAccuracy: float
    Maximum speed accuracy value to determine the range of the speed accuracy axis.
    If None or < SPEED_ACCURACY_THRESHOLD, range is 0-10. Otherwise, range is 0-maxSpeedAccuracy*1.1

    Returns
    -------
    An instance of `bp.figure` updated to report an additional Y axis.
    """
    speedAccuracyEnd = DEFAULT_SPEED_ACCURACY_SCALE
    if maxSpeedAccuracy is not None and maxSpeedAccuracy >= SPEED_ACCURACY_THRESHOLD:
        speedAccuracyEnd = maxSpeedAccuracy * 1.1
    plot.extra_y_ranges = {
        'altitudeFt': bm.Range1d(start = startY, end = endY),
        'angle': bm.Range1d(start = 0.0, end = 90.0),
        'speedAccuracy': bm.Range1d(start = 0.0, end = speedAccuracyEnd),
    }
    plot.add_layout(_initLinearAxis('Alt (ft)', 'altitudeFt', colorName=DEFAULT_AXIS_COLOR_BOKEH), 'left')
    plot.add_layout(_initLinearAxis('angle', 'angle', colorName=DEFAULT_AXIS_COLOR_BOKEH), 'left')
    plot.add_layout(_initLinearAxis('Speed accuracy ISC', 'speedAccuracy', colorName=DEFAULT_AXIS_COLOR_BOKEH), 'left')
    return plot


def validationWindowDataFrom(data: pd.DataFrame, window: PerformanceWindow) -> bm.ColumnDataSource:
    """
    Generate the validation window dataset for plotting the ISC speed accuracy
    values.  It's a subset defined from the end of the scoring window to the
    validation start.

    Arguments
    ---------
        data
    A dataframe with the `plotTime` column set, with all the jump data, after
    speed validation processing.

        window
    A `ssscoring.datatypes.PerformanceWindow` instance, with the `validationStart`
    value initialized.

    Returns
    -------
    A column data source ready for plotting the Y-values of a Bokeh chart.
    """
    validationData = data[data.altitudeAGL <= window.validationStart]
    return bm.ColumnDataSource({ 'x': validationData.plotTime, 'y': validationData.speedAccuracyISC, })


def _plotSpeedAccuracy(plot, data, window):
    accuracyDataSource = validationWindowDataFrom(data, window)
    plot.line('x', 'y', y_range_name='speedAccuracy', legend_label='Speed accuracy ISC', line_width=5.0, line_color='lime', source=accuracyDataSource)

    validationData = data[data.altitudeAGL <= window.validationStart]
    plot.line(x = validationData.plotTime, y = pd.Series([ SPEED_ACCURACY_THRESHOLD, ]*len(validationData)), y_range_name='speedAccuracy', line_dash='dashed', line_color='lime', line_width=1.0)


def graphJumpResult(plot,
                    jumpResult,
                    lineColor = 'green',
                    legend = 'speed',
                    showIt = True,
                    showAccuracy = True):
    """
    Graph the jump results using the initialized plot.

    Arguments
    ---------
        plot: bp.figure
    A Bokeh figure where to render the plot.

        jumpResult: ssscoring.JumpResults
    A jump results named tuple with score, max speed, scores, data, etc.

        lineColor: str
    A valid color from the Bokeh palette:  https://docs.bokeh.org/en/2.1.1/docs/reference/colors.html
    This module defines 8 colors for rendering a competition's results.  See:
    `ssscoring.notebook.SPEED_COLORS` for the list.

        legend: str
    A title for the plot.

        showIt: bool
    A boolean flag for whether the call should render the max speed, time,
    horizontal speed, etc. in the current plot.  This is used for discriminating
    between single jump plots and plotting only the speed for the aggregate
    plot display for a competition or training session.

    To display the actual plot, use `bp.show(plot)` if running from Lucyfer/Jupyter
    or use `st.bokeh_chart(plot)` if in the Streamlit environment.

    ```python
    # Basic usage showing speed accuracy overlay
    graphJumpResult(plot, result)
    bp.show(plot)

    # Multiple jumps without speed accuracy overlay
    for result in jumpResults:
        graphJumpResult(plot, result, showIt=False, showAccuracy=False)
    bp.show(plot)
    ```
    Another alternative use is in Streamlit.io applications:

    ```python
    # Streamlit app with speed accuracy overlay
    graphJumpResult(plot, result, showIt=False)
    st.bokeh_chart(plot, use_container_width=True)
    ```

    Returns
    -------
    `None`.
    """
    data = jumpResult.data
    scores = jumpResult.scores
    score = jumpResult.score
    # Main speed line
    plot.line(data.plotTime, data.vKMh, legend_label = legend, line_width = 2, line_color = lineColor)

    if showIt:
        plot.line(data.plotTime, data.hKMh, legend_label = 'H-speed', line_width = 2, line_color = 'red')
        _plotSpeedAccuracy(plot, data, jumpResult.window)
        _graphSegment(plot, scores[score], 0.0, scores[score], score, 3, 'lightblue')
        _graphSegment(plot, scores[score]+1.5, 0.0, scores[score]+1.5, score, 1, 'darkseagreen')
        _graphSegment(plot, scores[score]-1.5, 0.0, scores[score]-1.5, score, 1, 'darkseagreen')
        plot.scatter(x = [ scores[score], ], y = [ score, ], marker = 'square_cross', size = [ 20, ], line_color = 'lightblue', fill_color = None, line_width = 3)


def graphAltitude(plot,
                  jumpResult,
                  label = 'Alt (ft)',
                  lineColor = 'palegoldenrod',
                  rangeName = 'altitudeFt'):
    """
    Graph a vertical axis with additional data, often used for altitude in ft
    ASL.

    Arguments
    ---------
        plot: pb.figure
    A Bokeh figure where to render the plot.

        jumpResult: ssscoring.JumpResults
    A jump results named tuple with score, max speed, scores, data, etc.

        label: str
    The legend label for the new Y axis.

        lineColor: str
    A color name from the Bokeh palette.

        rangeName: str
    The range name to associate the `LinearAxis` layout with the data for
    plotting.

    Returns
    -------
    `None`.
    """
    data = jumpResult.data
    plot.line(data.plotTime, data.altitudeAGLFt, legend_label = label, line_width = 2, line_color = lineColor, y_range_name = rangeName)


def graphAngle(plot,
               jumpResult,
               label = 'angle',
               lineColor = 'deepskyblue',
               rangeName = 'angle'):
    """
    Graph the flight angle

    Arguments
    ---------
        plot: pb.figure
    A Bokeh figure where to render the plot.

        jumpResult: ssscoring.JumpResults
    A jump results named tuple with score, max speed, scores, data, etc.

        label: str
    The legend label for the new Y axis.

        lineColor: str
    A color name from the Bokeh palette.

        rangeName: str
    The range name to associate the `LinearAxis` layout with the data for
    plotting.

    Returns
    -------
    `None`.
    """
    data = jumpResult.data
    plot.line(data.plotTime, data.speedAngle, legend_label = label, line_width = 2, line_color = lineColor, y_range_name = rangeName)

