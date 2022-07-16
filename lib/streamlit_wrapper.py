import base64
import streamlit as st
from . import masters_data_analytics_lib as mlib

@st.cache
def csv_to_dataframe(filename, sep=","):
    return mlib.csv_to_dataframe(filename, sep=",")


def create_download_link(val, filename):
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}">Download file</a>'
