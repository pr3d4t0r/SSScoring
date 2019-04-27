# vim: set fileencoding=utf-8:

# BSD 3-Clause License
# 
# Copyright (c) 2018, 2019 Eugene "pr3d4t0r" Ciurana
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# 
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import math
import os
import shutil


# *** constants ***

BREAKOFF_ALTITUDE = 1700.0
COURSE_END        = BREAKOFF_ALTITUDE  # 2019 FAI rules
DEG_IN_RAD        = math.pi/180.0
RESOURCE_PATH     = 'resources'
VALID_MSL         = 100.0 # STD


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
        
        if RESOURCE_PATH not in source:
            shutil.move(source, destination)
        else:
            # Test code, data should not be moved.
            shutil.copy(source, destination)

        print('moved %s --> %s' % (source, destination))
    
    print('moved %d CSV files from data lake [%s] to data source [%s]' % (len(flightFilesList), dataLakePath, dataSourcePath))
    
    return

