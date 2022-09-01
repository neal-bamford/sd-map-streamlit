import logging
import os
import uuid

from lib import file_tools as ft
from lib import masters_data_analytics_lib as mlib
from data.daos import dao_facade_local as dao_fac
from managers import sd_report_type_dev_data_manager as data_manager
from managers import sd_report_type_dev_report_manager as report_type_manager
from managers import sd_report_manager_new as report_manager

log = logging.getLogger(__name__)

### This is the process for this report
template_processor_file_name = "./reports/processors/sd_new_manager_template.json"
log.debug(f"template_processor_file_name:{template_processor_file_name}")


def generate_report(session_id
                  , search_term
                  , report_context
                  , properties
                  , lib=mlib
                  , dao_fac=dao_fac):
    
    ##
    ## GENERATE THE DATA FOR THE REPORT
    ##
    data_manager.generate_report_data(session_id                    = session_id
                                    , search_term                   = search_term
                                    , report_context                = report_context
                                    , properties                    = properties)
    
    ###
    ### CREATE THE PARTS FOR THE REPORT FROM THE DATA
    ###
    report_type_manager.generate_report_artefacts(session_id     = session_id
                                                , report_context = report_context
                                                , properties     = properties)    
    
    ###
    ### GENERATE THE REPORT
    ###
    report_context["template_processor_file_name"] = template_processor_file_name
    generated_report = report_manager.generate_report(session_id=session_id
                                             , report_context=report_context
                                             , properties=properties)
    
    log.debug(f"returning generated_report:{generated_report}")
    return generated_report
