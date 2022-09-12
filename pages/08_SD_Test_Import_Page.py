from __future__ import print_function
from lib import file_tools as ft
from lib import streamlit_wrapper as mlib


import config_logging
import logging
import streamlit as st

# import pyodbc as pyodbc

st.markdown("# SD Test Import Page")
st.sidebar.markdown("# SD Test Import Page")

import pip #needed to use the pip functions
for i in pip.get_installed_distributions(local_only=True):
    print(i)

