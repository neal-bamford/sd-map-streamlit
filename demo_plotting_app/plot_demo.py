
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

# Take some secrets and display them to see how it works
st.write(os.environ["str_greeting"])
st.write(external_ip)

progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()
last_rows = np.random.randn(1, 1)

chart = st.line_chart(last_rows)
for i in range(1, 101):
    new_rows = last_rows[-1, :] + np.random.randn(50, 1).cumsum(axis=0)

status_text.text("%i%% Complete" % i)
#status_text.text("Hello World")

chart.add_rows(new_rows)


progress_bar.progress(i)
last_rows = new_rows


#Load the populatoin data file
bh_pop_data_file = "./data/bh_population.csv"

bh_pop_df = mlib.csv_to_dataframe(bh_pop_data_file)

stats_table = bh_pop_df.agg({"AreaHectares": ["sum","mean","std","skew","kurt"]}).round(2)

st.dataframe(stats_table)

time.sleep(0.05)

progress_bar.empty()