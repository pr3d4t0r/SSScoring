# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txtl

"""
## Experimental

Process a group of jumps uploaded from a file uploader.
"""

from ssscoring.appcommon import displayJumpDataIn
from ssscoring.appcommon import displayTrackOnMap
from ssscoring.appcommon import initFileUploaderState
from ssscoring.appcommon import interpretJumpResult
from ssscoring.appcommon import isStreamlitHostedApp
from ssscoring.appcommon import plotJumpResult
from ssscoring.appcommon import setSideBarAndMain
from ssscoring.calc import aggregateResults
from ssscoring.calc import processAllJumpFiles
from ssscoring.calc import totalResultsFrom
from ssscoring.datatypes import JumpStatus
# from ssscoring.mapview import multipleSpeedJumpsTrajectories
from ssscoring.mapview import speedJumpTrajectory
from ssscoring.notebook import SPEED_COLORS
from ssscoring.notebook import graphJumpResult
from ssscoring.notebook import initializePlot
from ssscoring.constants import M_2_FT
from ssscoring.calc import dropNonSkydiveDataFrom
from ssscoring.datatypes import PerformanceWindow
from ssscoring.constants import SPEED_ACCURACY_THRESHOLD

import pandas as pd
import streamlit as st


# +++ implementation +++

def _selectDZState(*args, **kwargs):
    if st.session_state.elevation:
        st.session_state.uploaderKey += 1
        st.session_state.trackFiles = None


def _styleShowMaxIn(scores: pd.Series) -> pd.DataFrame:
    return [
        'background-color: mediumseagreen' if v == scores.max() else \
        '' for v in scores ]


def _displayAllJumpDataIn(data: pd.DataFrame):
    if data is not None:
        columns = [ 'plotTime' ] + [ column for column in data.columns if column != 'plotTime' and column != 'timeUnix' ]
        st.html('<h3>All jump data from exit</h3>')
        st.dataframe(data,
            column_order=columns,
            column_config={
                'plotTime': st.column_config.NumberColumn(format='%.02f'),
                'speedAngle': st.column_config.NumberColumn(format='%.02f'),
                'speedAccuracyISC': st.column_config.NumberColumn(format='%.02f'),
            },
            hide_index=True)


def _displayScoresIn(rawData: dict):
    if rawData is not None:
        st.html('<h3>All 3-sec sliding window scores</h3>')
        data = pd.DataFrame.from_dict({ 'time': rawData.values(), 'score': rawData.keys(), })
        data.time = data.time.apply(lambda x: '%.2f' % x)
        st.dataframe(data, hide_index=True)


def _displayBadRowsISCAccuracyExceeded(data: pd.DataFrame, window: PerformanceWindow):
    badRows = data[data.speedAccuracyISC >= SPEED_ACCURACY_THRESHOLD]
    badRows = dropNonSkydiveDataFrom(badRows)
    times = pd.to_datetime(badRows.timeUnix, unit='s').dt.strftime('%Y-%m-%d %H:%M:%S.%f').str[:-4]
    badRows.insert(0, 'time', times)
    badRows.drop(columns = [
        'timeUnix',
        'altitudeMSL',
        'altitudeMSLFt',
        'speedAccuracy',
        'hMetersPerSecond',
        'hKMh',
        'speedAngle',
        'latitude',
        'longitude',
        'verticalAccuracy', ], inplace=True)
    st.html('<h3>Performance window:<br>start = %.2f m (%.2f ft)<br>end = %.2f m (%.2f ft)<br>validation start = %.2f m (%.2f ft)</h3>' % \
                    (window.start, M_2_FT*window.start, window.end, M_2_FT*window.end, window.validationStart, M_2_FT*window.validationStart))
    st.html('<h3>%d track rows where the ISC speed accuracy threshold was exceeded during the speed run:</h3>' % len(badRows))
    st.dataframe(badRows, hide_index=True)


    workData = data.copy()
    workData = dropNonSkydiveDataFrom(workData)
    times = pd.to_datetime(workData.timeUnix, unit='s').dt.strftime('%Y-%m-%d %H:%M:%S.%f').str[:-4]
    workData.insert(0, 'time', times)
    st.html('<h3>Full speed run data (%d rows)</h3>' % len(workData))
    st.dataframe(workData, hide_index=True)


