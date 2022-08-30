from __future__ import print_function
from lib import file_tools as ft
from lib import streamlit_wrapper as mlib
from data.daos import dao_facade_streamlit as dao_fac

import config_logging
import controllers.sd_report_type_passed_controller as sd_report_controller
import logging
import managers.sd_report_type_crime as sd_report_man_crime

## TIDY
import managers.sd_report_type_general_new as sd_report_man_general

import managers.sd_report_type_health as sd_report_man_health
import managers.sd_report_type_income as sd_report_man_income
import streamlit as st

import uuid

log = logging.getLogger(__name__)

def clear_text():
    st.session_state["search_borough"] = ""
    st.session_state["search_ward_name"] = ""
    st.session_state["search_post_code"] = ""

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


##
## Start of Streamlit
##
st.markdown("# SD Map Reports")
st.sidebar.markdown("#  SD Map Reports")


def x(borough_wards, borough_ward_name=None):
  # print("in x")
  search_terms_options = []
  if borough_ward_name == None:
    borough_wards_reduced = borough_wards
    for borough_name in borough_wards_reduced.keys():
      # print(f"{borough_name}")
      search_terms_options.append(borough_name)

      for ward_name in borough_wards_reduced[borough_name]['WARD_NAMES']:
        # print(f"\t{ward_name}")
        search_terms_options.append(ward_name)

  elif borough_ward_name != None:
    # print("Not None")
    if len(borough_ward_name) == 1:
      # print("1")
      # print(f"x:ward_name:{borough_ward_name[0]}")
      borough_wards_reduced = borough_wards[borough_ward_name[0]] 
      print(borough_wards_reduced )

      for ward_name in borough_wards_reduced['WARD_NAMES']:
        # print(f"\t{ward_name}")
        search_terms_options.append(ward_name)

  return search_terms_options

  
# def search_options_on_change():
#   print("here")
#   if "search_terms" in st.session_state:
#     print(f"st.session_state.search_terms:{st.session_state.search_terms}")
#
#     if st.session_state.search_terms != None:
#       print("then then here ")
#       _search_terms = st.session_state.search_terms
#       print(_search_terms)
#       st.session_state.search_terms_options = x(search_boroughs_wards, borough_ward_name=_search_terms)
#       print(f"st.session_state.search_terms_options:{st.session_state.search_terms_options}")

# search_boroughs = ["Hackney", "Hounslow", "Newham", "Richmond upon Thames", "Tower Hamlets"]

# search_boroughs_wards = {"Hackney":{"WARD_NAMES":["Brownswood", "Hoxton West", "Woodberry Down"]},
#                          "Hounslow":{"WARD_NAMES":["Bedfont", "Heston Central", "Turnham Green"]},
#                          "Newham":{"WARD_NAMES":["Beckton", "Forest Gate South", "West Ham"]},
#                          "Richmond upon Thames":{"WARD_NAMES":["Barnes", "Kew", "Whitton"]},
#                          "Tower Hamlets":{"WARD_NAMES":["Bethnal Green", "Limehouse", "Whitechapel"]}}
#
# search_terms_options = x(search_boroughs_wards)

# for borough_name in search_boroughs_wards.keys():
#   # print(f"{borough_name}")
#   search_terms_options.append(borough_name)
#
#   for ward_name in search_boroughs_wards[borough_name]['WARD_NAMES']:
#     # print(f"\t{ward_name}")
#     search_terms_options.append(ward_name)
# st.session_state.search_terms_options = search_terms_options
# print(f"st.session_state.k:{st.session_state.search_terms_options}")

# st.session_state.search_terms_options = search_terms_options

                         

# search_terms = st.multiselect(label = "search_terms", 
#                               options = st.session_state.search_terms_options,
#                               key="search_terms", 
#                               help="Search Options" , 
#                               on_change=search_options_on_change())

# options = st.selectbox(label='What are your favorite colors',
#      options = ['Green', 'Yellow', 'Red', 'Blue'])
#
# st.write('You selected:', options)

## Input the post code to search with
## City
search_city = url_search_city if url_search_city != "" else "London"
search_borough   = st.text_input("Borough", value=url_search_borough, key="search_borough", help="Borough you want to analyse")
search_ward_name = st.text_input("Ward Name", value=url_search_ward_name, key="search_ward_name", help="Ward in the borough you want to analyse")
search_post_code = st.text_input("Post Code", value=url_search_post_code, key="search_post_code", help="Post Code in the City you want to analyse")

## Clear input text
st.button("Clear", on_click=clear_text)
#report_type_idx = {"Crime":0, "General":1, "Health":2, "Earnings":3}
report_type_idx = {"General":1}

# print(f"url_report_type:{url_report_type}")
# print(report_type_idx[url_report_type])

# report_type = None

## These will come from a json file I think, but for now, we'll hard code them
# report_type_options = {"Crime":{"Full Report"}, "General":{"Full Report", "Condensed Report"}, "Health":{"Full Report"}, "Earnings":{"Full Report"}}
report_type_options = {"General":{"Full Report"}}
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
                           options=["Crime", "General", "Health", "Earnings"], 
                           index=report_type_idx[url_report_type],
                           on_change = report_type_on_chage())

## And the options of the report we can choose from
report_option = st.selectbox(key="report_option",
                             label="Report Option",
                             options=st.session_state.report_type_option)

st.session_state["report_option_obj"] = report_option


log.debug("Here")
year_from_to = st.slider("Date Range", min_value=2001, max_value=2022, value=[2001,2022], step=1)


## Capture the input and run generate_report
if url_report_auto_generate != "" and url_report_auto_generate.lower() == "true":
    generate_report_link = True
else:
    generate_report_link = st.button("Generate Report")

##
## Generate Link
##
if generate_report_link:
    
    
    search_term = {"city"      : search_city
                 , "borough"   : search_borough
                 , "ward_name" : search_ward_name
                 , "post_code" : search_post_code
                 , "year_from" : year_from_to[0]
                 , "year_to"   : year_from_to[1]}
    

    ## Generate a context to place items in which is used when generating the report in the final step
    report_context = {}
    # report_context["template_processor_file_name"] = "./reports/processors/sd_general_report_data_manager.json"
    ### This should come from another drop down
    report_context["report_option"] = report_option
    
    ## This comes from Streamlit so fake here
    properties = st.secrets
    
    try:
        log.debug(f"report_type:{report_type}")
        
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
        
        
        
        gernerated_report_download = "sd_{}_report_{}_{}_{}{}{}.docx".format(report_type.lower(), city, borough, ward_name, ("_" if post_code != "" else ""), post_code).replace(" ", "_")
        
        
        html_link = mlib.create_download_link(encoded , gernerated_report_download, f"[{report_type} - {report_option}]")
        
        
        
        
        st.markdown(html_link, unsafe_allow_html=True)
    except Exception as e:
        st.error(e)