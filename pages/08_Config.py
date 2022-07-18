from __future__ import print_function

import streamlit as st
import pyodbc 
import urllib.request

##
## Start of Streamlit
##
st.markdown("# Config")
st.sidebar.markdown("# Config")

external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')

db_flavour = st.secrets["database"]["flavour"]

db_driver = st.secrets[db_flavour]["driver"]
db_host = st.secrets[db_flavour]["host"]
db_port = st.secrets[db_flavour]["port"]
db_instance = st.secrets[db_flavour]["instance"]
db_database = st.secrets[db_flavour]["database"]
db_username = st.secrets[db_flavour]["username"]
db_password = st.secrets[db_flavour]["password"]

import pyodbc
s = pyodbc.drivers()


try:                      
    pyodbc.connect(driver=f"{db_driver}",
                   server=(f"{db_host},{db_port}\{db_instance}"),
                   database=f"{db_database}",
                   uid=(f"{db_username}"),
                   pwd=f"{db_password}")
    st.write(f"DATABASE CONNECTIVITY from {external_ip}") 
except Exception as e:
    st.write(f"NO DATABASE CONNECTIVITY from {external_ip}") 
    st.error(s)
    st.error(e)

