from lib import stats as stats
from lib import formatting as fmt
from lib import plot_tools as plttool
from lib import masters_data_analytics_lib as mlib
from data.daos import location_dao as loc_dao

import numpy as np
import pandas as pd


def generate_report_artefacts(session_id
            # , search_term
					       , report_context
				   	       , properties
					       , **kwargs):  
	"""
	Manager to create the formatted String data to include in the sd_general_report_data
	"""
	
	## These are the pandas dataframes used in this manager. They may be used in others too
 # sd_london_postcodes_df         = kwargs["sd_london_postcodes_df"]
 # sd_london_population_oa_df     = kwargs["sd_london_population_oa_df"]
 # sd_london_household_oa_df      = kwargs["sd_london_household_oa_df"]
 # sd_london_qualification_oa_df  = kwargs["sd_london_qualification_oa_df"] 
	validated_search_term = report_context["validated_search_term"]
	post_code = validated_search_term["post_code"]
  	
	## Choose the column to rank by	
	if post_code != "":
		ranking_column = "oacode_sum"
	else: 
		ranking_column = "ward_sum"
		
	###
	### EDUCATION SECTION
	###
	edu_unknown_stats = report_context["edu_unknown_stats"]
	edu_none_stats	  = report_context["edu_none_stats"]
	edu_level1_stats  = report_context["edu_level1_stats"]
	edu_level2_stats  = report_context["edu_level2_stats"]
	edu_level3_stats  = report_context["edu_level3_stats"]
	edu_level4_stats  = report_context["edu_level4_stats"]
	edu_other_stats   = report_context["edu_other_stats"]
	
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

	report_context["education_01"] = education[0]
	report_context["education_02"] = education[1]
	report_context["education_03"] = education[2]
	report_context["education_04"] = education[3]
	report_context["education_05"] = education[4]
	report_context["education_06"] = education[5]
	
