#
# *** Used for interactive debugging sessions with pdb 
# *** or PyCharm's debugger.
#

from collections import namedtuple
from copy import deepcopy

from haversine import haversine
from haversine import Unit

from ssscoring.constants import BREAKOFF_ALTITUDE
from ssscoring.constants import FT_IN_M
from ssscoring.constants import PERFORMANCE_WINDOW_LENGTH
from ssscoring.fs1 import aggregateResults
from ssscoring.fs1 import convertFlySight2SSScoring
from ssscoring.fs1 import dropNonSkydiveDataFrom
from ssscoring.fs1 import getAllSpeedJumpFilesFrom
from ssscoring.fs1 import getSpeedSkydiveFrom
from ssscoring.fs1 import isValidJump
from ssscoring.fs1 import isValidMinimumAltitude
from ssscoring.fs1 import jumpAnalysisTable
from ssscoring.fs1 import processAllJumpFiles
from ssscoring.fs1 import roundedAggregateResults
from ssscoring.fs1 import totalResultsFrom
from ssscoring.fs1 import validFlySightHeaderIn
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

dropZoneAltMSL = 23
dropZoneAltMSLMeters = dropZoneAltMSL/FT_IN_M
jumpFiles = getAllSpeedJumpFilesFrom(DATA_LAKE_ROOT)
jumpResults = processAllJumpFiles(jumpFiles, altitudeDZMeters = dropZoneAltMSLMeters)
aggregate = aggregateResults(jumpResults)
roundedAggregateResults(aggregate)

