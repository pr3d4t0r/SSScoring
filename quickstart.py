from ssscoring.calc import aggregateResults
from ssscoring.calc import convertFlySight2SSScoring
from ssscoring.calc import getFlySightDataFromCSV
from ssscoring.calc import processAllJumpFiles
from ssscoring.calc import processJump
from ssscoring.calc import roundedAggregateResults
from ssscoring.constants import FT_IN_M
from ssscoring.flysight import getAllSpeedJumpFilesFrom

import os

DATA_LAKE = './resources' # can be anywhere

dropZoneAltMSL = 100
dropZoneAltMSLMeters = dropZoneAltMSL/FT_IN_M
jumpFile = os.path.join('resources', 'test-data-00.CSV')
rawData, tag = getFlySightDataFromCSV(jumpFile)

jumpResult = processJump(
    convertFlySight2SSScoring(
        rawData,
        altitudeDZMeters = dropZoneAltMSLMeters))
print('%s - score = %5.2f' % (tag, jumpResult.score))
print(jumpResult.table)
print()

jumpFiles = getAllSpeedJumpFilesFrom(DATA_LAKE)
jumpResults = processAllJumpFiles(jumpFiles, altitudeDZMeters = dropZoneAltMSLMeters)
results = roundedAggregateResults(aggregateResults(jumpResults))
print(results)
