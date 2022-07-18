
from __future__ import print_function

from lib import streamlit_wrapper as mlib
from lib import file_tools as ft
from managers import sd_general_report_manager as sd_gen_repo_man

import uuid
import streamlit as st


# reports_generation_clean_temp_files = st.secrets["reports_generation"]["clean_temp_file"]

## City
city = "london"


session_id = str(uuid.uuid4())[:8]




##
## Start of Streamlit
##
st.markdown("# SD General Report Refactored")
st.sidebar.markdown("# SD General Report Refactored")

## Input the post code to search with
search_input = st.text_input("Search Term")
 
## Capture the input and run generate_report
generate_report_link = st.button("Generate General Report")


##
## Generate Link
##
if generate_report_link:
    
    
    search_term = {"city"      : city
                 , "ward"      : ""
                 , "borough"   : ""
                 , "post_code" : search_input}
    
    

    ## Generate a context to place items in which is used when generating the report in the final step
    report_context = {}
    report_context["template_processor_file_name"] = "./reports/processors/sd_general_report_data_manager.json"
    
    ## This comes from Streamlit so fake here
    properties = st.secrets
    
    generated_report = sd_gen_repo_man.generate_report(session_id=session_id, search_term=search_term, report_context=report_context, lib=mlib, properties=properties)    

    
    ##
    ## Generate the report data from the passed data
    ##
    # sd_gen_rep_data = sd_gen_rep_dat_man.generate_report_data(city = city
    #                                                         , search_term                   = search_term
    #                                                         , session_id                    = session_id
    #                                                         , sd_london_population_oa_df    = sd_london_population_oa_df
    #                                                         , sd_london_postcodes_df        = sd_london_postcodes_df
    #                                                         , sd_london_household_oa_df     = sd_london_household_oa_df
    #                                                         , sd_london_qualification_oa_df = sd_london_qualification_oa_df)
    #
    # ##
    # ## Get some data
    # ##
    # post_code_search           = sd_gen_rep_data["post_code"]
    # ward_name                  = sd_gen_rep_data["ward_name"]
    # borough                    = sd_gen_rep_data["borough"]
    # post_code_search_longitude = sd_gen_rep_data["post_code_search_longitude"]
    # post_code_search_latitude  = sd_gen_rep_data["post_code_search_latitude"]
    # pc_longitudes              = sd_gen_rep_data["pc_longitudes"]
    # pc_latitudes               = sd_gen_rep_data["pc_latitudes"]
    #
    # map_file_base = "./reports/generation/images/{}_map_{}_{}_{}_{}".format(session_id, city, borough, ward_name, post_code_search)
    #
    # ##
    # ## Generate the map    
    # ##
    # location_png_file = map_man.generate_map(file=map_file_base
    #                                        , post_code_search = sd_gen_rep_data["post_code"]
    #                                        , ward_name = ward_name
    #                                        , post_code_search_longitude = post_code_search_longitude
    #                                        , post_code_search_latitude = post_code_search_latitude
    #                                        , pc_longitudes = pc_longitudes
    #                                        , pc_latitudes = pc_latitudes
    #                                        , chrome_binary_location = "C:/DISTRIBUTIONS/ChromeDriver/chromedriver.exe"
    #                                        , browser_pause_s = 3)
    #
    # ## Assemble the report from template and various outher data...
    # ## Start creating the report for the template
    # template_name = "sd_general_report_processor_template.docx"
    # report_merge_data = sd_gen_rep_data["report_merge_data"]
    #
    # generated_report = rep_man.generate_report(session_id=session_id
    #                                          , template_name=template_name
    #                                          , location_png_file=location_png_file
    #                                          , report_merge_data=report_merge_data
    #                                          , remove_temp_files=reports_generation_clean_temp_files)    
    #

    ### 
    ### Read in the document to send out on the link
    ###    
    for file in [generated_report]:
            with open(file, "rb") as report:
                encoded = report.read()
    
    borough   = report_context["borough"]
    ward_name = report_context["ward_name"]
    post_code  = report_context["post_code"]
    
    gernerated_report_download = "sd_general_report_{}_{}_{}_{}.docx".format(city, borough, ward_name, post_code).replace(" ", "_")
    
    
    html_link = mlib.create_download_link(encoded , gernerated_report_download)
    
    
    
    
    st.markdown(html_link, unsafe_allow_html=True)