# See: https://github.com/pr3d4t0r/SSScoring/blob/master/LICENSE.txt


# from ssscoring.app import main

import os
import pathlib

import streamlit as st


if '__main__' == __name__:
    st.write(os.environ)
    dirPath = pathlib.Path('.')
    st.write('Path = %s' % dirPath.absolute())
    for entry in dirPath.iterdir():
        st.write(entry)

    # main()

