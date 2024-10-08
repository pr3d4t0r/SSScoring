% ssscoring(3) Version 1.7.2 | Speed Skydiving Scoring API documentation

Name
====

**SSScoring** - Speed Skydiving Scoring high level library in Python


Synopsis
========
```bash
pip install -U ssscoring
```

Have a FlySight speed run track file available (can be v1 or v2):
Have one or more FlySight speed run track files available (can be v1 or v2), set
the source directory to the data lake containing them.

```python
from ssscoring.calc import aggregateResults
from ssscoring.calc import processAllJumpFiles
from ssscoring.calc import roundedAggregateResults
from ssscoring.flysight import getAllSpeedJumpFilesFrom

DATA_LAKE = './resources' # can be anywhere
jumpResults = processAllJumpFiles(getAllSpeedJumpFilesFrom(DATA_LAKE))
print(roundedAggregateResults(aggregateResults(jumpResults)))
```

Output:

```bash
python synopsys.py
                           score  5.0  10.0  15.0  20.0  25.0  finalTime  maxSpeed
01-00-00:v2                  472  181   329   420   472   451       24.7       475
resources test-data-00:v1    443  175   299   374   427   449       25.0       449
resources test-data-01:v1    441  176   305   388   432   442       25.0       442
resources test-data-02:v1    451  164   295   387   441   452       25.0       453
```

SSScoring processes all FlySight files (tagged as v1 or v2, depending on the
device) and SkyTrax files.  It aggregates and summarizes the results.  Full
API documentation is available at:

https://pr3d4t0r.github.io/SSScoring/ssscoring.html


Description
===========
SSScoring provides analsysis tools for individual or bulk processing of FlySight
GPS competition data gathered during speed skydiving training and competition.
Scoring methodology adheres to International Skydiving Commission (ISC),
International Speed Skydiving Association (ISSA), and Unite States Parachute
Association (USPA) published competition and scoring rules.  Though FlySight is
the only Speed Measuring Device (SMD) accepted by all these organizations,
SSScoring libraries and tools also operate with track data files produced by
these devices:

- FlySight 2
- SkyTrax GPS and barometric device

SSScoring leverages data manipulation tools in the pandas and NumPy data
analysis libraries.  All the SSScoring code is written in pure Python, but the
implementation leverages libraries that may require native code for GPU and AI
chipset support like Nvidia and M-chipsets.


### Features

- Pure Python
- Supports output from FlySight versions v1 and v2, and SkyTrax devices
- Automatic file version detection
- Bulk file processing via data lake scanning
- Automatic selection of FlySight-like files mixed among files of multiple types
  and from different applications and operating systems
- Individual file processing
- Automatic jump file validation according to competition rules
- Automatic skydiver exit detection
- Automatic jump scoring with robust error detection based on exit altitude,
  break off altitude, scoring window, and validation window
- Produces time series dataframes for the speed run, summary data in 5-second
  intervals, scoring window, speed skydiver track angle with respect to the
  ground, horizontal distance from exit, etc.
- Reports max speed, exit altitude, scoring window end, and other data relevant
  to competitors during training
- Internal data representation includes SI and Imperial units

The current SSScoring API is available on GitHub:
https://pr3d4t0r.github.io/SSScoring/ssscoring.html

The SSScoring package can be installed into any Python environment version 3.9
or later.
https://pypi.org/project/ssscoring

SSScoring also includes Jupyter notebooks for dataset exploratory analysis and
for code troubleshooting.  Unit test coverage is greater than 92%, limited only
by Jupyter-specific components that can't be tested in a standalone environment.


### What is a data lake?

A **data lake** is a files repository that stores data in its raw, unprocessed
form.  A speed skydiving data lake often has two or more of these types of
files:

- FlySight versions 1 or 2 files
- SkyTrax files
- Video files (MP4 or MOV of whatever)
- PDFs of meet bulletins and related event information
- Miscellaneous other junk

SSScoring identifies FlySight and SkyTrax files regardless of what other file
types are available in the data lake.  SSScoring also classifies speed files
from other types of tracks (e.g. wingsuit) based on the performance profile and
scoring windows.  Tell the SSScoring tools where to get all the track files,
even if they are several levels deep in the directory structure, and SSScoring
will find, validate, and score only the speed skydiving files regardless of what
else is available in the data lake.  The only limitation is available memory.
SSScoring has been tested with as many as 467 speed files during a single run,
representing all the training files for a competitive skydiver over 10 months.


### Additional tools

- `nospot` shell script for disabling Spotlight scanning of FlySight file
  file systems
- `umountFlySight` Mac app and shell script for safe unmounting of a FlySight
  device from a Macintosh computer
>>>>>>> Stashed changes


License
=======
The **SSScoring** package, documentation and examples are licensed under the
[BSD-3 open source license](https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt).


