from data.daos import dao_facade_local as dao_fac
from lib import db_tools as db_tools
from lib import formatting as sd_formatting
from lib import masters_data_analytics_lib as mlib
from lib import stats as stats
from matplotlib.colors import ListedColormap 
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)

import colorcet as cc
import config_logging
import logging
import numpy as np
import pandas as pd
import pyodbc 
import toml
import urllib.request

log = logging.getLogger(__name__)

def validate_search(session_id
                  , search_term
                  , report_context
                  , properties
                  , lib=mlib
                  , dao_fac=dao_fac):
  
  from lib import db_tools as db_tools
  from lib import general_tools as gen_tools

  year_from = search_term["year_from"]
  year_to   = search_term["year_to"]
  
  city      = search_term["city"]
  ward_name = search_term["ward_name"]
  borough   = search_term["borough"]
  post_code = search_term["post_code"]
  
  db_conn = db_tools.get_db_conn(properties[properties["database"]["flavour"]] )
  
  ## Retrieve the postcode and coordinate data - needs to move to the database
  sd_london_postcodes_df = dao_fac.post_codes_coords(search_term, search_term)
  
  ## Validate the search terms
  validated_search_term = dao_fac.location_search(search_term, sd_london_postcodes_df)
  
  if year_to < year_from:
      raise Exception(f"year_to:{year_to} can not be less than year_to:{year_from}")
  
  validated_search_term = gen_tools.merge_two_dicts(search_term, validated_search_term)
  map_args={}
  
  ## Build the data for the map search
  if post_code != "":
      post_code_lat_long_combined = dao_fac.list_lat_long_postcode(validated_search_term, sd_london_postcodes_df)
      map_args["post_code"] = {"label":post_code, "lat_long":post_code_lat_long_combined}
  
  ward_name_lat_long_combined = dao_fac.list_lat_long_ward_name(validated_search_term, sd_london_postcodes_df)
  map_args["ward_name"] = {"label":ward_name, "lat_long":ward_name_lat_long_combined}
  
  borough_lat_long_combined = dao_fac.list_lat_long_borough(validated_search_term, sd_london_postcodes_df)
  map_args["borough"] = {"label":borough, "lat_long":borough_lat_long_combined}
  
  ## Add it all to the search context
  report_context["validated_search_term"] = validated_search_term
  report_context["map_args"] = map_args
  
  return validated_search_term