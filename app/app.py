


from ssscoring.calc import aggregateResults
from ssscoring.calc import convertFlySight2SSScoring
from ssscoring.calc import getFlySightDataFromCSV
from ssscoring.calc import processAllJumpFiles
from ssscoring.calc import processJump
from ssscoring.calc import roundedAggregateResults
from ssscoring.constants import FT_IN_M
from ssscoring.flysight import getAllSpeedJumpFilesFrom

import os

import pandas as pd
import streamlit as st


DATA_LAKE = './data'


def _setPageBasics():
    st.set_page_config(page_title = 'SSScoring GUI Test')
    st.header('SSScoring GUI Test')


if '__main__' == __name__:
    dropZoneAltMSL = 1515
    dropZoneAltMSLMeters = dropZoneAltMSL/FT_IN_M

    jumpFiles = getAllSpeedJumpFilesFrom(DATA_LAKE)
    jumpResults = processAllJumpFiles(jumpFiles, altitudeDZMeters = dropZoneAltMSLMeters)
    results = aggregateResults(jumpResults)

    cellStyles = {
        'score': '{:.2f}',
    }
    cellStyles = '{:.2f}'

    _setPageBasics()
    st.dataframe(results.style.highlight_max(subset = ['score'], axis = 0, color = 'green').highlight_min(subset = ['score'], axis = 0, color = 'orange').format(cellStyles))
    mapHeader = 'data 12-09-17-EC:v1'
    st.map(jumpResults[mapHeader].data, size = 10, color = '#ff0000')
    mapHeader = 'data 19-22-17-ND:v1'
    st.map(jumpResults[mapHeader].data, size = 10, color = '#0000ff')

