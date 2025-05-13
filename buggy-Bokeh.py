# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txtl

# Streamlit Bokeh bug report runner


import bokeh.models as bm
import bokeh.plotting as bp
import streamlit as st

backgroundColorName='#2c2c2c'
colorName = 'lightsteelblue'
THEME='caliber'
x = [ x for x in range(1,6) ]
y = [ 6, 7, 6, 4, 5, ]


def BUG_st_bokeh():
    # REQUIRES: pip install streamlit_bokeh
    from streamlit_bokeh import streamlit_bokeh

    plot = bp.figure(
                title='TICK MARKS MISSING - theme: %s' % THEME,
                width=500,
                height=300,
                background_fill_color=backgroundColorName,
                border_fill_color=backgroundColorName,
    )
    plot.title.text_font = 'Arial'
    plot.title.text_color = 'red'
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
    plot.line(x, y, line_color='orange')
    linearAxis = bm.LinearAxis(
            axis_label_text_color = colorName,
            axis_line_color = colorName,
            major_label_text_color = colorName,
            axis_label = 'Foo',
            major_tick_line_color='yellow',
            minor_tick_line_color='yellow',
            y_range_name = 'Bar'
    )
    plot.extra_y_ranges = { 'Bar': bm.Range1d(start = 0, end = 10) }
    plot.add_layout(linearAxis, 'left')
    streamlit_bokeh(plot, use_container_width=False, theme=THEME)


def WORKS_st_bokeh_chart():
    # REQUIRES: pip install bokeh==2.4.3
    import bokeh.io as bi

    bi.curdoc.theme = THEME
    plot = bp.figure(
                title='TICK MARKS SHOW - theme: %s' % THEME,
                width=500,
                height=300,
                background_fill_color=backgroundColorName,
                border_fill_color=backgroundColorName,
    )
    plot.title.text_font = 'Arial'
    plot.title.text_color = colorName
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
    plot.line(x, y, line_color='orange')
    linearAxis = bm.LinearAxis(
            axis_label_text_color = colorName,
            axis_line_color = colorName,
            major_label_text_color = colorName,
            axis_label = 'Foo',
            major_tick_line_color='yellow',
            minor_tick_line_color='yellow',
            y_range_name = 'Bar'
    )
    plot.extra_y_ranges = { 'Bar': bm.Range1d(start = 0, end = 10) }
    plot.add_layout(linearAxis, 'left')
    st.bokeh_chart(plot, use_container_width=False)


if '__main__' == __name__:
    WORKS_st_bokeh_chart()
    # BUG_st_bokeh()

