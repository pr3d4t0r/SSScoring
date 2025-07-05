#!/usr/bin/env python3
# See: https://github.com/pr4d4t0r/SSSCoring/blob/master/LICENSE.txt

# https://github.com/ncrevois/streamlit_dash
# https://discuss.streamlit.io/t/theme-defined-in-the-config-toml-file-is-not-applying-when-the-app-is-packaged-using-pyinstaller/79699

from pathlib import Path
from pathlib import PurePath

import os
import sys

import streamlit.web.bootstrap
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
#     sys.argv = [
#         'streamlit',
#         'run',
#         _resolveRunnerPathFrom(bundlePath),
#         '--global.developmentMode=false',
#     ]

    # Set environment variables to ensure production mode and specify the port
    os.environ["STREAMLIT_DEVELOPMENT_MODE"] = "false"  # This disables development mode
    os.environ["STREAMLIT_ENV"] = "production"
    os.environ["STREAMLIT_SERVER_ADDRESS"] = "localhost"
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    os.environ["STREAMLIT_SERVER_PORT"] = "8005"

    sys.argv = [
        'streamlit',
        'run',
        'ssscrunner.py',
        '--server.port=8005',
        '--server.headless=true',
        '--server.address=localhost',
        '--server.headless=true',
        '--server.env=production',
    ]
    sys.exit(stcli.main())
#     streamlit.web.bootstrap.run(
#         'ssscrunner.py',
#         False,
#         sys.argv[1:],
#         {},
#     )

