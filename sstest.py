#!/usr/bin/env python3


from ssscoring import convertFlySight2SSScoring
from ssscoring import dropNonSkydiveDataFrom
from ssscoring import getSpeedSkydiveFrom
from ssscoring import isValidJump
from ssscoring import jumpAnalysisTable

import pandas as pd


if '__main__' == __name__:
    rawData = pd.read_csv('./data/12-45-43.CSV', skiprows = (1,1))

    data = convertFlySight2SSScoring(rawData)
    data = dropNonSkydiveDataFrom(data)
    window, data = getSpeedSkydiveFrom(data)
    if isValidJump(data, window):
        table = jumpAnalysisTable(data)

