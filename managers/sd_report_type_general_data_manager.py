from lib import stats as stats
from lib import plot_tools as plttool
from lib import masters_data_analytics_lib as mlib
from data.daos import location_dao as loc_dao

import numpy as np
import pandas as pd

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

	### VALIDATE THE SEARCH TERMS
	validated_search_term = loc_dao.location_search(search_term, sd_london_postcodes_df)
	report_context["validated_search_term"] = validated_search_term
	
	## Use the validated search terms
	city      = validated_search_term["city"]
	borough   = validated_search_term["borough"]
	ward_name = validated_search_term["ward_name"]
	oacode    = validated_search_term["oacode"]
	post_code = validated_search_term["post_code"]


	###
	### LOCATION DATA
	###

	#### POST CODE DATA AT WARD LEVEL	
	all_ward_post_codes = loc_dao.list_post_codes_for_borough_ward_name(borough, ward_name, sd_london_postcodes_df)
	other_post_codes = all_ward_post_codes
	if post_code != "":
		other_post_codes = np.delete(all_ward_post_codes, np.where(all_ward_post_codes == post_code))
	
	### WARD DATA AT BOROUGH LEVEL
	all_borough_wards   = loc_dao.list_wards_for_borough(borough, sd_london_postcodes_df)
	other_wards = np.delete(all_borough_wards, np.where(all_borough_wards == ward_name))
	number_of_boroughs = len(loc_dao.list_boroughs_for_city(city, sd_london_postcodes_df))

	###
	### BUILD THE MAP DATA
	###
	map_args = {}
	
	if post_code != "":
		post_code_lat_long_combined = loc_dao.list_lat_long_postcode(validated_search_term, sd_london_postcodes_df)
		map_args["post_code"] = {"label":post_code, "lat_long":post_code_lat_long_combined}
	
	ward_name_lat_long_combined = loc_dao.list_lat_long_ward_name(validated_search_term, sd_london_postcodes_df)
	map_args["ward_name"] = {"label":ward_name, "lat_long":ward_name_lat_long_combined}

	borough_lat_long_combined = loc_dao.list_lat_long_borough(validated_search_term, sd_london_postcodes_df)
	map_args["borough"] = {"label":borough, "lat_long":borough_lat_long_combined}

	###
	### POPULATION DATA STATS
	###
	pop_all_stats	  = stats.generate_stats(sd_london_population_oa_df, borough, ward_name, oacode, "All")
	pop_male_stats	  = stats.generate_stats(sd_london_population_oa_df, borough, ward_name, oacode, "Males")
	pop_female_stats  = stats.generate_stats(sd_london_population_oa_df, borough, ward_name, oacode, "Females")
	pop_density_stats = stats.generate_stats(sd_london_population_oa_df, borough, ward_name, oacode, "DensityPPH")
	
 # ### Obtain rankings for this compared to others at the borough level
	limit = 5
	pop_top, pop_this, pop_bottom = stats.generate_rankings(sd_london_population_oa_df, borough, "DensityPPH", limit)

	### MALE FEMALE RATIOS
	#### WARD
	pop_male_female_ward_total = pop_male_stats["ward_sum"] + pop_female_stats["ward_sum"]
	pop_male_ward_ratio = round(pop_male_stats["ward_sum"]/pop_male_female_ward_total * 100,0)
	pop_female_ward_ratio = round(pop_female_stats["ward_sum"]/pop_male_female_ward_total * 100,0)
	
	### BOROUGH
	pop_male_female_borough_total = pop_male_stats["borough_sum"] + pop_female_stats["borough_sum"]
	pop_male_borough_ratio = round(pop_male_stats["borough_sum"]/pop_male_female_borough_total * 100,0)
	pop_female_borough_ratio = round(pop_female_stats["borough_sum"]/pop_male_female_borough_total * 100,0)
	
	### BOROUGH AVERAGE
	pop_male_female_city_borough_total = pop_male_stats["city_sum"] + pop_female_stats["city_sum"]
	pop_male_city_ratio = round(pop_male_stats["city_sum"]/pop_male_female_city_borough_total * 100,0)
	pop_female_city_ratio = round(pop_female_stats["city_sum"]/pop_male_female_city_borough_total * 100,0)
	
	###
	### HOUSEHOLD STATS DATA
	###
	hous_commerical_stats = stats.generate_stats(sd_london_household_oa_df, borough, ward_name, oacode, "CommercialBuilding")
	hous_detatched_stats  = stats.generate_stats(sd_london_household_oa_df, borough, ward_name, oacode, "Detached")
	hous_flat_stats	      = stats.generate_stats(sd_london_household_oa_df, borough, ward_name, oacode, "Flat")
	hous_semi_stats	      = stats.generate_stats(sd_london_household_oa_df, borough, ward_name, oacode, "Semi_detached")
	hous_terraced_stats   = stats.generate_stats(sd_london_household_oa_df, borough, ward_name, oacode, "Terraced")
	
	###
	### EDUCATION STATS DATA
	###
	edu_unknown_stats = stats.generate_stats(sd_london_qualification_oa_df, borough, ward_name, oacode, "UnkownQualification")
	edu_none_stats	  = stats.generate_stats(sd_london_qualification_oa_df, borough, ward_name, oacode, "NoQualification")
	edu_level1_stats  = stats.generate_stats(sd_london_qualification_oa_df, borough, ward_name, oacode, "Level1")
	edu_level2_stats  = stats.generate_stats(sd_london_qualification_oa_df, borough, ward_name, oacode, "Level2")
	edu_level3_stats  = stats.generate_stats(sd_london_qualification_oa_df, borough, ward_name, oacode, "Level3")
	edu_level4_stats  = stats.generate_stats(sd_london_qualification_oa_df, borough, ward_name, oacode, "Level4")
	edu_other_stats   = stats.generate_stats(sd_london_qualification_oa_df, borough, ward_name, oacode, "OtherQualifications")
	
	###
	### PLACE ALL THE STATS COLLECTED INTO THE REPORT_CONTEXT
	###
	report_context["all_ward_post_codes"] = all_ward_post_codes
	report_context["all_borough_wards"] = all_borough_wards
	report_context["other_post_codes"] = other_post_codes
	report_context["other_wards"] = other_wards
	report_context["number_of_boroughs"] = number_of_boroughs
	report_context["map_args"] = map_args
	report_context["pop_all_stats"] = pop_all_stats
	report_context["pop_male_stats"] = pop_male_stats
	report_context["pop_female_stats"] = pop_female_stats
	report_context["pop_density_stats"] = pop_density_stats
	report_context["pop_top"] = pop_top
	report_context["pop_this"] = pop_this
	report_context["pop_bottom"] = pop_bottom
	report_context["pop_male_ward_ratio"] = pop_male_ward_ratio
	report_context["pop_female_ward_ratio"] = pop_female_ward_ratio
	report_context["pop_male_borough_ratio"] = pop_male_borough_ratio
	report_context["pop_female_borough_ratio"] = pop_female_borough_ratio
	report_context["pop_male_city_ratio"] = pop_male_city_ratio
	report_context["pop_female_city_ratio"] = pop_female_city_ratio
	report_context["hous_commerical_stats"] = hous_commerical_stats
	report_context["hous_detatched_stats"] = hous_detatched_stats
	report_context["hous_flat_stats"] = hous_flat_stats
	report_context["hous_semi_stats"] = hous_semi_stats
	report_context["hous_terraced_stats"] = hous_terraced_stats
	report_context["edu_unknown_stats"] = edu_unknown_stats
	report_context["edu_none_stats"] = edu_none_stats
	report_context["edu_level1_stats"] = edu_level1_stats
	report_context["edu_level2_stats"] = edu_level2_stats
	report_context["edu_level3_stats"] = edu_level3_stats
	report_context["edu_level4_stats"] = edu_level4_stats
	report_context["edu_other_stats"] = edu_other_stats

