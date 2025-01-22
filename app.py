# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt


import os
import pathlib

dirPath = pathlib.Path('.')
# This doesn't work because streamlit.io's os package is locekd.
# os.environ['PYTHONPATH'] = dirPath.absolute()

import streamlit as st

from ssscoring.app import main


if '__main__' == __name__:
    st.write(os.environ)
    st.write('Path = %s' % dirPath.absolute())
    for entry in dirPath.iterdir():
        st.write(entry)

    main()

