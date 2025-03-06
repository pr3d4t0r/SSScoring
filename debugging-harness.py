# *** or PyCharm's debugger.
#

from collections import namedtuple
from copy import deepcopy

from haversine import haversine
from haversine import Unit

from ssscoring.calc import aggregateResults
from ssscoring.calc import convertFlySight2SSScoring
from ssscoring.calc import dropNonSkydiveDataFrom
from ssscoring.calc import getFlySightDataFromCSVFileName
from ssscoring.calc import getSpeedSkydiveFrom
from ssscoring.calc import isValidMinimumAltitude
from ssscoring.calc import jumpAnalysisTable
from ssscoring.calc import processAllJumpFiles
from ssscoring.calc import processJump
from ssscoring.calc import roundedAggregateResults
from ssscoring.calc import totalResultsFrom
from ssscoring.constants import BREAKOFF_ALTITUDE
from ssscoring.constants import FT_IN_M
from ssscoring.constants import PERFORMANCE_WINDOW_LENGTH
from ssscoring.flysight import getAllSpeedJumpFilesFrom
from ssscoring.flysight import validFlySightHeaderIn
from ssscoring.notebook import SPEED_COLORS
from ssscoring.notebook import graphAltitude
from ssscoring.notebook import graphAngle
from ssscoring.notebook import graphJumpResult
from ssscoring.notebook import initializeExtraYRanges
from ssscoring.notebook import initializePlot

import csv
import os
import os.path as path

import bokeh.plotting as bp
import bokeh.models as bm
import ipywidgets as widgets
import pandas as pd

DATA_LAKE_ROOT = './data'

def main():
    dropZoneAltMSL = 10
    # dropZoneAltMSL = 15.0
    dropZoneAltMSLMeters = dropZoneAltMSL/FT_IN_M
    jumpFiles = getAllSpeedJumpFilesFrom(DATA_LAKE_ROOT)
    filePath = list(jumpFiles.keys())[0]
    rawData, tag = getFlySightDataFromCSVFileName(filePath)
    data = convertFlySight2SSScoring(rawData, altitudeDZMeters=dropZoneAltMSLMeters)
    jumpResult = processJump(data)


if '__main__' == __name__:
    main()

# --------------------------------------------------
# jumpResults = processAllJumpFiles(jumpFiles, altitudeDZMeters = dropZoneAltMSLMeters)
# aggregate = aggregateResults(jumpResults)
# sumResults = totalResultsFrom(aggregate)
# roundedAggregateResults(aggregate)

