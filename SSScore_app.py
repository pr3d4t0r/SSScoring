#!/usr/bin/env python3
# See: https://github.com/pr4d4t0r/SSSCoring/blob/master/LICENSE.txt

import os
import sys

import streamlit
import pandas
import streamlit.web.cli as stcli


# *** functions ***

def resolvePath(path):
    path = os.path.abspath(os.path.join(os.getcwd(), path))
    return path


# *** main ***

if '__main__' == __name__:
    sys.argv = [
        'streamlit',
        'run',
        resolvePath('ssscrunner.py'),
        '--global.developmentMode=false',
    ]
    sys.exit(stcli.main())

