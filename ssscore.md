% ssscore(1) Version 1.8.2 | Speed Skydiving Scoring command line tool

Name
====

**sscore** - Speed Skydiving Scoring tool for processing spped dive FlySight
files


Synopsis
========
```bash
pip install -U ssscoring
```

`ssscore` will be located in either of these paths:

- `$VIRTUAL_ENV/bin/ssscore`
- `/usr/local/bin/ssscore`

Command after installation:

```bash
ssscore datalake
```

Where `datalake` is a directory containing one or more speed skydiving tracks,
either in the topmost directory or nested.  `ssscore` ignores all files present
in the data lake that aren't speed skydives, even if they are
FlySight-compatible CSV files.

_Examples_:

Scores all of Joe's files in his speed skydiving directory:

```bash
ssscore /Users/joe/speed-skydiving/tracks
```

Score all the files present in the FlySight device mounted at `/mnt`:

```bash
mount /dev/sda1 /mnt/FLYSIGHT1
ssscore /mnt/FLYSIGHT1
umount /mnt/FLYSIGHT1
```


Description
===========
`ssscore` processes speed skydiving FlySight files in bulk.  Track files can
be in versions 1 or 2, or even in SkyTrax format.  The program scores files
according to the International Skydiving Commission, the International Speed
Skydiving Association, and the United States Parachute Association scoring and
competition rules.

`ssscore` writes only to stdout.  It's output may be redicrected or piped as
required.


Arguments
=========
`datalake` is a directory containing one or more speed skydiving tracks,
either at the topmost level or nested.  `ssscore` ignores all files present in
the data lake that aren't speed skydives, even if they are FlySight-compatible
CSV files.

The man page or README.md file for the SSScoring API have a longer description
of what a data lake is and how `ssscore` treats it.


Ooptions
========
None.


Files
=====
`/usr/local/bin/ssscore` if installed via `pip` to the derault Python run-time
`$VIRTUAL_ENV/bin/ssscore` if installed to an active virtual environment.


Bugs and Notes
==============
None.


See Also
========
ssscoring(3)

Project:  https://github.com/pr3d4t0r/SSScoring


License
=======
The **SSScoring** package, documentation and examples are licensed under the
[BSD-3 open source license](https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt).

