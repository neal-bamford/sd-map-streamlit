import logging
import os
import uuid

from lib import file_tools as ft
from lib import masters_data_analytics_lib as mlib
from managers import sd_search_validation as search_validation
from managers import sd_map_manager as map_manager
from managers import sd_report_manager as report_manager
from data.daos import dao_facade_local as dao_fac

from managers.sections import sd_report_section_02_Population as report_section_populaton
from managers.sections import sd_report_section_03_Ethnicity as report_section_ethnicity
from managers.sections import sd_report_section_04_General_Health as report_section_health
from managers.sections import sd_report_section_05_Education as report_section_education
from managers.sections import sd_report_section_06_Earnings as report_section_earnings
from managers.sections import sd_report_section_07_Crime as report_section_crime

log = logging.getLogger("sd_report_type_general")

def generate_report(session_id
                  , search_term
                  , report_context
                  , properties
                  , lib=mlib
                  , dao_fac=dao_fac):
    """
    Orchestrates the the creation of the general report by calling the sections after validating the 
    search terms, also makes use of the map manager to create the map image for use in the document.
    """
    
    log.info("Generating General Report")

    
    ###
    ### VALIDATE THE SEARCH TERMS
    ###
    validated_search_term = search_validation.validate_search(session_id
                                                            , search_term
                                                            , report_context
                                                            , properties
                                                            , lib
                                                            , dao_fac)

    ## Add them to the report context for merging with the word doc  
    report_context["city"] = validated_search_term["city"].capitalize()
    report_context["ward_name"] = validated_search_term["ward_name"]
    report_context["borough"] = validated_search_term["borough"]
    report_context["post_code"] = validated_search_term["post_code"]
    report_context["post_code_or_ward_name"] = validated_search_term["post_code"] if validated_search_term["post_code"] != "" else validated_search_term["ward_name"]

    ##
    ### GENERATE POPULATION SECTION
    ##
    report_section_populaton.generate_report_section(session_id     = session_id
                                                   , search_term    = validated_search_term
                                                   , report_context = report_context
                                                   , properties     = properties 
                                                   , dao_fac        = dao_fac)  

    ##
    ### GENERATE ETHNICITY SECTION
    ##
    report_section_ethnicity.generate_report_section(session_id     = session_id
                                                   , search_term    = validated_search_term
                                                   , report_context = report_context
                                                   , properties     = properties 
                                                   , dao_fac        = dao_fac)  
    
    ##
    ### GENERATE HEALTH SECTION
    ##
    report_section_health.generate_report_section(session_id     = session_id
                                                , search_term    = validated_search_term
                                                , report_context = report_context
                                                , properties     = properties 
                                                , dao_fac        = dao_fac)  

    ##
    ### GENERATE EDUCATION SECTION
    ##
    report_section_education.generate_report_section(session_id     = session_id
                                                   , search_term    = validated_search_term
                                                   , report_context = report_context
                                                   , properties     = properties 
                                                   , dao_fac        = dao_fac)  

    ##
    ### GENERATE EARNINGS SECTION
    ##
    report_section_earnings.generate_report_section(session_id     = session_id
                                                  , search_term    = validated_search_term
                                                  , report_context = report_context
                                                  , properties     = properties 
                                                  , dao_fac        = dao_fac)  


    ##
    ### GENERATE CRIME SECTION
    ##
    report_section_crime.generate_report_section(session_id     = session_id
                                               , search_term    = validated_search_term
                                               , report_context = report_context
                                               , properties     = properties 
                                               , dao_fac        = dao_fac)  

    
    ##
    ## GENERATE THE MAP FOR THE REPORT
    ##
    ### Create a KWARGS for THIS
    ##
    include_map = True
    if "include_map" in report_context:
      include_map = report_context["include_map"]
      log.debug(f"Using value from report_context for include_map:{include_map}")
      
    if include_map:
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

    # report_type_manager.generate_report_artefacts(session_id     = session_id
    #                                             , report_context = report_context
    #                                             , properties     = properties )    
    
    ###
    ### GENERATE THE REPORT
    ###
    generated_report = report_manager.generate_report(session_id=session_id
                                                    , report_context=report_context
                                                    , properties=properties)
    
    log.debug(f"returning generated_report:{generated_report}")
    return generated_report


