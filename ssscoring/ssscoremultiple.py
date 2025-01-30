# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt

"""
## Experimental

Process a group of jumps uploaded from a file uploader.
"""

# from ssscoring.appcommon import initDropZonesFromObject
from ssscoring import __VERSION__
from ssscoring.appcommon import DZ_DIRECTORY
from ssscoring.appcommon import displayJumpDataIn
from ssscoring.appcommon import initDropZonesFromResource
from ssscoring.appcommon import interpretJumpResult
from ssscoring.appcommon import isStreamlitHostedApp
from ssscoring.appcommon import plotJumpResult
from ssscoring.calc import aggregateResults
from ssscoring.calc import processAllJumpFiles
from ssscoring.calc import totalResultsFrom
from ssscoring.datatypes import JumpStatus
from ssscoring.mapview import speedJumpTrajectory
from ssscoring.notebook import SPEED_COLORS
from ssscoring.notebook import graphJumpResult
from ssscoring.notebook import initializePlot

import pandas as pd
import streamlit as st


# +++ implementation +++

def _setSideBarAndMain():
    dropZones = initDropZonesFromResource(DZ_DIRECTORY)
    st.sidebar.title('🔢 SSScore %s β' % __VERSION__)
    st.session_state.processBadJump = st.sidebar.checkbox('Process bad jumps', value=True, help='Display results from invalid jumps')
    dropZone = st.sidebar.selectbox('Select drop zone:', dropZones.dropZone, index=None)
    if dropZone:
        st.session_state.elevation = dropZones[dropZones.dropZone == dropZone ].iloc[0].elevation
    else:
        st.session_state.elevation = None
        st.session_state.trackFiles = None
    st.sidebar.metric('Elevation', value='%.1f m' % (0.0 if st.session_state.elevation == None else st.session_state.elevation))
    st.session_state.trackFiles = st.sidebar.file_uploader(
        'Track files',
        [ 'CSV' ],
        disabled=st.session_state.elevation == None,
        accept_multiple_files=True
    )
# TODO: Refine this to clear the cache AND the file_uploader() selections:
#     if st.sidebar.button('Clear') and 'trackFiles' in st.session_state.keys():
#         st.session_state.pop('trackFile')
#         st.experimental_rerun()
    st.sidebar.html("<a href='https://github.com/pr3d4t0r/SSScoring/issues/new?template=Blank+issue' target='_blank'>Make a bug report or feature request</a>")


def _styleShowMaxIn(scores: pd.Series) -> pd.DataFrame:
    return [
        'background-color: mediumseagreen' if v == scores.max() else \
        '' for v in scores ]


def _styleShowMinMaxIn(scores: pd.Series) -> pd.DataFrame:
    return [
        'background-color: green' if v == scores.max() else \
        'background-color: orangered' if v == scores.min() else \
        '' for v in scores ]


def main():
    if not isStreamlitHostedApp():
        st.set_page_config(layout = 'wide')
    _setSideBarAndMain()

    col0, col1 = st.columns([0.5, 0.5, ])
    if st.session_state.trackFiles:
        jumpResults = processAllJumpFiles(st.session_state.trackFiles, altitudeDZMeters=st.session_state.elevation)
        allJumpsPlot = initializePlot('All jumps', backgroundColorName='#2c2c2c')
        mixColor = 0
        jumpResultsSubset = dict()
        for tag in sorted(list(jumpResults.keys())):
            jumpResult = jumpResults[tag]
            mixColor = (mixColor+1)%len(SPEED_COLORS)
            with col1:
                jumpStatusInfo,\
                scoringInfo,\
                badJumpLegend,\
                jumpStatus = interpretJumpResult(tag, jumpResult, st.session_state.processBadJump)
                if jumpStatus == JumpStatus.OK:
                    jumpResultsSubset[tag] = jumpResult
                st.html('<hr><h3>'+jumpStatusInfo+scoringInfo+(badJumpLegend if badJumpLegend else '')+'</h3>')
                if jumpStatus == JumpStatus.OK:
                    displayJumpDataIn(jumpResult.table)
                    plotJumpResult(tag, jumpResult)
                    graphJumpResult(
                        allJumpsPlot,
                        jumpResult,
                        lineColor=SPEED_COLORS[mixColor],
                        legend='%s = %.2f' % (tag, jumpResult.score),
                        showIt=False
                    )
                    st.write('Brightest point corresponds to the max speed')
                    st.pydeck_chart(speedJumpTrajectory(jumpResult))
        with col0:
            aggregate = aggregateResults(jumpResultsSubset)
            st.html('<h2>Jumps in this set</h2>')
            displayAggregate = aggregate.style.apply(_styleShowMinMaxIn, subset=[ 'score', ]).apply(_styleShowMaxIn, subset=[ 'maxSpeed', ]).format(precision=2)
            st.dataframe(displayAggregate)
            st.html('<h2>Summary</h2>')
            st.dataframe(totalResultsFrom(aggregate), hide_index = True)
            if jumpStatus == JumpStatus.OK:
                st.bokeh_chart(allJumpsPlot, use_container_width=True)


if '__main__' == __name__:
    main()

