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



from lib import masters_data_analytics_lib as mlib
import numpy as np
import pandas as pd
import streamlit as st

def create_download_link(val, filename):
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}">Download file</a>'

##
## Start of Streamlit
##
st.markdown("# Directory Sniffer")
st.sidebar.markdown("# Directory Sniffer")

## Input the post code to search with
directory_file = st.text_input("directory/file")
 
## Capture the input and run generate_report
sniff_file_directory = st.button("SNIFF")
import chromedriver_binary.utils as chromedriver_binary_utils
from chromedriver_binary.utils import print_chromedriver_path
from selenium.webdriver.chrome.service import Service as ChromeService
import chromedriver_binary

print(">>>>>>>>>>>>>print_chromedriver_path>>>>>>>>>>>")
print_chromedriver_path
print(">>>>>>>>>>>>>>>>>>>>>>>>")

print(">>>>>>>>>>>>>chromedriver_binary>>>>>>>>>>>")
print(chromedriver_binary.chromedriver_filename)
print(">>>>>>>>>>>>>>>>>>>>>>>>")

print(">>>>>>>>>>>>>get_chrome_major_version>>>>>>>>>>>")
print(chromedriver_binary_utils.get_latest_release_for_version())
print(">>>>>>>>>>>>>>>>>>>>>>>>")

print(chromedriver_binary_utils.find_binary_in_path(chromedriver_binary_utils.get_chromedriver_filename()))


old_path = os.environ['PATH']
print(">>>>>>>>old_path>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
print(old_path)
print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
try:
    os.environ['PATH'] = "{}{}{}".format('/home/appuser/venv/lib/python3.9/site-packages/chromedriver_binary/chromedriver', os.pathsep, old_path)
finally:
    os.environ['PATH'] = old_path

new_path = os.environ['PATH']
print(">>>>>>>>new_path>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
print(new_path)
print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

import platform
print(platform.platform())

# import chromedriver_autoinstaller as chromedriver
# chromedriver.install()

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
        
        
download_file = st.button("DOWNLOAD")   

if download_file:     
        
        
        
        
    for file in [directory_file]:
            with open(file, "rb") as remote_file:
                encoded = remote_file.read()
    
    html2 = create_download_link(encoded , os.path.basename(directory_file))
    
    st.markdown(html2, unsafe_allow_html=True)        
