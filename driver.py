#!/usr/bin/env python3

# Tactical debugging aid driver.  Used for executing code snippets that are
# otherwise hard to debug in a notebook.


from ssscoring import BREAKOFF_ALTITUDE
from ssscoring import PERFORMANCE_WINDOW_LENGTH
from ssscoring import convertFlySight2SSScoring
from ssscoring import dropNonSkydiveDataFrom
from ssscoring import getSpeedSkydiveFrom
from ssscoring import isValidJump
from ssscoring import jumpAnalysisTable
from ssscoring.notebook import processJump

import pandas as pd


if '__main__' == __name__:
    jumpResult = processJump(convertFlySight2SSScoring(pd.read_csv('data/23-09-04/12-54-41.CSV', skiprows = (1, 1))))

