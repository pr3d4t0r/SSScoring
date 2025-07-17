#.!/usr/bin/env python3
# See: https://github.com/pr4d4t0r/SSSCoring/blob/master/LICENSE.txt


from pathlib import Path
from pathlib import PurePath

import os
import sys

import streamlit.runtime.scriptrunner.magic_funcs # For PyInstaller
import streamlit.web.bootstrap


# *** functions ***

def _resolveRunnerPathFrom(bundlePath: str) -> str:
    path = PurePath(bundlePath)
    runnerPath = Path()
    for dir in path.parts:
        # if dir == 'MacOS':
        if dir == 'SSScore_app':
            break
        runnerPath /= dir
    # runnerPath = Path(runnerPath).joinpath('_internal', 'ssscrunner.py')
    runnerPath = Path(runnerPath) / 'SSScore_app' / '_internal' / 'ssscrunner.py'
    # runnerPath = Path(runnerPath).joinpath('MacOS', 'ssscrunner.py')
    return runnerPath.as_posix()


# *** main ***

if '__main__' == __name__:
    bundlePath = sys.argv[0]
    print('bundlePath = %s' % bundlePath)
    # os.chdir('/Users/ciurana/development/SSScoring/dist/SSScore_app')
    print('current directory = %s' % os.getcwd())
    print('expected runner directory = %s' % _resolveRunnerPathFrom(bundlePath))

    sys.argv = [
        'streamlit',
        'run',
        'ssscrunner.py',
    ]
    streamlit.web.bootstrap.run(
        # TODO:  fix this
        # '_internal/ssscrunner.py', # THIS WORKS FINE IN VIRTUAL ENV
        _resolveRunnerPathFrom(bundlePath),
        False,
        sys.argv[1:],
        {},
    )

