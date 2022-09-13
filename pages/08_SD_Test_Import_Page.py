from __future__ import print_function
from lib import file_tools as ft
from lib import streamlit_wrapper as mlib


import config_logging
import logging
import streamlit as st

# import pyodbc as pyodbc

st.markdown("# SD Test Import Page")
st.sidebar.markdown("# SD Test Import Page")

import pkg_resources

dists = [d for d in pkg_resources.working_set]

st.write(dists)

import subprocess

def install(name):
    subprocess.call(['pip', 'install', name])
    
install("pyodbc")