from __future__ import print_function
from lib import file_tools as ft
from lib import streamlit_wrapper as mlib
from data.daos import dao_facade_streamlit as dao_fac

import config_logging
import controllers.sd_report_type_passed_controller as sd_report_controller
import logging
import managers.sd_report_type_crime as sd_report_man_crime
import managers.sd_report_type_general_new as sd_report_man_general
import managers.sd_report_type_health as sd_report_man_health
import managers.sd_report_type_income as sd_report_man_income
import streamlit as st
from lib import db_tools as db_tools

## This comes from Streamlit so fake here
properties = st.secrets
database_props = properties[properties["database"]["flavour"]] 
db_conn = None
db_conn = db_tools.get_db_conn(database_props)

import uuid

log = logging.getLogger(__name__)


session_id = str(uuid.uuid4())[:8]

query_params = st.experimental_get_query_params()
log.debug(f"query_params:{query_params}")

url_search_city = ""
url_search_borough = ""
url_search_ward_name = ""
url_search_post_code = ""
url_report_type = "General"
url_report_auto_generate = ""

if "search_city" in  query_params:
    url_search_city = query_params["search_city"][0]
    
if "search_borough" in  query_params:
    url_search_borough = query_params["search_borough"][0]
    
if "search_ward_name" in  query_params:
    url_search_ward_name = query_params["search_ward_name"][0]
    
if "search_post_code" in  query_params:
    url_search_post_code = query_params["search_post_code"][0]
    
if "report_type" in  query_params:
    url_report_type = query_params["report_type"][0]
    
if "report_auto_generate" in  query_params:
    url_report_auto_generate = query_params["report_auto_generate"][0]
    
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

def borough_from_ward(ward_name, borough_dict):
    ret_list = []
    
    for borough in borough_dict:
        wards = borough_dict[borough]["WARD_NAMES"]
        if ward_name in wards:
            ret_list.append(borough)
        
    return ret_list



def df_to_dict_of_lists(df, df_key, df_child_key, list_key_name):
    ret_dict = {}
    ## Create the keys
    unique_df_key_list = borough_list = boroughs_and_wards_df[df_key].unique().tolist()
    
    ## Loop through them
    for unique_df_key in unique_df_key_list:
        child_to_list = df[df[df_key] == unique_df_key][df_child_key].to_list()
        ret_dict[unique_df_key]={list_key_name:child_to_list}

    return ret_dict
  
  
### Retrieve the boroughs and wards
boroughs_and_wards_df = dao_fac.boroughs_and_wards(db_conn, None)

## List -- this will come from a DAO
# ms_borough_list = ["Hackney", "Hounslow", "Newham", "Richmond upon Thames", "Tower Hamlets"]
#
# ms_borough_wards = {"Hackney":{"WARD_NAMES":["Brownswood", "Hoxton West", "Barnes", "Woodberry Down"]},
#                     "Hounslow":{"WARD_NAMES":["Bedfont", "Heston Central", "Turnham Green"]},
#                     "Newham":{"WARD_NAMES":["Beckton", "Forest Gate South", "West Ham"]},
#                     "Richmond upon Thames":{"WARD_NAMES":["Barnes", "Kew", "Whitton", "Bedfont"]},
#                     "Tower Hamlets":{"WARD_NAMES":["Bethnal Green", "Limehouse", "Whitechapel"]}}

ms_borough_list = boroughs_and_wards_df["BOROUGH"].unique().tolist()
ms_borough_wards = df_to_dict_of_lists(boroughs_and_wards_df, "BOROUGH", "WARD_NAME", "WARD_NAMES")

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
          st.session_state.ms_borough_default = borough_from_ward(selected_ward, ms_borough_wards)
          st.session_state.ms_borough_default_run = True
          print(st.session_state.ms_borough_default_run)
          
          
          # st.session_state["X"] = "Newham"
          #set_ms_borough_list(selected_ward)
          # del st.session_state.borough_search_term
          

set_ms_borough_list()
set_ms_ward_list()


def clear_text():
    st.session_state["borough_search_term"] = []
    st.session_state["ward_search_term"] = []
    st.session_state["post_code_search_term"] = ""


## PAGE START

st.markdown("# SD Map Reports")
st.sidebar.markdown("#  SD Map Reports")

## INPUT FIELDS START

container = st.container()

search_city = url_search_city if url_search_city != "" else "London"

ms_borough = container.multiselect(label = "Borough", 
                            options = st.session_state.ms_borough_list,
                            default = st.session_state.ms_borough_default, 
                            key="borough_search_term", 
                            help="Borough name of area to search" , 
                            on_change=ms_borough_on_change())
  

ms_ward    = container.multiselect(label = "Ward", 
                            options = st.session_state.ms_ward_list,
                            key="ward_search_term",
                            help="Ward name of area to search" , 
                            on_change=ms_ward_on_change())

