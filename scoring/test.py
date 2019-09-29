def calculateSpeedAndPitchFor(fileName, elevation = 0.00):
    """
    Accepts a file name to a FlySight data file.
    
    Returns a Series with the results of a speed skydiving jump.
    """
    flightData             = adjustElevation(pd.read_csv(fileName, header = [0, 1]), elevation)
    flightData             = _discardDataOutsideCourse(flightData)
    flightData['unixTime'] = flightData['time'].iloc[:,0].apply(_convertToUnixTime)
    
    return _calculateCourseSpeedUsing(flightData)

    maxSpeed, \
    bestSpeed, \
    startCourse, \
    endCourse = _calculateCourseSpeedUsing(flightData)
    
    # pitchR    = math.atan(maxSpeed/maxHorizontalSpeedFrom(flightData, maxSpeed))
    pitchR    = 0
    
    skydiveResults = pd.Series(
                        [
                            fileName,
                            3.6*maxSpeed,  # km/h; 3,600 seconds, 1,000 meters
                            3.6*bestSpeed,
                            pitchR/DEG_IN_RAD,
                            startCourse,
                            endCourse,
                        ],
                        [
                            'maxSpeed',
                            'bestSpeed',
                            'pitch',
                            'startCourse',
                            'endCourse',

                        ])

#     return skydiveResults
    return flightData

calculateSpeedAndPitchFor(os.path.join(DATA_SOURCE, FLYSIGHT_DATA_FILE), elevation = DZ_AMSL)
