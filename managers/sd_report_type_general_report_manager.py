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

  all_ward_post_codes = report_context["all_ward_post_codes"]
  all_borough_wards   = report_context["all_borough_wards"]
  other_post_codes    = report_context["other_post_codes"]
  other_wards         = report_context["other_wards"]
  number_of_boroughs  = report_context["number_of_boroughs"]

  ###
  ### LOCATION SECTION
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
    
  ## Choose the column to rank by  
  if post_code != "":
    ranking_column = "oacode_sum"
  else: 
    ranking_column = "ward_sum"
    
  ###
  ### POPULATION SECTION
  ###
  pop_all_stats = report_context["pop_all_stats"] 
  pop_male_stats = report_context["pop_male_stats"] 
  pop_female_stats = report_context["pop_female_stats"] 
  pop_density_stats = report_context["pop_density_stats"] 
  
  pop_top = report_context["pop_top"] 
  pop_this = report_context["pop_this"]
  pop_bottom = report_context["pop_bottom"]

  ### Stats for the searched for borough    
  population_field_01_part_01 = "The population density of {} is ranked {:g} of {} at {:.2f}" \
       .format(borough, pop_this["rank"].values[0], number_of_boroughs, round(pop_this["total"].values[0], 2))
  
  population_field_01_part_02 = "which is {} the average borough population density of {:.2f}.".format("above" if round(pop_this["total"].values[0], 2) > pop_density_stats["borough_mean"] else "below", pop_density_stats["borough_mean"])
  
  ### If it's not the first then display the first
  population_field_01_part_03 = ""
  
  if pop_this["rank"].values[0] != 1:
      population_field_01_part_03 = "{} has the highest population density at {:.2f}." \
           .format(pop_top.iloc[0]["borough"], round(pop_top.iloc[0]["total"]), 2)
  
  population_field_01_part_04 = ""
  
  if pop_this["rank"].values[0] != number_of_boroughs:
      population_field_01_part_04 ="{} has the lowest population density at {:.2f}." \
           .format(pop_bottom.iloc[-1]["borough"], round(pop_bottom.iloc[-1]["total"]), 2)

  #### GENDER      
  pop_male_ward_ratio = report_context["pop_male_ward_ratio"]
  pop_female_ward_ratio = report_context["pop_female_ward_ratio"]
  
  pop_male_borough_ratio = report_context["pop_male_borough_ratio"] 
  pop_female_borough_ratio = report_context["pop_female_borough_ratio"]

  pop_male_city_ratio = report_context["pop_male_city_ratio"]
  pop_female_city_ratio = report_context["pop_female_city_ratio"]

  #### WARD LEVEL
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
 
  ### BOROUGH LEVEL
  population_field_01_part_07 = ""
  ### What to print
  if pop_male_borough_ratio > pop_female_borough_ratio:
    population_field_01_part_07 = "Males account for {:g}% of the borough population, which is {} the average of {:g}% at borough level. Females account for {:g}% which is {} the average of {:g}% at borough level."\
       .format(pop_male_borough_ratio, fmt.hls_str(pop_male_borough_ratio, pop_male_city_ratio), \
           pop_male_city_ratio, pop_female_borough_ratio, fmt.hls_str(pop_female_borough_ratio, pop_female_city_ratio), pop_female_city_ratio)
 
  elif pop_male_borough_ratio < pop_female_borough_ratio:
    population_field_01_part_07 = "Females account for {:g}% of the borough population, which is {} the average of {:g}% at borough level. Males account for {:g}% which is {} the average of {:g}% at borough level."\
       .format(pop_female_borough_ratio, fmt.hls_str(pop_female_borough_ratio, pop_female_city_ratio),\
           pop_female_city_ratio, pop_male_borough_ratio, fmt.hls_str(pop_male_borough_ratio, pop_male_city_ratio), pop_male_city_ratio)
  else:
    population_field_01_part_07 ="Males and females are equal for the borough. The borough level average is males {:g}% and females {:g}%."\
       .format(pop_male_city_ratio, pop_female_city_ratio)
 
  ### COMBINED
  population_field_01 = population_field_01_part_01 + " " +  \
              population_field_01_part_02 + " " +  \
              population_field_01_part_03 + " " +  \
              population_field_01_part_04 + " " +  \
              population_field_01_part_06 + " " +  \
              population_field_01_part_07    
     
  ###
  ### POPULATION PLOTS
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
  
  ###
  ### HOUSEHOLD SECTION
  ###
  hous_commerical_stats = report_context["hous_commerical_stats"]
  hous_detatched_stats = report_context["hous_detatched_stats"]
  hous_flat_stats = report_context["hous_flat_stats"]
  hous_semi_stats = report_context["hous_semi_stats"]
  hous_terraced_stats = report_context["hous_terraced_stats"]
    
  ## Create a data frame of the findings
  household_location_stats_columns = ["household_type", "d_nd", "oacode_sum", "ward_sum", "borough_sum", "city_borough_mean", "city_sum" ]
  household_location_stats_data    = [
                                        [   "commercial", "nd", hous_commerical_stats["oacode_sum"], hous_commerical_stats["ward_sum"], hous_commerical_stats["borough_sum"], hous_commerical_stats["borough_mean"], hous_commerical_stats["city_sum"]],
                                        [     "detached",  "d",  hous_detatched_stats["oacode_sum"],  hous_detatched_stats["ward_sum"],  hous_detatched_stats["borough_sum"],  hous_detatched_stats["borough_mean"],  hous_detatched_stats["city_sum"]],
                                        [         "flat",  "d",       hous_flat_stats["oacode_sum"],       hous_flat_stats["ward_sum"],       hous_flat_stats["borough_sum"],       hous_flat_stats["borough_mean"],       hous_flat_stats["city_sum"]],
                                        ["semi-detached",  "d",       hous_semi_stats["oacode_sum"],       hous_semi_stats["ward_sum"],       hous_semi_stats["borough_sum"],       hous_semi_stats["borough_mean"],       hous_semi_stats["city_sum"]],
                                        [     "terraced",  "d",   hous_terraced_stats["oacode_sum"],   hous_terraced_stats["ward_sum"],   hous_terraced_stats["borough_sum"],   hous_terraced_stats["borough_mean"],   hous_terraced_stats["city_sum"]]
                                       ]

  household_location_stats_df = pd.DataFrame(household_location_stats_data, columns=household_location_stats_columns)
    
  ## Remove the non dwelling data i.e. Commercial buildings
  ## And sort descending
  household_location_d_stats_df = household_location_stats_df.loc[household_location_stats_df["d_nd"] == "d"]
  household_location_d_stats_df = household_location_d_stats_df.sort_values(by=[ranking_column], ascending=False)
    
  ## Build the report text
  house_hold = []
  household_type_pretty = {"detached":"Detached", "flat":"Flat", "semi-detached":"Semi Detached", "terraced":"Terraced"}
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
  ### EDUCATION SECTION
  ###
  edu_unknown_stats = report_context["edu_unknown_stats"]
  edu_none_stats    = report_context["edu_none_stats"]
  edu_level1_stats  = report_context["edu_level1_stats"]
  edu_level2_stats  = report_context["edu_level2_stats"]
  edu_level3_stats  = report_context["edu_level3_stats"]
  edu_level4_stats  = report_context["edu_level4_stats"]
  edu_other_stats   = report_context["edu_other_stats"]
  
  ## Create a data frame of the findings
  qualification_location_stats_columns = ["qualification_type", "oacode_sum", "ward_sum", "borough_sum", "city_borough_mean", "city_sum" ]
  qualification_location_stats_data  = [
                      [  "no_qualification",       edu_none_stats["oacode_sum"],   edu_none_stats["ward_sum"],   edu_none_stats["borough_sum"],   edu_none_stats["borough_mean"],   edu_none_stats["city_sum"]],
                      [        "level1",     edu_level1_stats["oacode_sum"], edu_level1_stats["ward_sum"], edu_level1_stats["borough_sum"], edu_level1_stats["borough_mean"], edu_level1_stats["city_sum"]],
                      [        "level2",     edu_level2_stats["oacode_sum"], edu_level2_stats["ward_sum"], edu_level2_stats["borough_sum"], edu_level2_stats["borough_mean"], edu_level2_stats["city_sum"]],
                      [        "level3",     edu_level3_stats["oacode_sum"], edu_level3_stats["ward_sum"], edu_level3_stats["borough_sum"], edu_level3_stats["borough_mean"], edu_level3_stats["city_sum"]],
                      [        "level4",     edu_level4_stats["oacode_sum"], edu_level4_stats["ward_sum"], edu_level4_stats["borough_sum"], edu_level4_stats["borough_mean"], edu_level4_stats["city_sum"]],
                      ["other_qualifications",      edu_other_stats["oacode_sum"],  edu_other_stats["ward_sum"],  edu_other_stats["borough_sum"],  edu_other_stats["borough_mean"],  edu_other_stats["city_sum"]]
                       ]
  
  qualification_location_stats_df = pd.DataFrame(qualification_location_stats_data, columns=qualification_location_stats_columns)
  
  ## Sort descending
  qualification_location_stats_df = qualification_location_stats_df.sort_values(by=[ranking_column], ascending=False)
  
  ## Build the report text
  education = []
  qualification_type_pretty = {"no_qualification":"No qualifications", "level1":"Level 1", "level2":"Level 2", "level3":"Level 3", "level4":"Level 4", "other_qualifications":"Other qualifications"}
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
  ### ALL THE FORMATTED TEXT AND PLOT FILES TO GO INTO THE REPORT GENERATION
  ###
  report_context["city"] = city.capitalize()
  report_context["ward_name"] = ward_name
  report_context["borough"] = borough
  report_context["post_code"] = post_code
  report_context["post_code_or_ward_name"] = post_code if post_code != "" else ward_name

  report_context["location_field_01"] = location_field_01
  report_context["population_field_01"] = population_field_01
  report_context["population_mekko_plot_gender"] = mekko_gender_borough_plot_file

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
  
