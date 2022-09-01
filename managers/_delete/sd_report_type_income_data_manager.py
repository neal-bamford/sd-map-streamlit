from lib import db_tools as db_tools
from lib import formatting as fmt
from lib import general_tools as gen_tools
from lib import masters_data_analytics_lib as mlib
from lib import plot_tools as plttool
from lib import stats as stats
from data.daos import location_dao as loc_dao
from lib import general_tools as gen_tools

import logging
import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

def generate_report_data(session_id
					   , search_term
					   , report_context
				   	 , properties
					   , **kwargs):  
	"""
	Manager to create the formatted String data to include in the sd_general_report_data
	"""
	
	## These are the pandas dataframes used in this manager. They may be used in others too
	sd_london_postcodes_df         = kwargs["sd_london_postcodes_df"]
	sd_london_population_oa_df     = kwargs["sd_london_population_oa_df"]
	sd_london_household_oa_df      = kwargs["sd_london_household_oa_df"]
	sd_london_qualification_oa_df  = kwargs["sd_london_qualification_oa_df"] 

	## Validate the search term	
	validated_search_term = loc_dao.location_search(search_term, sd_london_postcodes_df)
	## Merge any non validated values with validated ones for future use	
	validated_search_term = gen_tools.merge_two_dicts(search_term, validated_search_term)
	
	## Merge any non validated values with validated ones for future use	
	validated_search_term = gen_tools.merge_two_dicts(search_term, validated_search_term)
	report_context["validated_search_term"] = validated_search_term

	
	city      = validated_search_term["city"]
	borough   = validated_search_term["borough"]
	ward_name = validated_search_term["ward_name"]
	oacode    = validated_search_term["oacode"]
	post_code = validated_search_term["post_code"]
	
	year_from = validated_search_term["year_from"]
	year_to   = validated_search_term["year_to"]
	
	## These need to be behind DAOs
	all_ward_post_codes = loc_dao.list_post_codes_for_borough_ward_name(borough, ward_name, sd_london_postcodes_df)
	all_borough_wards   = loc_dao.list_wards_for_borough(borough, sd_london_postcodes_df)
	
	other_post_codes = all_ward_post_codes
	if post_code != "":
		other_post_codes = np.delete(all_ward_post_codes, np.where(all_ward_post_codes == post_code))
	
	other_wards = np.delete(all_borough_wards, np.where(all_borough_wards == ward_name))
	number_of_boroughs = len(loc_dao.list_boroughs_for_city(city, sd_london_postcodes_df))

	map_args = {}
	
	if post_code != "":
		post_code_combined = loc_dao.list_lat_long_postcode(validated_search_term, sd_london_postcodes_df)
		map_args["post_code"] = {"label":post_code, "lat_long":post_code_combined}
	
	ward_name_combined = loc_dao.list_lat_long_ward_name(validated_search_term, sd_london_postcodes_df)
	map_args["ward_name"] = {"label":ward_name, "lat_long":ward_name_combined}

	borough_combined = loc_dao.list_lat_long_borough(validated_search_term, sd_london_postcodes_df)
	map_args["borough"] = {"label":borough, "lat_long":borough_combined}

	report_context["map_args"] = map_args
