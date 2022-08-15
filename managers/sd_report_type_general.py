import logging
import os
import uuid

from lib import file_tools as ft
from lib import masters_data_analytics_lib as mlib
from data.daos import dao_facade_local as dao_fac
from managers import sd_report_type_general_data_manager as data_manager
from managers import sd_map_manager as map_manager
from managers import sd_report_type_general_report_manager as report_type_manager
from managers import sd_report_manager_new as report_manager

log = logging.getLogger(__name__)

### This is the process for this report
template_processor_file_name = "./reports/processors/sd_general_report_template_processor.json"
log.debug(f"template_processor_file_name:{template_processor_file_name}")

def load_data(search_term, lib):
    ##
    ## LOAD ALL THE DATA FILES
    ##
    ## London Post Codes
    log.debug("load_data")
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
                  , lib=mlib
                  , dao_fac=dao_fac):
    
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
                                    , dao_fac                       = dao_fac
                                    , sd_london_postcodes_df        = sd_london_postcodes_df
                                    , sd_london_population_oa_df    = sd_london_population_oa_df
                                    , sd_london_household_oa_df     = sd_london_household_oa_df
                                    , sd_london_qualification_oa_df = sd_london_qualification_oa_df)

    
    ##
    ## GENERATE THE MAP FOR THE REPORT
    ##
    ##
    ### RETRIEVE DATA FROM CONTEXT
    ###
    validated_search_term      = report_context["validated_search_term"]
    city                       = validated_search_term["city"]
    borough                    = validated_search_term["borough"]
    ward_name                  = validated_search_term["ward_name"]
    post_code                  = validated_search_term["post_code"]
    
    map_file_base = "./reports/generation/images/{}_map_{}_{}_{}_{}".format(session_id, city, borough, ward_name, post_code).replace(" ", "_")
    map_args      = report_context["map_args"]
    location_png_file = map_manager.generate_map(file       = map_file_base
                                               , map_args   = map_args
                                               , properties = properties)
    
    report_context["location_png_file"] = location_png_file
    
    ###
    ### CREATE THE PARTS FOR THE REPORT FROM THE DATA
    ###
    report_type_manager.generate_report_artefacts(session_id     = session_id
                                                , report_context = report_context
                                                , properties     = properties )    
    
    ###
    ### GENERATE THE REPORT
    ###
    report_context["template_processor_file_name"] = template_processor_file_name
    generated_report = report_manager.generate_report(session_id=session_id
                                             , report_context=report_context
                                             , properties=properties)
    
    log.debug(f"returning generated_report:{generated_report}")
    return generated_report
