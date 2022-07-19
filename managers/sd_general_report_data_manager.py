from lib import stats as stats
from lib import formatting as fmt
from lib import plot_tools as plttool
from lib import masters_data_analytics_lib as mlib
from data.daos import location_dao as loc_dao

import numpy as np
import pandas as pd


### Simple text formatting function
def hls_str(r1, r2):
	return "higher than" if r1 > r2 else "lower than" if r1 < r2 else "the same as"

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

	## Validae the search term	
	validated_result = loc_dao.location_search(search_term, sd_london_postcodes_df)
	
	city      = validated_result["city"]
	borough   = validated_result["borough"]
	ward_name = validated_result["ward_name"]
	oacode    = validated_result["oacode"]
	post_code = validated_result["post_code"]
	
	validated_search_term = {"city"      : city
                           , "borough"   : borough
                           , "ward_name" : ward_name
                           , "post_code" : post_code}

	
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

	###
	### LOCATION
	###
	### We have a post code
	if post_code != "":
		location_field_01 = "The post code {} belongs to the ward {} and borough {} within the city of {}. There {} {} other post code{} which the following data is part of. {} being {}. There are {} other ward{} in the borough which are {}" \
	                       .format(post_code
								 , ward_name
								 , borough
								 , city.capitalize()
								 , ("are" if len(all_ward_post_codes)>1 else "is")
								 , len(other_post_codes)
								 , ("s" if len(other_post_codes) > 1 else "")
								 , ("These" if len(other_post_codes)>1 else "This")
								 , fmt.series_format(other_post_codes)
								 , len(other_wards)
								 , ("s" if len(other_wards) > 1 else "")
								 , fmt.series_format(other_wards))
	### We have ward
	else:
		location_field_01 = "The ward {} belongs to the borough {} within the city of {}. There are {} other ward{} in the borough which are {}" \
	                       .format(ward_name
								 , borough
								 , city.capitalize()
								 , len(other_wards)
								 , ("s" if len(other_wards) > 1 else "")
								 , fmt.series_format(other_wards))
    	
	
	###
	### POPULATION DATA
	###
	pop_all_stats	  = stats.generate_stats(sd_london_population_oa_df, borough, ward_name, oacode, "All")
	pop_male_stats	  = stats.generate_stats(sd_london_population_oa_df, borough, ward_name, oacode, "Males")
	pop_female_stats  = stats.generate_stats(sd_london_population_oa_df, borough, ward_name, oacode, "Females")
	pop_density_stats = stats.generate_stats(sd_london_population_oa_df, borough, ward_name, oacode, "DensityPPH")

	### Obtain rankings for this compared to others at the borough level
	limit = 5
	top, this, bottom = stats.generate_rankings(sd_london_population_oa_df, borough, "DensityPPH", limit)
	
	### Stats for the searched for borough	
	population_field_01_part_01 = "The population density of {} is ranked {:g} of {} at {:.2f}" \
		 .format(borough, this["rank"].values[0], number_of_boroughs, round(this["total"].values[0], 2))

	population_field_01_part_02 = "which is {} the average borough population density of {:.2f}.".format("above" if round(this["total"].values[0], 2) > pop_density_stats["borough_mean"] else "below", pop_density_stats["borough_mean"])

	### If it's not the first then display the first
	population_field_01_part_03 = ""
	
	if this["rank"].values[0] != 1:
		population_field_01_part_03 = "{} has the highest population density at {:.2f}." \
			 .format(top.iloc[0]["borough"], round(top.iloc[0]["total"]), 2)
	
	population_field_01_part_04 = ""
	
	if this["rank"].values[0] != number_of_boroughs:
		population_field_01_part_04 ="{} has the lowest population density at {:.2f}." \
			 .format(bottom.iloc[-1]["borough"], round(bottom.iloc[-1]["total"]), 2)
		
	### Male female ratio
	## Ward
	pop_male_female_ward_total =pop_male_stats["ward_sum"] + pop_female_stats["ward_sum"]
	pop_male_ward_ratio = round(pop_male_stats["ward_sum"]/pop_male_female_ward_total * 100,0)
	pop_female_ward_ratio = round(pop_female_stats["ward_sum"]/pop_male_female_ward_total * 100,0)
	
	## Borough
	pop_male_female_borough_total = pop_male_stats["borough_sum"] + pop_female_stats["borough_sum"]
	pop_male_borough_ratio = round(pop_male_stats["borough_sum"]/pop_male_female_borough_total * 100,0)
	pop_female_borough_ratio = round(pop_female_stats["borough_sum"]/pop_male_female_borough_total * 100,0)
	
	## Borough Average
	pop_male_female_city_borough_total = pop_male_stats["city_sum"] + pop_female_stats["city_sum"]
	pop_male_city_ratio = round(pop_male_stats["city_sum"]/pop_male_female_city_borough_total * 100,0)
	pop_female_city_ratio = round(pop_female_stats["city_sum"]/pop_male_female_city_borough_total * 100,0)

	####
	#### POPULATION TEXT
	#### 
	
	### Ward Level
	population_field_01_part_06 = ""
	### What to print
	if pop_male_ward_ratio > pop_female_ward_ratio:
		population_field_01_part_06 = "Males account for {:g}% of the ward population. Females account for {:g}%."\
			 .format(pop_male_ward_ratio, pop_female_ward_ratio)
			 
	elif pop_male_ward_ratio < pop_female_ward_ratio:
		population_field_01_part_06 = "Females account for {:g}% of the ward population. Males account for {:g}%."\
			 .format(pop_female_ward_ratio, pop_male_ward_ratio)
	else:
		population_field_01_part_06 = "Males and females are equal at the ward level."
	
	### Borough Level
	population_field_01_part_07 = ""
	### What to print
	if pop_male_borough_ratio > pop_female_borough_ratio:
		population_field_01_part_07 = "Males account for {:g}% of the borough population, which is {} the average of {:g}% at borough level. Females account for {:g}% which is {} the average of {:g}% at borough level."\
			 .format(pop_male_borough_ratio, hls_str(pop_male_borough_ratio, pop_male_city_ratio), \
					 pop_male_city_ratio, pop_female_borough_ratio, hls_str(pop_female_borough_ratio, pop_female_city_ratio), pop_female_city_ratio)
			 
	elif pop_male_borough_ratio < pop_female_borough_ratio:
		population_field_01_part_07 = "Females account for {:g}% of the borough population, which is {} the average of {:g}% at borough level. Males account for {:g}% which is {} the average of {:g}% at borough level."\
			 .format(pop_female_borough_ratio, hls_str(pop_female_borough_ratio, pop_female_city_ratio),\
					 pop_female_city_ratio, pop_male_borough_ratio, hls_str(pop_male_borough_ratio, pop_male_city_ratio), pop_male_city_ratio)
	else:
		population_field_01_part_07 ="Males and females are equal for the borough. The borough level average is males {:g}% and females {:g}%."\
			 .format(pop_male_city_ratio, pop_female_city_ratio)

	### Combine for the report
	population_field_01 = population_field_01_part_01 + " " +  \
						  population_field_01_part_02 + " " +  \
						  population_field_01_part_03 + " " +  \
						  population_field_01_part_04 + " " +  \
						  population_field_01_part_06 + " " +  \
						  population_field_01_part_07		
						  
	###
	### Create a Mekko Chart of the ratios at borough and average borough level for population gender ratio
	###
	from lib import plot_tools as plt_tool

	data = [
	        pop_male_ward_ratio
	      , pop_female_ward_ratio
	      , pop_male_borough_ratio
	      , pop_female_borough_ratio
	      , pop_male_city_ratio
	      , pop_female_city_ratio
	]

	names   = ["ward", "borough", "borough average"]
	options = ["male", "female"]
	title   = "Gender Population - Ward, Borough & Borough Average"
	props   = lambda key: {"color": "orange" if "male" in key else "deepskyblue"}
	
	mekko_gender_borough_plot_file = "./reports/generation/images/{}_mekko_gender_borough_{}_{}_{}.png".format(session_id, city, borough, ward_name)
	mekko_chart_file = plt_tool.mekko_chart(data=data, names=names, options=options, title=title, props=props) 
	mlib.save_plot_filename(plot=mekko_chart_file, filename=mekko_gender_borough_plot_file, save_artefacts=True)
						  
	## Choose the column to rank by	
	if post_code != "":
		ranking_column = "oacode_sum"
	else: 
		ranking_column = "ward_sum"


	###
	### HOUSEHOLD
	###
	hous_commerical_stats = stats.generate_stats(sd_london_household_oa_df, borough, ward_name, oacode, "CommercialBuilding")
	hous_detatched_stats  = stats.generate_stats(sd_london_household_oa_df, borough, ward_name, oacode, "Detached")
	hous_flat_stats	      = stats.generate_stats(sd_london_household_oa_df, borough, ward_name, oacode, "Flat")
	hous_semi_stats	      = stats.generate_stats(sd_london_household_oa_df, borough, ward_name, oacode, "Semi_detached")
	hous_terraced_stats   = stats.generate_stats(sd_london_household_oa_df, borough, ward_name, oacode, "Terraced")

	## Create a data frame of the findings
	household_location_stats_columns = ["household_type", "d_nd", "oacode_sum", "ward_sum", "borough_sum", "city_borough_mean", "city_sum" ]
	household_location_stats_data	= [
										[   "commercial", "nd", hous_commerical_stats["oacode_sum"], hous_commerical_stats["ward_sum"], hous_commerical_stats["borough_sum"], hous_commerical_stats["borough_mean"], hous_commerical_stats["city_sum"]],
										[	 "detached",  "d",  hous_detatched_stats["oacode_sum"],  hous_detatched_stats["ward_sum"],  hous_detatched_stats["borough_sum"],  hous_detatched_stats["borough_mean"],  hous_detatched_stats["city_sum"]],
										[		 "flat",  "d",	   hous_flat_stats["oacode_sum"],	   hous_flat_stats["ward_sum"],	   hous_flat_stats["borough_sum"],	   hous_flat_stats["borough_mean"],	   hous_flat_stats["city_sum"]],
										["semi-detached",  "d",	   hous_semi_stats["oacode_sum"],	   hous_semi_stats["ward_sum"],	   hous_semi_stats["borough_sum"],	   hous_semi_stats["borough_mean"],	   hous_semi_stats["city_sum"]],
										[	 "terraced",  "d",   hous_terraced_stats["oacode_sum"],   hous_terraced_stats["ward_sum"],   hous_terraced_stats["borough_sum"],   hous_terraced_stats["borough_mean"],   hous_terraced_stats["city_sum"]]
									   ]

	household_location_stats_df = pd.DataFrame(household_location_stats_data, columns=household_location_stats_columns)
	
	## Remove the non dwelling data i.e. Commercial buildings
	## And sort descending
	household_location_d_stats_df = household_location_stats_df.loc[household_location_stats_df["d_nd"] == "d"]
	household_location_d_stats_df = household_location_d_stats_df.sort_values(by=[ranking_column], ascending=False)
	
	household_type_pretty = {"detached":"Detached", "flat":"Flat", "semi-detached":"Semi Detached", "terraced":"Terraced"}
	
	house_hold = []
	for i in range(0, 4):
		if post_code != "":
			str = "{} - post codes:{} - ward:{} - borough:{} - borough avg:{}".format(
				                                                               household_type_pretty[household_location_d_stats_df.iloc[i]["household_type"]], \
																			   household_location_d_stats_df.iloc[i]["oacode_sum"], \
																			   household_location_d_stats_df.iloc[i]["ward_sum"],   \
																			   household_location_d_stats_df.iloc[i]["borough_sum"],   \
																			   household_location_d_stats_df.iloc[i]["city_borough_mean"],   \
																			   )
		else:
			str = "{} - ward:{} - borough:{} - borough avg:{}".format(
				                                               household_type_pretty[household_location_d_stats_df.iloc[i]["household_type"]], \
															   household_location_d_stats_df.iloc[i]["ward_sum"],   \
															   household_location_d_stats_df.iloc[i]["borough_sum"],   \
															   household_location_d_stats_df.iloc[i]["city_borough_mean"],   \
															   )
			
		house_hold.append(str)
		
	###
	### EDUCATION
	###
	edu_unknown_stats = stats.generate_stats(sd_london_qualification_oa_df, borough, ward_name, oacode, "UnkownQualification")
	edu_none_stats	  = stats.generate_stats(sd_london_qualification_oa_df, borough, ward_name, oacode, "NoQualification")
	edu_level1_stats  = stats.generate_stats(sd_london_qualification_oa_df, borough, ward_name, oacode, "Level1")
	edu_level2_stats  = stats.generate_stats(sd_london_qualification_oa_df, borough, ward_name, oacode, "Level2")
	edu_level3_stats  = stats.generate_stats(sd_london_qualification_oa_df, borough, ward_name, oacode, "Level3")
	edu_level4_stats  = stats.generate_stats(sd_london_qualification_oa_df, borough, ward_name, oacode, "Level4")
	edu_other_stats   = stats.generate_stats(sd_london_qualification_oa_df, borough, ward_name, oacode, "OtherQualifications")
	
	## Create a data frame of the findings
	qualification_location_stats_columns = ["qualification_type", "oacode_sum", "ward_sum", "borough_sum", "city_borough_mean", "city_sum" ]
	qualification_location_stats_data	= [
											[	"no_qualification",		   edu_none_stats["oacode_sum"],   edu_none_stats["ward_sum"],   edu_none_stats["borough_sum"],   edu_none_stats["borough_mean"],   edu_none_stats["city_sum"]],
											[			  "level1",		 edu_level1_stats["oacode_sum"], edu_level1_stats["ward_sum"], edu_level1_stats["borough_sum"], edu_level1_stats["borough_mean"], edu_level1_stats["city_sum"]],
											[			  "level2",		 edu_level2_stats["oacode_sum"], edu_level2_stats["ward_sum"], edu_level2_stats["borough_sum"], edu_level2_stats["borough_mean"], edu_level2_stats["city_sum"]],
											[			  "level3",		 edu_level3_stats["oacode_sum"], edu_level3_stats["ward_sum"], edu_level3_stats["borough_sum"], edu_level3_stats["borough_mean"], edu_level3_stats["city_sum"]],
											[			  "level4",		 edu_level4_stats["oacode_sum"], edu_level4_stats["ward_sum"], edu_level4_stats["borough_sum"], edu_level4_stats["borough_mean"], edu_level4_stats["city_sum"]],
											["other_qualifications",		  edu_other_stats["oacode_sum"],  edu_other_stats["ward_sum"],  edu_other_stats["borough_sum"],  edu_other_stats["borough_mean"],  edu_other_stats["city_sum"]]
										   ]
	
	qualification_location_stats_df = pd.DataFrame(qualification_location_stats_data, columns=qualification_location_stats_columns)
	
	## Sort descending
	qualification_location_stats_df = qualification_location_stats_df.sort_values(by=[ranking_column], ascending=False)
	
	qualification_type_pretty = {"no_qualification":"No qualifications", "level1":"Level 1", "level2":"Level 2", "level3":"Level 3", "level4":"Level 4", "other_qualifications":"Other qualifications"}
	
	education = []
	for i in range(0, 6):
		if post_code != "":
			str = "{} - post codes:{} - ward:{} - borough:{} - borough avg:{}".format(
				                                                               qualification_type_pretty[qualification_location_stats_df.iloc[i]["qualification_type"]], \
																			   qualification_location_stats_df.iloc[i]["oacode_sum"], \
																			   qualification_location_stats_df.iloc[i]["ward_sum"],   \
																			   qualification_location_stats_df.iloc[i]["borough_sum"],   \
																			   qualification_location_stats_df.iloc[i]["city_borough_mean"]
																				   )
		else:
			str = "{} - ward:{} - borough:{} - borough avg:{}".format(qualification_type_pretty[qualification_location_stats_df.iloc[i]["qualification_type"]], \
																				   qualification_location_stats_df.iloc[i]["ward_sum"],   \
																				   qualification_location_stats_df.iloc[i]["borough_sum"],   \
																				   qualification_location_stats_df.iloc[i]["city_borough_mean"]
																				   )
			
		education.append(str)	

	###
	### Place any fields in the template into the report_context along with the value
	###
	report_context["city"] = city.capitalize()
	report_context["ward_name"] = ward_name
	report_context["borough"] = borough
	report_context["post_code"] = post_code

	report_context["post_code_or_ward_name"] = post_code if post_code != "" else ward_name
	report_context["population_field_01"] = population_field_01
	report_context["population_mekko_plot_gender"] = mekko_gender_borough_plot_file
	report_context["location_field_01"] = location_field_01
	report_context["house_hold_01"] = house_hold[0]
	report_context["house_hold_02"] = house_hold[1]
	report_context["house_hold_03"] = house_hold[2]
	report_context["house_hold_04"] = house_hold[3]
	report_context["education_01"] = education[0]
	report_context["education_02"] = education[1]
	report_context["education_03"] = education[2]
	report_context["education_04"] = education[3]
	report_context["education_05"] = education[4]
	report_context["education_06"] = education[5]
	
	report_context["map_args"] = map_args
