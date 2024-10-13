from ssscoring.calc import aggregateResults
from ssscoring.calc import processAllJumpFiles
from ssscoring.calc import roundedAggregateResults
from ssscoring.flysight import getAllSpeedJumpFilesFrom

DATA_LAKE = './resources' # can be anywhere
jumpResults = processAllJumpFiles(getAllSpeedJumpFilesFrom(DATA_LAKE))
print(roundedAggregateResults(aggregateResults(jumpResults)))
