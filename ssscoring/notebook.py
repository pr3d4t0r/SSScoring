# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt
"""
## Utility reusable code for notebooks.
"""


import bokeh.plotting as bp
import ipywidgets as widgets
import pandas as pd

# *** constants ***
DATA_LAKE_ROOT = './data' # Lucyfer default
SPEED_COLORS = colors = ('blue', 'limegreen', 'tomato', 'turquoise', 'deepskyblue', 'forestgreen', 'coral', 'darkcyan',)


# *** global initialization ***

bp.output_notebook(hide_banner = True)


# *** functions ***

def initializePlot(jumpTitle: str,
                   height = 500,
                   width = 900,
                   xLabel = 'seconds from exit',
                   yLabel = 'km/h',
                   xMax = 40.0,
                   yMax = 550.0):
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
    """
    return bp.figure(title = jumpTitle,
                     height = height,
                     width = width,
                     x_axis_label = xLabel,
                     y_axis_label = yLabel,
                     x_range = (0.0, xMax),
                     y_range = (0.0, yMax))


def _graphSegment(plot,
                  x0 = 0.0,
                  y0 = 0.0,
                  x1 = 0.0,
                  y1 = 0.0,
                  lineWidth = 1,
                  color = 'black'):
    plot.segment(x0 = [ x0, ],
                 y0 = [ y0, ],
                 x1 = [ x1, ],
                 y1 = [ y1, ],
                 line_width = lineWidth,
                 color = color)


def graphJumpResult(plot,
                    jumpResult,
                    lineColor = 'green',
                    legend = 'speed',
                    showIt = True):
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

        leged: str
    A title for the plot.

        showIt: bool
    A boolean flag for whether the call should render the plot upon the function
    call.  This flag is used for combining two or more jumps on the same plot.
    In that case, a call to this function is made with a different `jumpResult`
    and the `showIt` flag set to `False`.  When the user is ready to view the
    combined plot, issue a call to `bp.show(plot)`.  Example:

    ```python
    for result in jumpResults:
        graphJumpResult(plot, result, showIt = False)

    bp.show(plot)

    Returns
    -------
    `None`.
    ```
    """
    data = jumpResult.data
    scores = jumpResult.scores
    score = jumpResult.score
    plot.line(data.plotTime, data.vKMh, legend_label = legend, line_width = 2, line_color = lineColor)

    if showIt:
        _graphSegment(plot, scores[score], 0.0, scores[score], score, 3, 'green')
        _graphSegment(plot, scores[score]+1.5, 0.0, scores[score]+1.5, score, 1, 'darkseagreen')
        _graphSegment(plot, scores[score]-1.5, 0.0, scores[score]-1.5, score, 1, 'darkseagreen')
        plot.square_cross(x = [ scores[score], ], y = [ score, ], size = [ 20, ], line_color = 'green', fill_color = None, line_width = 3)
        # TODO:  Decide whether to use any of these to show the scoring point in
        #        the plot.  They all have advantages and drawbacks.
        # plot.triangle_dot(x = [ scores[score], ], y = [ score, ], size = [ 20, ], line_color = 'green', fill_color = None, line_width = 3)
        # plot.y(x = [ scores[score], ], y = [ score, ], size = [ 20, ], line_color = 'green', line_width = 3)
        bp.show(plot)

