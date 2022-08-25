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
import pandas as pd
import pyodbc 
import toml
import urllib.request

log = logging.getLogger(__name__)

def generate_report_section(session_id
                          , search_term
                          , report_context
                          , properties
                          , dao_fac=dao_fac
                          , **kwargs):  

  ## Retrieve values from properties
  save_image_path = properties["save_image"]["path"]
  database_props = properties[properties["database"]["flavour"]] 

  ## Create a DB Connection at the manager level.
  db_conn = db_tools.get_db_conn(database_props)

  ## Get the search terms
  city      = search_term["city"]
  borough   = search_term["borough"]
  ward_name = search_term["ward_name"]
  
  year_from = search_term["year_from"]
  year_to   = search_term["year_to"]
  
  
  ###
  ### FETCH THE DATA
  ###
  
  education_year_from = year_from
  education_year_to   = year_to
  
  # What do we have? We are only using the max for now
  education_min_max_year_df = dao_fac.qualifications_min_max_year(db_conn)
  
  log.debug(education_min_max_year_df)
  
  education_year_min = education_min_max_year_df["MIN_YEAR"].values[0]
  education_year_max = education_min_max_year_df["MAX_YEAR"].values[0]
  
  log.debug(f"education_year_min:{education_year_min}")
  log.debug(f"education_year_max:{education_year_max}")
  
  education_year_from_orig = education_year_from
  education_year_to_orig = education_year_to
  
  if education_year_from < int(education_year_min):
      education_year_from = int(education_year_min)
  elif education_year_from > int(education_year_max):
      education_year_from = int(education_year_max)
  
  if education_year_to > int(education_year_max):
      education_year_to = int(education_year_max)
  elif education_year_to < int(education_year_min):
      education_year_to = int(education_year_min)
  
  log.debug(f"education orig_year_to    :{education_year_to_orig}")
  log.debug(f"education search_year_to  :{education_year_to}")
  
  search_term = {"year_from" : education_year_from,
                   "year_to" : education_year_to,
                   "borough" : borough,
                 "ward_name" : ward_name}
  
  ## City
  education_average_year_df         = dao_fac.education_ratio_average_years(db_conn, search_term)
  ## Borough
  education_by_borough_year_df      = dao_fac.education_ratio_by_borough_years(db_conn, search_term)
  ## Ward
  education_by_borough_ward_year_df = dao_fac.education_ratio_by_borough_ward_years(db_conn, search_term)

  ##
  ##
  
  ## Education Search Range Narrative
  education_narrative_01 = ""
  education_in_not_in = "in" if ((education_year_to >= education_year_from_orig) &
                              (education_year_to <= education_year_to)) else "outside"
  
  education_search_range = f"of {education_year_from_orig} to {education_year_to_orig}" if education_year_from_orig != education_year_to_orig else f"{education_year_to_orig}"
  education_narrative_search_criters = f"Using the latest qualifications data from {education_year_to} which is {education_in_not_in} your search range {education_search_range}"
  
  education_narrative_01 = f"{education_narrative_search_criters}. The table below ranks qualifications in {ward_name}, {borough} and {city}. " + \
  "The ranking is highest to lowest percentage from top to bottom. Where there is a difference in qualification the cell is shaded, a darker " + \
  "shade denotes a difference between borough and ward. Values in [] give the percentage value."  


  ## Borough & Ward
  education_borough_ward_for_year = education_by_borough_ward_year_df.copy()
  education_borough_ward_for_year = education_borough_ward_for_year.drop(["YEAR", "LAD", "LAD_NAME", "WARD_CODE", "WARD_NAME"], axis=1)
  education_borough_ward_for_year = education_borough_ward_for_year.T.copy()
  education_borough_ward_for_year.columns = ["PCT"]
  education_borough_ward_for_year = education_borough_ward_for_year.sort_values(by=["PCT"], ascending=False)
  
  ## Borough
  education_borough_for_year = education_by_borough_year_df[education_by_borough_year_df["LAD_NAME"] == borough].copy()
  education_borough_for_year = education_borough_for_year.drop(["YEAR", "LAD", "LAD_NAME"], axis=1)
  education_borough_for_year = education_borough_for_year.T.copy()
  education_borough_for_year.columns = ["PCT"]
  education_borough_for_year = education_borough_for_year.sort_values(by=["PCT"], ascending=False)
  
  ## City
  education_city_for_year = education_average_year_df.copy()
  education_city_for_year
  education_city_for_year = education_city_for_year.drop(["YEAR"], axis=1)
  education_city_for_year = education_city_for_year.T.copy()
  education_city_for_year.columns = ["PCT"]
  education_city_for_year = education_city_for_year.sort_values(by=["PCT"], ascending=False)
  
  ## Borough Ward
  education_ward_pct_sorted = []
  for index, row in education_borough_ward_for_year.iterrows():
      education     = index
      education_pct = row.values[0]*100
      education_name_pct_fmt = "{} - [{:,.2f}%]".format(education, education_pct)
      education_ward_pct_sorted.append(education_name_pct_fmt)
  
  ## Borough
  education_borough_pct_sorted = []
  for index, row in education_borough_for_year.iterrows():
      education     = index
      education_pct = row.values[0]*100
      education_name_pct_fmt = "{} - [{:,.2f}%]".format(education, education_pct)
      education_borough_pct_sorted.append(education_name_pct_fmt)
  
  ## City
  education_city_pct_sorted = []
  for index, row in     education_city_for_year.iterrows():
      education     = index
      education_pct = row.values[0]*100
      education_name_pct_fmt = "{} - [{:,.2f}%]".format(education, education_pct)
      education_city_pct_sorted.append(education_name_pct_fmt)
  
  education_ward_borough_city_pct_ranked_merged = [education_ward_pct_sorted, education_borough_pct_sorted, education_city_pct_sorted]
  education_ward_borough_city_pct_ranked_merged_df = pd.DataFrame(data=education_ward_borough_city_pct_ranked_merged)
  
  ## Rotate 
  education_ward_borough_city_pct_ranked_merged_df = education_ward_borough_city_pct_ranked_merged_df.T
  education_ward_borough_city_pct_ranked_merged_df.columns = [f"{ward_name}",f"{borough}",f"{city}"]
  education_ward_borough_city_pct_ranked_merged_df.index   = [str(rank) for rank in range(1, len(education_ward_borough_city_pct_ranked_merged_df.index)+1)]
  
  education_ward_borough_city_pct_ranked_merged_df
  
  ##
  ##
  
  education_narrative_02 = ""
  
  # education_level_4_borough_top_2
  
  
  ## Level 4 - top 2 then high
  level_4_education_ward_top_2    = "Level 4" in str(education_ward_borough_city_pct_ranked_merged_df[0:2][ward_name])
  level_4_education_borough_top_2 = "Level 4" in str(education_ward_borough_city_pct_ranked_merged_df[0:2][borough])
  level_4_education_city_top_2 = "Level 4" in str(education_ward_borough_city_pct_ranked_merged_df[0:2][city])
  
  ## None    - top 4 then high
  none_education_ward_top_4     = "None" in str(education_ward_borough_city_pct_ranked_merged_df[0:4][ward_name])
  none_education_borough_top_4  = "None" in str(education_ward_borough_city_pct_ranked_merged_df[0:4][borough])
  none_education_city_top_4  = "None" in str(education_ward_borough_city_pct_ranked_merged_df[0:4][city])
  
  ## FT Student 18+ top 3 then post school student area
  student_education_ward_top_3     = "FT Student 18+" in str(education_ward_borough_city_pct_ranked_merged_df[0:3][ward_name])
  student_education_borough_top_3  = "FT Student 18+" in str(education_ward_borough_city_pct_ranked_merged_df[0:3][borough])
  student_education_city_top_3  = "FT Student 18+" in str(education_ward_borough_city_pct_ranked_merged_df[0:3][city])
  
  ## Build the narrative
  
  ## Level 4 education
  level_4_high         = "" if level_4_education_ward_top_2 else " not"
  level_4_high_similar = "similar" if level_4_education_ward_top_2 == level_4_education_borough_top_2 else "not the same"
  
  # log.debug(f"none_education_ward_top_4:{none_education_ward_top_4}")
  # log.debug(f"none_education_borough_top_4:{none_education_borough_top_4}")
  
  ## Non education
  none_high_ward       = "high" if none_education_ward_top_4 else "low"
  none_also            = "and also" if none_education_ward_top_4 == none_education_borough_top_4 else "but not"
  none_high_borough    = "" if (none_education_ward_top_4 and none_education_borough_top_4) \
                         else " which ranks higher" if none_education_borough_top_4 else "which ranks lower"
  
  ## Student area narrative - ignored if not - Start
  student_area_both_01 = "The ward" if (student_education_ward_top_3 and not student_education_borough_top_3) \
                    else " The borough" if (not student_education_ward_top_3 and student_education_borough_top_3) \
                    else " Both ward and borough"
  
  student_area_both_02 = "the ward is a" if (student_education_ward_top_3 and not student_education_borough_top_3) \
                    else "the borough is a" if (not student_education_ward_top_3 and student_education_borough_top_3) \
                    else "both are"
  
  student_area_both_03 = "" if (student_education_ward_top_3 and not student_education_borough_top_3) \
                    else "" if (not student_education_ward_top_3 and student_education_borough_top_3) \
                    else "s"
  
  ## Student area narrative - ignored if not - End
  
  student_area         = "" if (not student_education_ward_top_3 and not student_education_borough_top_3) \
                            else f"{student_area_both_01} have high levels of full time 18+ students. Indicating that {student_area_both_02} student area{student_area_both_03}."
  
  education_narrative_01 = f"For the borough {borough} and ward {ward_name}, the Level 4 education level (post secondary school including university) " + \
                           f"is{level_4_high} high, which is {level_4_high_similar} at the borough level." + \
                           f" Levels of no education (None) is {none_high_ward} for the ward {none_also} at the borough level{none_high_borough}." + \
                           f"{student_area}"

  report_context["education_narrative_01"] = education_narrative_01
  
  ##
  ##
  
  colour_change = []
  ## 0 == no change in that cell
  ## 1 == shade 1 change
  ## 2 == shade 2 change
  
  for index, row in education_ward_borough_city_pct_ranked_merged_df.iterrows():
      colour_change_row =[]
      
      ## Borough to City Check
      ward_val    = row.iloc[0].split(' - [')[0].strip()
      borough_val = row.iloc[1].split(' - [')[0].strip()
      city_val    = row.iloc[2].split(' - [')[0].strip()
      # log.debug(f"{ward_val}-{borough_val}-{city_val}")
  
      ward_val_cell_col = 0 if ward_val     == city_val else 1 if ward_val == borough_val else 2
      borough_val_col   = 0 if borough_val  == city_val else 1
      cityl_col         = 0
      
      colour_change_row.append(ward_val_cell_col)
      colour_change_row.append(borough_val_col)
      colour_change_row.append(cityl_col)
      colour_change.append(colour_change_row)
  
  def format_ranking_row(row):
      ## Borough to City Check
      ward_val    = row.iloc[0].split(' - [')[0].strip()
      borough_val = row.iloc[1].split(' - [')[0].strip()
      city_val    = row.iloc[2].split(' - [')[0].strip()
      # log.debug(f"{ward_val}-{borough_val}-{city_val}")
  
      ward_val_cell_col = "" if ward_val     == city_val else "background-color: #EAFAF1" if ward_val == borough_val else "background-color: #D5F5E3"
      borough_val_col   = "" if borough_val  == city_val else "background-color: #EAFAF1"
      # log.debug(r[1])
      return [ward_val_cell_col] + [borough_val_col] + [""]
  
  
  from IPython.display import HTML
  styles = [
    dict(selector="tr", props=[("font-size", "110%"),
                               ("text-align", "right")])
  ]
  
  education_ward_borough_city_pct_ranked_merged_df_html = (education_ward_borough_city_pct_ranked_merged_df.style.set_table_styles(styles).apply(format_ranking_row, axis=1))
  
  education_ranking_display_table_file_name = "{}/{}_education_ranking_display_table_{}_{}_{}.png".format(save_image_path, session_id, city, borough, ward_name) 
  mlib.save_df(education_ward_borough_city_pct_ranked_merged_df_html, education_ranking_display_table_file_name, save_artefacts=True)
  report_context["education_ranking_display_table"] = education_ranking_display_table_file_name

  ##
  ##  

  education_borough_ward_for_year_name_sorted = education_borough_ward_for_year.sort_index(ascending=True)
  education_borough_for_year_name_sorted      = education_borough_for_year.sort_index(ascending=True)
  education_city_for_year_name_sorted         = education_city_for_year.sort_index(ascending=True)
  
  education_borough_ward_for_year_name_sorted = education_borough_ward_for_year
  education_borough_for_year_name_sorted      = education_borough_for_year
  education_city_for_year_name_sorted         = education_city_for_year
  
  
  ## Borough Ward
  education_ward_name_sorted = []
  for index, row in education_borough_ward_for_year_name_sorted.iterrows():
      education_pct = row.values[0]*100
      education_pct_fmt = "{:,.2f}%".format(education_pct)
      education_ward_name_sorted.append(education_pct_fmt)
  
  ## Borough
  education_borough_name_sorted = []
  for index, row in education_borough_for_year_name_sorted.iterrows():
      education_pct = row.values[0]*100
      education_pct_fmt = "{:,.2f}%".format(education_pct)
      education_borough_name_sorted.append(education_pct_fmt)
  
  ## City
  education_city_name_sorted = []
  for index, row in education_city_for_year_name_sorted.iterrows():
      education_pct = row.values[0]*100
      education_pct_fmt = "{:,.2f}%".format(education_pct)
      education_city_name_sorted.append(education_pct_fmt)
  
  education_ward_borough_city_pct_name_merged = [education_ward_name_sorted, education_borough_name_sorted, education_city_name_sorted]
  education_ward_borough_city_pct_name_merged_df = pd.DataFrame(data=education_ward_borough_city_pct_name_merged)
  
  ## Rotate 
  education_ward_borough_city_pct_name_merged_df = education_ward_borough_city_pct_name_merged_df.T
  education_ward_borough_city_pct_name_merged_df.columns = [f"{ward_name}",f"{borough}",f"{city}"]
  education_ward_borough_city_pct_name_merged_df.index   = education_borough_ward_for_year_name_sorted.index
  
  education_ward_borough_city_pct_name_merged_df
  
  ##
  ##
  
  def format_pct_row(row):
      
      # log.debug(f"index:{row.name}")
      
      ## Borough to City 
      # name        = row.name
      ward_val    = float(row.iloc[0].split("%")[0].strip())
      borough_val = float(row.iloc[1].split("%")[0].strip())
      city_val    = float(row.iloc[2].split("%")[0].strip())
      
      ## It's more than the city so should be green
      if ward_val >= city_val:
          # log.debug("Ward more so Green")
          diff = ward_val - city_val
          ward_val_cell_col = ""                          if (diff) < 1.0 else \
                              "background-color: #EAFAF1" if (diff) < 2.0 else \
                              "background-color: #D5F5E3" if (diff) < 3.0 else \
                              "background-color: #ABEBC6" if (diff) < 4.0 else \
                              "background-color: #82E0AA" if (diff) < 5.0 else \
                              "background-color: #58D68D"
  
      ## It's less than, so should be red
      else:
          # log.debug("Ward less so Red")
          #-ve then red shades
          diff = city_val - ward_val
          ward_val_cell_col = ""                          if (diff) < 1.0 else \
                              "background-color: #F5EEF8" if (diff) < 2.0 else \
                              "background-color: #EBDEF0" if (diff) < 3.0 else \
                              "background-color: #D7BDE2" if (diff) < 4.0 else \
                              "background-color: #C39BD3" if (diff) < 5.0 else \
                              "background-color: #AF7AC5"
  
      ## It's more than the city so should be green
      if borough_val >= city_val:
          # log.debug("Borough more so Green")
          #+ve then green shades
          diff = borough_val - city_val
          borough_val_col   = ""                          if (diff) < 1.0 else \
                              "background-color: #EAFAF1" if (diff) < 2.0 else \
                              "background-color: #D5F5E3" if (diff) < 3.0 else \
                              "background-color: #ABEBC6" if (diff) < 4.0 else \
                              "background-color: #82E0AA" if (diff) < 5.0 else \
                              "background-color: #58D68D"
  
  
      ## It's less than, so should be red
      else:
          # log.debug("Borough less so Red")
          #-ve then red shades
          diff = city_val - borough_val
          borough_val_col   = ""                          if (diff) < 1.0 else \
                              "background-color: #F5EEF8" if (diff) < 2.0 else \
                              "background-color: #EBDEF0" if (diff) < 3.0 else \
                              "background-color: #D7BDE2" if (diff) < 4.0 else \
                              "background-color: #C39BD3" if (diff) < 5.0 else \
                              "background-color: #AF7AC5"
  
      return [ward_val_cell_col] + [borough_val_col] + [""]
  
  
  from IPython.display import HTML
  styles = [
    dict(selector="tr", props=[("font-size", "110%"),
                               ("text-align", "right")])
  ]
  
  education_ward_borough_city_pct_name_merged_df_html = (education_ward_borough_city_pct_name_merged_df.style.set_table_styles(styles).apply(format_pct_row, axis=1))
  
  education_comparison_display_table_file_name = "{}/{}_education_comparison_display_table_{}_{}_{}.png".format(save_image_path, session_id, city, borough, ward_name) 
  mlib.save_df(education_ward_borough_city_pct_name_merged_df_html, education_comparison_display_table_file_name, save_artefacts=True)
  report_context["educataion_comparison_display_table"] = education_comparison_display_table_file_name

  ##
  ##
  
  education_narrative_02 = f"The table below shows the percentage levels of qualifications achieved in {ward_name}, {borough} and {city} for the year {education_year_to}" + \
  ". Value shading indicates a difference from the city level from 1 to 5 percent in 1 percent intervals." + \
  " The shade darkens with an increase in difference. Increases and decreases use different colours for clarity only."

  report_context["education_narrative_02"] = education_narrative_02

  db_conn.close()
  