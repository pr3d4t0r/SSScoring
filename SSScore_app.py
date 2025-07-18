#.!/usr/bin/env python3
# See: https://github.com/pr4d4t0r/SSSCoring/blob/master/LICENSE.txt


from pathlib import Path
from pathlib import PurePath

import os
import sys

import streamlit.runtime.scriptrunner.magic_funcs # For PyInstaller
import streamlit.web.bootstrap


# *** functions ***

# def _resolveRunnerPathFrom(bundlePath: str) -> str:
#     path = PurePath(bundlePath)
#     runnerPath = Path()
#     for dir in path.parts:
#         # if dir == 'MacOS':
#         if dir == 'SSScore_app':
#             break
#         runnerPath /= dir
#     # runnerPath = Path(runnerPath).joinpath('_internal', 'ssscrunner.py')
#     runnerPath = Path(runnerPath) / 'SSScore_app' / '_internal' / 'ssscrunner.py'
#     # runnerPath = Path(runnerPath).joinpath('MacOS', 'ssscrunner.py')
#     return runnerPath.as_posix()


def _resolveRunnerPath() -> str:
    if hasattr(sys, 'frozen'):
        basePath = Path(sys._MEIPASS)
    else:
        basePath = Path(__file__).parent
    return (basePath / 'ssscrunner.py').as_posix()


def _assertStreamlitDir():
    dir = Path(os.environ['HOME']) / '.streamlit'
    msg = '%s: ' % dir.as_posix()
    if not dir.exists():
        os.makedirs(dir.as_posix(), exist_ok=True)
        msg += '...created'
    else:
        msg += 'OK'
    print(msg)


# *** main ***

if __name__ == '__main__':
    bundlePath = sys.argv[0]
    print('bundlePath = %s' % bundlePath)
    print('current directory = %s' % os.getcwd())
    print('expected runner path = %s' % _resolveRunnerPath())
    _assertStreamlitDir()

    runnerPath = _resolveRunnerPath()
    sys.argv = [
        'streamlit',
        'run',
        'ssscrunner.py',
    ]
    streamlit.web.bootstrap.run(
        runnerPath,
        False,
        sys.argv[1:],
        {},
    )

