from __future__ import print_function

import base64
from datetime import date
import os
import shutil
import sys
import time
import uuid
import mailmerge as mm

from docx import Document
import docx
from docx.shared import Inches
import folium
from fpdf import FPDF
from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.firefox import GeckoDriverManager

from selenium.webdriver.chrome.service import Service as ChromeService

from lib import masters_data_analytics_lib as mlib
import numpy as np
import pandas as pd
import streamlit as st

##
## Start of Streamlit
##
st.markdown("# Directory Sniffer")
st.sidebar.markdown("# Directory Sniffer")

## Input the post code to search with
directory_file = st.text_input("directory/file")
 
## Capture the input and run generate_report
sniff_file_directory = st.button("SNIFF")


##
## Generate Link
##
if sniff_file_directory:
    
    if(os.path.isdir(directory_file)):
        st.write("## {} is A DIRECTORY".format(directory_file))    
        st.write(os.listdir(directory_file))
    
    elif(os.path.isfile(directory_file)):
        st.write("### {} is A FILE".format(directory_file))    
    
    elif(os.path.islink(directory_file)):
            st.write("### {} is A SYMLINK".format(directory_file))    
            st.write("### {}".format(os.readlink(directory_file)))    

    else:
        st.write("## {} is not a directory or file".format(directory_file))    
