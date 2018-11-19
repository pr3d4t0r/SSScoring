# vim: set fileencoding=utf-8:


import math
import os


# *** constants ***

COURSE_START  = 2700.0    # m
COURSE_END    = 1700.0
DEG_IN_RAD    = math.pi/180.0
VALID_MSL     = 100.0 # STD
YEAR_PATH_TAG = '18-'


# *** functions ***


def _findFlySightDataFilesIn(root, filesList):
    for root, directories, files in os.walk(root):
        for file in files:
            if file.upper().endswith(('.CSV', )) and '-checkpoint' not in file.lower():
                source = os.path.join(root, file)
                filesList.append(source)

        for directory in directories:
            _findFlySightDataFilesIn(directory, filesList)

    return


# *** public ***

def updateFlySightDataSource(dataLakePath, dataSourcePath):
    flightFilesList = list()
    os.makedirs(dataSourcePath, exist_ok = True)
    _findFlySightDataFilesIn(dataLakePath, flightFilesList)
    
    for source in sorted(flightFilesList, reverse = True):
        _, fileName  = os.path.split(source)
        destination = os.path.join(dataSourcePath, fileName)
        
        shutil.move(source, destination)
        print('moved %s --> %s' % (source, destination))
    
    print('moved %d CSV files from data lake [%s] to data source [%s]' % (len(flightFilesList), dataLakePath, dataSourcePath))
    
    return

