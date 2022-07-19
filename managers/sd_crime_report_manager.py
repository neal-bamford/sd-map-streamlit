import uuid
import os

from lib import file_tools as ft
from lib import masters_data_analytics_lib as mlib
from managers import map_manager as map_manager
from managers import sd_crime_report_data_manager as data_manager
from managers import report_manager as report_manager

### This is the process for this report
template_processor_file_name = "./reports/processors/sd_crime_report_template_processor.json"

def load_data(search_term, lib):
    ##
    ## LOAD ALL THE DATA FILES
    ##
    ## London Post Codes
    city = search_term["city"]
    
    sd_london_postcodes_file        = "./data/streamlit_{}_postcodes_oa.csv".format(city.lower())
    sd_london_population_oa_file    = "./data/streamlit_{}_population_oa.csv".format(city.lower())
    sd_london_household_oa_file     = "./data/streamlit_{}_household_population_oa.csv".format(city.lower())
    sd_london_qualification_oa_file = "./data/streamlit_{}_qualifictation_population_oa.csv".format(city.lower())
    
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
    
    ###
    ### LOAD THE RAW DATA
    ###
    #### Load our data. lib will either be mlib or streamlit wrapper mlib which uses caching
    sd_london_postcodes_df, sd_london_population_oa_df, sd_london_household_oa_df, sd_london_qualification_oa_df = load_data(search_term=search_term, lib=lib)

    
    ##
    ## GENERATE THE DATA FOR THE REPORT
    ##
    data_manager.generate_report_data(session_id                    = session_id
                                    , search_term                   = search_term
                                    , report_context                = report_context
                                    , properties                    = properties 
                                    , sd_london_postcodes_df        = sd_london_postcodes_df
                                    , sd_london_population_oa_df    = sd_london_population_oa_df
                                    , sd_london_household_oa_df     = sd_london_household_oa_df
                                    , sd_london_qualification_oa_df = sd_london_qualification_oa_df)
    report_context["general_information"] = "THIS IS PLACEHOLDER DATA"

    
    ##
    ## GENERATE THE MAP FOR THE REPORT
    ##
    ##
    ### RETRIEVE DATA FROM CONTEXT
    ###
    city                       = report_context["city"]
    borough                    = report_context["borough"]
    ward_name                  = report_context["ward_name"]
    post_code                  = report_context["post_code"]
    map_args                   = report_context["map_args"]
    
    map_file_base = "./reports/generation/images/{}_map_{}_{}_{}_{}".format(session_id, city, borough, ward_name, post_code).replace(" ", "_")
    location_png_file = map_manager.generate_map(file       = map_file_base
                                               , map_args   = map_args
                                               , properties = properties)
    
    report_context["location_png_file"] = location_png_file

        
    ###
    ### GENERATE THE REPORT
    ###
    report_context["template_processor_file_name"] = template_processor_file_name
    generated_report = report_manager.generate_report(session_id=session_id
                                             , report_context=report_context
                                             , properties=properties)
    
    return generated_report