s_post_code = st.text_input(label = "Post Code",
                            value = "", 
                            key="post_code_search_term",
                            help="Post code of area to search")

st.button("Clear", on_click=clear_text)


# print(f"url_report_type:{url_report_type}")
# print(report_type_idx[url_report_type])

# report_type = None

## These will come from a json file I think, but for now, we'll hard code them
# report_type_options = {"Crime":{"Full Report"}, "General":{"Full Report", "Condensed Report"}, "Health":{"Full Report"}, "Earnings":{"Full Report"}}

report_type_idx = {"General":0, "X":1}
report_type_options = report_type_idx.keys() 
report_type_options = {"General":{"Full Report"}, "X":{"A", "B"}}
## Choose the initial set to dispaly as options   
report_type_option = report_type_options[url_report_type]
## Stick it into the streamlit session
st.session_state.report_type_option = report_type_option

def report_type_on_chage():
  """
  When the report_type selectbox chnages we need to set the
  value for the options
  """
  if "report_type" in st.session_state:
    if st.session_state.report_type != None:
        ## Update the available options for the report_type
        report_type_option = report_type_options[st.session_state.report_type]
        ## Stick it into the streamlit session
        st.session_state.report_type_option = report_type_option

## This is the report type
report_type = st.selectbox(key="report_type",
                           label="Report Type",
                           options=report_type_options, 
                           index=report_type_idx[url_report_type],
                           on_change = report_type_on_chage())

## And the options of the report we can choose from
report_option = st.selectbox(key="report_option",
                             label="Report Option",
                             options=st.session_state.report_type_option)

st.session_state["report_option_obj"] = report_option


year_from_to = st.slider("Date Range", min_value=2010, max_value=2022, value=[2010,2022], step=1)
# year_from_to = st.slider("Date Range", min_value=2001, max_value=2022, value=[2001,2022], step=1)
## INPUT FIELDS END

## GENERATE REPORT BUTTON START
## Capture the input and run generate_report
if url_report_auto_generate != "" and url_report_auto_generate.lower() == "true":
    generate_report_link = True
else:
    generate_report_link = st.button("Generate Report")
## GENERATE REPORT BUTTON END

#### GENERATE THE REPORT START
if generate_report_link:
    
    print(f"ms_borough:{ms_borough}")
    print(f"ms_wardh:{ms_ward}")
    print(f"s_post_code:{s_post_code}")
    print(f"year_from_to[0]:{year_from_to[0]}")
    print(f"year_from_to[1]:{year_from_to[1]}")
    
    search_borough   = ms_borough[0]
    search_ward_name = ms_ward[0]
    search_post_code = s_post_code
    year_from        = year_from_to[0]
    year_to          = year_from_to[1]
    
    search_term = {"city"      : search_city
                 , "borough"   : search_borough
                 , "ward_name" : search_ward_name
                 , "post_code" : search_post_code
                 , "year_from" : year_from
                 , "year_to"   : year_to}
    

    ## Generate a context to place items in which is used when generating the report in the final step
    report_context = {}
    # report_context["template_processor_file_name"] = "./reports/processors/sd_general_report_data_manager.json"
    ### This should come from another drop down
    report_context["report_option"] = report_option
    
    
    try:
        print(f"report_type:{report_type}")
        
        rep_man = None
        if report_type == "Crime":
            rep_man = sd_report_man_crime
        elif report_type == "General":
            rep_man = sd_report_man_general
            template_processor_file_name = "./reports/processors/sd_general_report_template_processor_dev.json"
            report_context["template_processor_file_name"] = template_processor_file_name
            
        elif report_type == "Health":
            rep_man = sd_report_man_health
        elif report_type == "Earnings":
            rep_man = sd_report_man_income

        generated_report = rep_man.generate_report(session_id=session_id, search_term=search_term, report_context=report_context, properties=properties, lib=mlib, dao_fac=dao_fac)    
        ### 
        ### Read in the document to send out on the link
        ###    
        for file in [generated_report]:
                with open(file, "rb") as report:
                    encoded = report.read()
        
        city      = report_context["city"]
        borough   = report_context["borough"]
        ward_name = report_context["ward_name"]
        post_code = report_context["post_code"]
        
        gernerated_report_download = "sd_{}_report_{}_{}_{}{}{}_{}_{}.docx".format(report_type.lower(), city, borough, ward_name, ("_" if post_code != "" else ""), post_code, year_from, year_to).replace(" ", "_")
        html_link = mlib.create_download_link(encoded , gernerated_report_download, f"[{report_type} - {report_option}]")
        st.markdown(html_link, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(e)
        
#### GENERATE THE REPORT END
                            
## THIS BIT IS A SWITCH TO TURN OFF THE UPDATE - NOT 100% SURE HOW IT WORKS YET
if "ms_borough_default_run" in st.session_state:
  if st.session_state.ms_borough_default_run == True:
    st.session_state["ms_borough_default_run"] = False
    st.experimental_rerun()