def _styleShowMinMaxIn(scores: pd.Series) -> pd.DataFrame:
    return [
        'background-color: green' if v == scores.max() else \
        'background-color: orangered' if v == scores.min() else \
        '' for v in scores ]


def main():
    if not isStreamlitHostedApp():
        st.set_page_config(layout = 'wide')
    initFileUploaderState('trackFiles')
    setSideBarAndMain('🔢', False, _selectDZState)

    if st.session_state.trackFiles:
        jumpResults = processAllJumpFiles(st.session_state.trackFiles, altitudeDZMeters=st.session_state.elevation)
        allJumpsPlot = initializePlot('All jumps', backgroundColorName='#2c2c2c')
        mixColor = 0
        jumpResultsSubset = dict()
        resultTags = sorted(list(jumpResults.keys()), reverse=True)
        tabs = st.tabs(['Totals']+resultTags)
        index = 1
        jumpStatus = JumpStatus.OK
        for tag in resultTags:
            jumpResult = jumpResults[tag]
            mixColor = (mixColor+1)%len(SPEED_COLORS)
            with tabs[index]:
                jumpStatusInfo,\
                scoringInfo,\
                badJumpLegend,\
                jumpStatus = interpretJumpResult(tag, jumpResult, st.session_state.processBadJump)
                if jumpStatus != JumpStatus.OK:
                    st.toast('#### %s - %s' % (tag, str(jumpStatus)), icon='⚠️')
                if (st.session_state.processBadJump and jumpStatus != JumpStatus.OK) or jumpStatus == JumpStatus.OK:
                    jumpResultsSubset[tag] = jumpResult
                st.html('<h3>'+jumpStatusInfo+scoringInfo+(badJumpLegend+"<br>If this was NOT a warm-up file, it's probably an ISC altitude violation; please report to Eugene/pr3d4t0r and attach the TRACK.CSV file" if badJumpLegend else '')+'</h3>')
                if (st.session_state.processBadJump and jumpStatus != JumpStatus.OK) or jumpStatus == JumpStatus.OK:
                    displayJumpDataIn(jumpResult.table)
                    plotJumpResult(tag, jumpResult)
                    graphJumpResult(
                        allJumpsPlot,
                        jumpResult,
                        lineColor=SPEED_COLORS[mixColor],
                        legend='%s = %.2f' % (tag, jumpResult.score),
                        showIt=False
                    )
                    displayTrackOnMap(speedJumpTrajectory(jumpResult))
                    _displayAllJumpDataIn(jumpResult.data)
                    _displayScoresIn(jumpResult.scores)
                elif jumpStatus == JumpStatus.SPEED_ACCURACY_EXCEEDS_LIMIT:
                    _displayBadRowsISCAccuracyExceeded(jumpResult.data, jumpResult.window)
            index += 1
        with tabs[0]:
            st.html('<h2>Jumps in this set</h2>')
            if len(resultTags):
                if (st.session_state.processBadJump and jumpStatus != JumpStatus.OK) or jumpStatus == JumpStatus.OK:
                    aggregate = aggregateResults(jumpResultsSubset)
                    if len(aggregate) > 0:
                        displayAggregate = aggregate.style.apply(_styleShowMinMaxIn, subset=[ 'score', ]).apply(_styleShowMaxIn, subset=[ 'maxSpeed', ]).format(precision=2)
                        st.dataframe(displayAggregate)
                        st.html('<h2>Summary</h2>')
                        st.dataframe(totalResultsFrom(aggregate), hide_index = True)
                        st.bokeh_chart(allJumpsPlot, use_container_width=True)
                        # displayTrackOnMap(multipleSpeedJumpsTrajectories(jumpResults))


if '__main__' == __name__:
    main()

