
import streamlit as st
import time
import numpy as np
import sys
import os
import urllib.request

# Add our lib directory
sys.path.append("lib")

import masters_data_analytics_lib as mlib

external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')

st.markdown("# Dataframe Page")
st.sidebar.markdown("# Dataframe Page")

# Take some secrets and display them to see how it works
st.write(os.environ["str_greeting"])
st.write(external_ip)


time.sleep(0.05)

bh_pop_data_file = "../data/streamlit_london_population_oa.csv"

bh_pop_df = mlib.csv_to_dataframe(bh_pop_data_file)

stats_table = bh_pop_df.agg({"AreaHectares": ["sum","mean","std","skew","kurt"]}).round(2)

st.dataframe(stats_table)