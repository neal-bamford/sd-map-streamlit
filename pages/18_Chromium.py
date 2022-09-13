from __future__ import print_function
import streamlit as st

from chromedriver_binary.utils import get_chromedriver_path, get_chrome_major_version, get_chromedriver_filename

st.write(f"get_chromedriver_path():{get_chromedriver_path()}")
st.write(f"get_chrome_major_version():{get_chrome_major_version()}")
st.write(f"get_chromedriver_filename():{get_chromedriver_filename()}")
    
        
