from lib import stats as stats
from lib import formatting as fmt
from lib import plot_tools as plttool
from lib import masters_data_analytics_lib as mlib

import numpy as np
import pandas as pd


### Simple text formatting function
def hls_str(r1, r2):
	return "higher than" if r1 > r2 else "lower than" if r1 < r2 else "the same as"

def generate_report_data(city		 # passed in, here to accommodate even though only London data
                       , search_term # post_code, ward_name or borough
		               , session_id  # to make files unique within a user's session
					   , **kwargs    # to allow for multiple values
					    ):  
	"""
	Manager to create the formatted String data to include in the sd_general_report_data
	"""
	
	## These are the pandas dataframes used in this manager. They may be used in others too
	sd_london_population_oa_df     = kwargs["sd_london_population_oa_df"]
	sd_london_postcodes_df         = kwargs["sd_london_postcodes_df"]
	sd_london_household_oa_df      = kwargs["sd_london_household_oa_df"]
	sd_london_qualification_oa_df  = kwargs["sd_london_qualification_oa_df"] 
	
	## Search via the search_term, start from post_code
	
	try:
		OAcode = sd_london_postcodes_df.loc[sd_london_postcodes_df["Post_Code"] == search_term]["OAcode"].values[0]
	except:
		raise Exception("Unable to find post code {}".format(search_term))
	
	other_post_codes = sd_london_postcodes_df.loc[sd_london_postcodes_df["OAcode"] == OAcode]["Post_Code"].to_numpy()
	other_post_codes = np.delete(other_post_codes, np.where(other_post_codes == search_term))
	number_of_boroughs = len(sd_london_postcodes_df["borough"].unique())
	
	
	## Obtain the ward_name from the OACode
	ward_name = sd_london_postcodes_df.loc[sd_london_postcodes_df["OAcode"] == OAcode]["WARD_NAME"].values[0]
	borough   = sd_london_postcodes_df.loc[sd_london_postcodes_df['OAcode'] == OAcode]["borough"].values[0]
	
	other_wards = sd_london_postcodes_df.loc[sd_london_postcodes_df["borough"] == borough]["WARD_NAME"]
	other_wards = other_wards.unique()
	other_wards = np.delete(other_wards, np.where(other_wards == borough))
	
	post_code_search_longitude = sd_london_postcodes_df.loc[sd_london_postcodes_df["Post_Code"] == search_term]["longitude"].to_numpy()
	post_code_search_latitude = sd_london_postcodes_df.loc[sd_london_postcodes_df["Post_Code"] == search_term]["latitude"].to_numpy()

	pc_longitudes = sd_london_postcodes_df.loc[sd_london_postcodes_df["borough"] == borough]["longitude"].to_numpy()
	pc_latitudes  = sd_london_postcodes_df.loc[sd_london_postcodes_df["borough"] == borough]["latitude"].to_numpy()


	###
	### Location
	###
	location_field_01 = "The post code {} belongs to the ward {} and borough {} within the city of {}. There {} {} other post code{} which the following data is part of. {} being {}. There are {} other ward{} in the borough which are {}" \
                       .format(search_term
							 , ward_name
							 , borough
							 , city.capitalize()
							 , ("are" if len(other_post_codes)>1 else "is")
							 , len(other_post_codes)
							 , ("s" if len(other_post_codes) > 1 else "")
							 , ("These" if len(other_post_codes)>1 else "This")
							 , fmt.series_format(other_post_codes)
							 , len(other_wards)
							 , ("s" if len(other_wards) > 1 else "")
							 , fmt.series_format(other_wards))
	
	###
	### Population
	###
	pop_all_stats	  = stats.generate_stats(sd_london_population_oa_df, borough, ward_name, OAcode, "All")
	pop_male_stats	  = stats.generate_stats(sd_london_population_oa_df, borough, ward_name, OAcode, "Males")
	pop_female_stats  = stats.generate_stats(sd_london_population_oa_df, borough, ward_name, OAcode, "Females")
	pop_density_stats = stats.generate_stats(sd_london_population_oa_df, borough, ward_name, OAcode, "DensityPPH")

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
		population_field_01_part_03 = "{} has the highest population density at {:.2f}" \
			 .format(top.iloc[0]["borough"], round(top.iloc[0]["total"]), 2)
	
	population_field_01_part_04 = ""
	
	if this["rank"].values[0] != number_of_boroughs:
		population_field_01_part_04 ="{} has the lowest population density at {:.2f}." \
			 .format(bottom.iloc[-1]["borough"], round(bottom.iloc[-1]["total"]), 2)
		
	### Male female ratio
	pop_male_female_borough_total = pop_male_stats["borough_sum"] + pop_female_stats["borough_sum"]
	pop_male_ratio = round(pop_male_stats["borough_sum"]/pop_male_female_borough_total * 100,0)
	pop_female_ratio = round(pop_female_stats["borough_sum"]/pop_male_female_borough_total * 100,0)
	
	pop_male_female_city_borough_total = pop_male_stats["city_sum"] + pop_female_stats["city_sum"]
	pop_male_city_ratio = round(pop_male_stats["city_sum"]/pop_male_female_city_borough_total * 100,0)
	pop_female_city_ratio = round(pop_female_stats["city_sum"]/pop_male_female_city_borough_total * 100,0)

	###
	### Create a Mekko Chart of the ratios at borough and average borough level for population gender ratio
	###
	from lib import plot_tools as plt_tool
	data = [pop_male_ratio, pop_male_city_ratio, pop_female_ratio, pop_female_city_ratio]
	names = ["borough", "borough average"]
	categories = ["male", "female"]
	title = "Gender Population - Borough and Borough Average"
	mekko_gender_borough_plot_file = "./reports/generation/images/{}_mekko_gender_borough_{}_{}_{}.png".format(session_id, city, borough, ward_name)
	mekko_chart_file = plttool.mekko_chart(data=data, names=names, categories=categories, title=title) 
	mlib.save_plot_filename(plot=mekko_chart_file, filename=mekko_gender_borough_plot_file, save_artefacts=True)
	
	###
	### Create text for population
	### 
	population_field_01_part_05 = ""
	### What to print
	if pop_male_ratio > pop_female_ratio:
		population_field_01_part_05 = "Males account for {:g}% of the borough population, which is {} the average of {:g}% at borough level. Females account for {:g}% which is {} the average of {:g}% at borough level."\
			 .format(pop_male_ratio, hls_str(pop_male_ratio, pop_male_city_ratio), \
					 pop_male_city_ratio, pop_female_ratio, hls_str(pop_female_ratio, pop_female_city_ratio), pop_female_city_ratio)
			 
	elif pop_male_ratio < pop_female_ratio:
		population_field_01_part_05 = "Females account for {:g}% of the borough population, which is {} the average of {:g}% at borough level. Males account for {:g}% which is {} the average of {:g}% at borough level."\
			 .format(pop_female_ratio, hls_str(pop_female_ratio, pop_female_city_ratio),\
					 pop_female_city_ratio, pop_male_ratio, hls_str(pop_male_ratio, pop_male_city_ratio), pop_male_city_ratio)
	else:
		population_field_01_part_05 ="Males and females are equal for the borough. The borough level average is males {:g}% and females {:g}%."\
			 .format(pop_male_city_ratio, pop_female_city_ratio)

	### Combine for the report
	population_field_01 = population_field_01_part_01 + " " +  \
						  population_field_01_part_02 + " " +  \
						  population_field_01_part_03 + " " +  \
						  population_field_01_part_04 + " " +  \
						  population_field_01_part_05		

	###
	### Household
	###
	hous_commerical_stats = stats.generate_stats(sd_london_household_oa_df, borough, ward_name, OAcode, "CommercialBuilding")
	hous_detatched_stats  = stats.generate_stats(sd_london_household_oa_df, borough, ward_name, OAcode, "Detached")
	hous_flat_stats	      = stats.generate_stats(sd_london_household_oa_df, borough, ward_name, OAcode, "Flat")
	hous_semi_stats	      = stats.generate_stats(sd_london_household_oa_df, borough, ward_name, OAcode, "Semi_detached")
	hous_terraced_stats   = stats.generate_stats(sd_london_household_oa_df, borough, ward_name, OAcode, "Terraced")

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
	household_location_d_stats_df = household_location_d_stats_df.sort_values(by=["oacode_sum"], ascending=False)
	
	household_type_pretty = {"detached":"Detached", "flat":"Flat", "semi-detached":"Semi Detached", "terraced":"Terraced"}
	
	house_hold = []
	for i in range(0, 4):
		str = "{} - OAcode:{} - ward:{} - borough:{} - borough avg:{}".format(household_type_pretty[household_location_d_stats_df.iloc[i]["household_type"]], \
																			   household_location_d_stats_df.iloc[i]["oacode_sum"], \
																			   household_location_d_stats_df.iloc[i]["ward_sum"],   \
																			   household_location_d_stats_df.iloc[i]["borough_sum"],   \
																			   household_location_d_stats_df.iloc[i]["city_borough_mean"],   \
																			  )
		house_hold.append(str)
		
	###
	### Education
	###
	edu_unknown_stats = stats.generate_stats(sd_london_qualification_oa_df, borough, ward_name, OAcode, "UnkownQualification")
	edu_none_stats	  = stats.generate_stats(sd_london_qualification_oa_df, borough, ward_name, OAcode, "NoQualification")
	edu_level1_stats  = stats.generate_stats(sd_london_qualification_oa_df, borough, ward_name, OAcode, "Level1")
	edu_level2_stats  = stats.generate_stats(sd_london_qualification_oa_df, borough, ward_name, OAcode, "Level2")
	edu_level3_stats  = stats.generate_stats(sd_london_qualification_oa_df, borough, ward_name, OAcode, "Level3")
	edu_level4_stats  = stats.generate_stats(sd_london_qualification_oa_df, borough, ward_name, OAcode, "Level4")
	edu_other_stats   = stats.generate_stats(sd_london_qualification_oa_df, borough, ward_name, OAcode, "OtherQualifications")
	
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
	qualification_location_stats_df = qualification_location_stats_df.sort_values(by=["oacode_sum"], ascending=False)
	
	qualification_type_pretty = {"no_qualification":"No qualifications", "level1":"Level 1", "level2":"Level 2", "level3":"Level 3", "level4":"Level 4", "other_qualifications":"Other qualifications"}
	
	education = []
	for i in range(0, 6):
		str = "{} - OAcode:{} - ward:{} - borough:{} - borough avg:{}".format(qualification_type_pretty[qualification_location_stats_df.iloc[i]["qualification_type"]], \
																			   qualification_location_stats_df.iloc[i]["oacode_sum"], \
																			   qualification_location_stats_df.iloc[i]["ward_sum"],   \
																			   qualification_location_stats_df.iloc[i]["borough_sum"],   \
																			   qualification_location_stats_df.iloc[i]["city_borough_mean"]
																			   )
		education.append(str)	

	## Create the report string to include in the report
	
	report_merge_data = {
	    "post_code_search"    : search_term,
	    "borough"             : borough,
	    "city"                : city.capitalize(),
	    "population_field_01" : population_field_01,
	    "location_field_01"   : location_field_01,
	    "house_hold_01"       : house_hold[0],
	    "house_hold_02"       : house_hold[1],
	    "house_hold_03"       : house_hold[2],
	    "house_hold_04"       : house_hold[3],
	    "education_01"        : education[0],
	    "education_02"        : education[1],
	    "education_03"        : education[2],
	    "education_04"        : education[3],
	    "education_05"        : education[4],
	    "education_06"        : education[5],
	  	"plots" :{"mekko_gender_borough_plot_file":mekko_gender_borough_plot_file}
	    }
	
	
	ret_dict = {
			    "post_code_search_longitude" : post_code_search_longitude
	          , "post_code_search_latitude"  : post_code_search_latitude
	          , "pc_longitudes"              : pc_longitudes
	          , "pc_latitudes"               : pc_latitudes
			  , "city"                       : city.capitalize()
		      , "post_code"                  : search_term
		      , "ward_name"                  : ward_name
			  , "borough"                    : borough
			  , "population_field_01"		 : population_field_01
			  , "location_field_01"          : location_field_01
			  , "house_hold"                 : house_hold
			  , "education"                  : education
			  , "report_merge_data"          : report_merge_data
		      }

	return ret_dict