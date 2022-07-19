
from __future__ import print_function

from lib import streamlit_wrapper as mlib
from lib import file_tools as ft

from managers import sd_crime_report_manager as sd_crime_repo_man
from managers import sd_general_report_manager as sd_general_repo_man
from managers import sd_health_report_manager as sd_health_repo_man
from managers import sd_income_report_manager as sd_income_repo_man

import uuid
import streamlit as st


# reports_generation_clean_temp_files = st.secrets["reports_generation"]["clean_temp_file"]


def clear_text():
    st.session_state["search_borough"] = ""
    st.session_state["search_ward_name"] = ""
    st.session_state["search_post_code"] = ""
    

## City
search_city = "London"


session_id = str(uuid.uuid4())[:8]






##
## Start of Streamlit
##
st.markdown("# SD General Report Refactored")
st.sidebar.markdown("# SD General Report Refactored")

## Input the post code to search with
search_borough   = st.text_input("Borough", key="search_borough")
search_ward_name = st.text_input("Ward Name", key="search_ward_name")
search_post_code = st.text_input("Post Code", key="search_post_code")

## Clear input text
st.button("Clear", on_click=clear_text)

report_type = st.selectbox("Select Report Type", ("Crime", "General", "Health", "Income"))


## Capture the input and run generate_report
generate_report_link = st.button("Generate Report")

##
## Generate Link
##
if generate_report_link:
    
    
    search_term = {"city"      : search_city
                 , "borough"   : search_borough
                 , "ward_name" : search_ward_name
                 , "post_code" : search_post_code}
    
    

    ## Generate a context to place items in which is used when generating the report in the final step
    report_context = {}
    report_context["template_processor_file_name"] = "./reports/processors/sd_general_report_data_manager.json"
    
    ## This comes from Streamlit so fake here
    properties = st.secrets
    
    try:
        print(f"report_type:{report_type}")
        
        
        rep_man = None
        if report_type == "Crime":
            rep_man = sd_crime_repo_man
        elif report_type == "General":
            rep_man = sd_general_repo_man
        elif report_type == "Health":
            rep_man = sd_health_repo_man
        elif report_type == "Income":
            rep_man = sd_income_repo_man

        generated_report = rep_man.generate_report(session_id=session_id, search_term=search_term, report_context=report_context, lib=mlib, properties=properties)    

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
        
        
        html_link = mlib.create_download_link(encoded , gernerated_report_download)
        
        
        
        
        st.markdown(html_link, unsafe_allow_html=True)
    except Exception as e:
        st.error(e)