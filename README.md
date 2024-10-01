% ssscoring(3) Version 1.7.2 | Speed Skydiving Scoring API documentation

Name
====
**SSScoring** - Speed Skydiving Scoring library and tools.



Synopsis
========
**SSScoring** - Speed Skydiving Scoring library, exploratory analysis tools, and
multi-platform GUI apps written in Python.

```bash
pip install ssscoring
```


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

The SSScoring package can be installed into any Python installation version 3.9
or later.
https://pypi.org/project/ssscoring

SSScoring also includes Jupyter notebooks for dataset exploratory analysis and
for code troubleshooting.  Unit test coverage is greater than 92%, limited only
by Jupyter-specific components that can't be tested in a standalone environment.


### Additional tools

- `nospot` shell script for disabling Spotlight scanning of FlySight file
  file systems
- `umountFlySight` Mac app and shell script for safe unmounting of a FlySight
  device from a Macintosh computer


License
=======
The **SSScoring** package, documentation and examples are licensed under the
[BSD-3 open source license](https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt).


