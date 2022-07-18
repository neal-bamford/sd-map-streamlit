import uuid
import os
import json

from lib import file_tools as ft
from lib import masters_data_analytics_lib as mlib
from managers import map_manager as map_manager
from managers import sd_general_report_data_manager as data_manager
from managers import report_manager as report_manager


def load_data(search_term, lib):
    ##
    ## LOAD ALL THE DATA FILES
    ##
    ## London Post Codes
    city = search_term["city"]
    
    sd_london_postcodes_file        = "./data/streamlit_{}_postcodes_oa.csv".format(city)
    sd_london_population_oa_file    = "./data/streamlit_{}_population_oa.csv".format(city)
    sd_london_household_oa_file     = "./data/streamlit_{}_household_population_oa.csv".format(city)
    sd_london_qualification_oa_file = "./data/streamlit_{}_qualifictation_population_oa.csv".format(city)
    
    sd_london_postcodes_df        = lib.csv_to_dataframe(sd_london_postcodes_file)
    sd_london_population_oa_df    = lib.csv_to_dataframe(sd_london_population_oa_file)
    sd_london_household_oa_df     = lib.csv_to_dataframe(sd_london_household_oa_file)
    sd_london_qualification_oa_df = lib.csv_to_dataframe(sd_london_qualification_oa_file) 
    
    return sd_london_postcodes_df, sd_london_population_oa_df, sd_london_household_oa_df, sd_london_qualification_oa_df

def generate_report(session_id
                  , search_term
                  , report_context
                  , properties
                  , lib=mlib):
    
    
    
    template_processor_file_name = report_context["template_processor_file_name"]

    with open(template_processor_file_name) as template_processor_file:
        template_processor = json.load(template_processor_file)

    
    ## Load our data. lib will either be mlib or streamlit wrapper mlib which uses caching
    sd_london_postcodes_df, sd_london_population_oa_df, sd_london_household_oa_df, sd_london_qualification_oa_df = load_data(search_term=search_term, lib=lib)
    
    ## Pass the json around
    report_context["template_processor"] = template_processor

    ##
    ## Generate the report data from the passed data
    ##
    data_manager.generate_report_data(session_id                    = session_id
                                    , search_term                   = search_term
                                    , report_context                = report_context
                                    , properties                    = properties 
                                    , sd_london_postcodes_df        = sd_london_postcodes_df
                                    , sd_london_population_oa_df    = sd_london_population_oa_df
                                    , sd_london_household_oa_df     = sd_london_household_oa_df
                                    , sd_london_qualification_oa_df = sd_london_qualification_oa_df)
    ##
    ## Get some data
    ##
    city                       = report_context["city"]
    borough                    = report_context["borough"]
    ward_name                  = report_context["ward_name"]
    post_code                  = report_context["post_code"]
    post_code_search_longitude = report_context["post_code_search_longitude"]
    post_code_search_latitude  = report_context["post_code_search_latitude"]
    pc_longitudes              = report_context["pc_longitudes"]
    pc_latitudes               = report_context["pc_latitudes"]
    
    map_file_base = "./reports/generation/images/{}_map_{}_{}_{}_{}".format(session_id, city, borough, ward_name, post_code)
    
    ##
    ## Generate the map    
    ##
    location_png_file = map_manager.generate_map(file=map_file_base
                                               , post_code_search = post_code
                                               , ward_name = ward_name
                                               , post_code_search_longitude = post_code_search_longitude
                                               , post_code_search_latitude = post_code_search_latitude
                                               , pc_longitudes = pc_longitudes
                                               , pc_latitudes = pc_latitudes
                                               , properties = properties)
    
    report_context["location_png_file"] = location_png_file
        
    ## Assemble the report from template and various outher data...
    ## Start creating the report for the template
    template_name = "sd_general_report_processor_template.docx"
    # report_merge_data = data["report_merge_data"]
    
    generated_report = report_manager.generate_report(session_id=session_id
                                             , report_context=report_context
                                             , properties=properties)
    
    return generated_report
