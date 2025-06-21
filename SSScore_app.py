#!/usr/bin/env python3
# See: https://github.com/pr4d4t0r/SSSCoring/blob/master/LICENSE.txt

from pathlib import Path
from pathlib import PurePath

import sys

import streamlit.web.cli as stcli


# *** functions ***

def _resolveRunnerPathFrom(bundlePath: str) -> str:
    path = PurePath(bundlePath)
    runnerPath = Path()
    for dir in path.parts:
        if dir == 'MacOS':
            break
        runnerPath /= dir
    # runnerPath = Path(runnerPath).joinpath('Resources', 'ssscrunner.py')
    runnerPath = Path(runnerPath).joinpath('MacOS', 'ssscrunner.py')
    return runnerPath.as_posix()


# *** main ***

if '__main__' == __name__:
    bundlePath = sys.argv[0]
    sys.argv = [
        'streamlit',
        'run',
        _resolveRunnerPathFrom(bundlePath),
        '--global.developmentMode=false',
    ]
    sys.exit(stcli.main())

