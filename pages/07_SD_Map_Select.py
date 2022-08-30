from __future__ import print_function
from lib import file_tools as ft
from lib import streamlit_wrapper as mlib
from data.daos import dao_facade_streamlit as dao_fac

import config_logging
import controllers.sd_report_type_passed_controller as sd_report_controller
import logging
import managers.sd_report_type_crime as sd_report_man_crime
import managers.sd_report_type_general as sd_report_man_general
import managers.sd_report_type_health as sd_report_man_health
import managers.sd_report_type_income as sd_report_man_income
import streamlit as st

import uuid

log = logging.getLogger(__name__)



# if "X" in st.session_state:
#   print("X in st.session")
#   st.session_state.borough_search_term = st.session_state.pop("X")
# else:
#   print("X not st.session")

if "ms_borough_default" not in st.session_state:
  print("initialising st.session_state.ms_borough_default")
  st.session_state.ms_borough_default = None
  
if "ms_borough_default_run" not in st.session_state:
  st.session_state.ms_borough_default_run = False


def create_list(dict):
    ret_list = []
    for key in dict:
        log.debug(key)
        for item in dict[key]["WARD_NAMES"]:
            if item not in ret_list:
                ret_list.append(item)
    
    return ret_list
  
  


## List -- this will come from a DAO
ms_borough_list = ["Hackney", "Hounslow", "Newham", "Richmond upon Thames", "Tower Hamlets"]
ms_borough_wards = {"Hackney":{"WARD_NAMES":["Brownswood", "Hoxton West", "Woodberry Down"]},
                    "Hounslow":{"WARD_NAMES":["Bedfont", "Heston Central", "Turnham Green"]},
                    "Newham":{"WARD_NAMES":["Beckton", "Forest Gate South", "West Ham"]},
                    "Richmond upon Thames":{"WARD_NAMES":["Barnes", "Kew", "Whitton", "Bedfont"]},
                    "Tower Hamlets":{"WARD_NAMES":["Bethnal Green", "Limehouse", "Whitechapel"]}}

ms_ward_list = create_list(ms_borough_wards) 

def set_ms_borough_list(ward=None):
  
  ## We're not restricting with values from the ward_list
  if ward == None:
    ## Stick it in the session
    st.session_state.ms_borough_list = ms_borough_list 
  else:
    log.debug("Some other action borough list")
    
def set_ms_ward_list(borough=None):
  
  if borough == None:
    st.session_state.ms_ward_list = ms_ward_list
  else:
    print(f"restricting the ward option with borough:{borough}")
    st.session_state.ms_ward_list = ms_borough_wards[borough]["WARD_NAMES"]
    # log.debug("Some other action ward list")
        

def ms_borough_on_change():
  st.session_state.ms_borough_default_run = None
  if "borough_search_term" in st.session_state:
    print(f"borough:{st.session_state.borough_search_term}")
    ## Only process if there's something in the borough multiselect
    if st.session_state.borough_search_term != None:
      if len(st.session_state.borough_search_term) >1:
        st.error("Select only one borough")
      elif len(st.session_state.borough_search_term) == 1:
        selected_borough = st.session_state.borough_search_term[0]
        print(f"selected_borough:{selected_borough}")
        set_ms_ward_list(selected_borough)

def ms_ward_on_change():
  st.session_state.ms_borough_default_run = None
  if "ward_search_term" in st.session_state:
    print(f"ward:{st.session_state.ward_search_term}")
    ## Only process if there's something in the borough multiselect
    if st.session_state.ward_search_term != None:
      if len(st.session_state.ward_search_term) >1:
        st.error("Select only one ward")
      elif len(st.session_state.ward_search_term) == 1:
        selected_ward = st.session_state.ward_search_term[0]
        print(f"selected_ward:{selected_ward}")
        print(len(st.session_state.borough_search_term))
        ## If we started by selecting a ward then set the borough
        if len(st.session_state.borough_search_term) == 0:
          print("you set a ward and no borough -> setting borough")
          st.session_state.ms_borough_default = "Newham"
          st.session_state.ms_borough_default_run = True
          print(st.session_state.ms_borough_default_run)
          
          
          # st.session_state["X"] = "Newham"
          #set_ms_borough_list(selected_ward)
          # del st.session_state.borough_search_term
          

set_ms_borough_list()
set_ms_ward_list()

container = st.container()


ms_borough = container.multiselect(label = "Borough", 
                            options = st.session_state.ms_borough_list,
                            default = st.session_state.ms_borough_default, 
                            key="borough_search_term", 
                            help="Borough Search Term" , 
                            on_change=ms_borough_on_change())
  

ms_ward    = container.multiselect(label = "Ward", 
                            options = st.session_state.ms_ward_list,
                            key="ward_search_term",
                            on_change=ms_ward_on_change())
                            

if "ms_borough_default_run" in st.session_state:
  print("In Here")
  
  if st.session_state.ms_borough_default_run == True:
    st.session_state["ms_borough_default_run"] = False
    st.experimental_rerun()
