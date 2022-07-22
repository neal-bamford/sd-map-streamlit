from lib import stats as stats
from lib import formatting as fmt
from lib import plot_tools as plttool
from lib import masters_data_analytics_lib as mlib
from data.daos import location_dao as loc_dao

import logging
import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

def generate_report_artefacts(session_id
                 , report_context
                 , properties
                 , **kwargs):  
  """
  Manager to create the formatted String data to include in the sd_general_report_data
  """
  ## These are the pandas dataframes used in this manager. They may be used in others too
  validated_search_term = report_context["validated_search_term"]
  
  city      = validated_search_term["city"]
  borough   = validated_search_term["borough"]
  ward_name = validated_search_term["ward_name"]
  post_code = validated_search_term["post_code"]
    
  ###
  ### ALL THE FORMATTED TEXT AND PLOT FILES TO GO INTO THE REPORT GENERATION
  ###
  report_context["city"] = city.capitalize()
  report_context["ward_name"] = ward_name
  report_context["borough"] = borough
  report_context["post_code"] = post_code
  report_context["post_code_or_ward_name"] = post_code if post_code != "" else ward_name

  report_context["general_information"] = "Placeholder Text"
  
