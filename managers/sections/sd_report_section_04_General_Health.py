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
  
  health_year_from = year_from
  health_year_to   = year_to
  
  # What do we have? We are only using the max for now
  health_min_max_year_df = dao_fac.general_health_min_max_year(db_conn)
  
  health_year_min = health_min_max_year_df["MIN_YEAR"].values[0]
  health_year_max = health_min_max_year_df["MAX_YEAR"].values[0]
  
  health_year_from_orig = health_year_from
  health_year_to_orig = health_year_to
  
  if health_year_from < int(health_year_min):
      health_year_from = int(health_year_min)
  elif health_year_from > int(health_year_max):
      health_year_from = int(health_year_max)
  
  if health_year_to > int(health_year_max):
      health_year_to = int(health_year_max)
  elif health_year_to < int(health_year_min):
      health_year_to = int(health_year_min)
  
  log.debug(f"health orig_year_to    :{health_year_to_orig}")
  log.debug(f"health search_year_to  :{health_year_to}")
  
  search_term = {"year_from":health_year_from,
                 "year_to":health_year_to,
                 "borough":borough,
                 "ward_name":ward_name}
  
  ## City
  health_average_year_df         = dao_fac.general_health_ratio_average_years(db_conn, search_term)
  ## Borough
  health_by_borough_year_df      = dao_fac.general_health_ratio_by_borough_years(db_conn, search_term)
  ## Ward
  health_by_borough_ward_year_df = dao_fac.general_health_ratio_by_borough_ward_years(db_conn, search_term)
  
  ###
  ### HEALTH NARRATIVE 01 
  ###

  health_narrative_01 = ""
  health_in_not_in = "in" if ((health_year_to >= health_year_from_orig) &
                              (health_year_to <= health_year_to)) else "outside"
  
  health_search_range = f"of {health_year_from_orig} to {health_year_to_orig}" if health_year_from_orig != health_year_to_orig else f"{health_year_to_orig}"
  health_narrative_search_criters = f"Using the latest general health data from {health_year_to} which is {health_in_not_in} your search range {health_search_range}"
  
  health_narrative_01 = f"{health_narrative_search_criters}. The table {{}} ranks general health in {ward_name}, {borough} and {city}. " + \
  "The ranking is highest to lowest percentage from top to bottom. Where there is a difference in general health the cell is shaded, a darker " + \
  "shade denotes a difference between borough and ward. Values in [] give the percentage value." 

  #
  ##
  ### ADD ITEM TO REPORT CONTEXT - HEALTH NARRATIVE 01
  ##
  #

  report_context["health_narrative_01"] = health_narrative_01
  
  ###
  ### BUILD HEALTH RANKING DATA TABLE
  ###
  
  ## Borough & Ward
  health_borough_ward_for_year = health_by_borough_ward_year_df.copy()
  health_borough_ward_for_year = health_borough_ward_for_year.drop(["YEAR", "LAD", "LAD_NAME", "WARD_CODE", "WARD_NAME"], axis=1)
  health_borough_ward_for_year = health_borough_ward_for_year.T.copy()
  health_borough_ward_for_year.columns = ["PCT"]
  health_borough_ward_for_year = health_borough_ward_for_year.sort_values(by=["PCT"], ascending=False)
  
  ## Borough
  health_borough_for_year = health_by_borough_year_df[health_by_borough_year_df["LAD_NAME"] == borough].copy()
  health_borough_for_year = health_borough_for_year.drop(["YEAR", "LAD", "LAD_NAME"], axis=1)
  health_borough_for_year = health_borough_for_year.T.copy()
  health_borough_for_year.columns = ["PCT"]
  health_borough_for_year = health_borough_for_year.sort_values(by=["PCT"], ascending=False)
  
  ## City
  health_city_for_year = health_average_year_df.copy()
  health_city_for_year
  health_city_for_year = health_city_for_year.drop(["YEAR"], axis=1)
  health_city_for_year = health_city_for_year.T.copy()
  health_city_for_year.columns = ["PCT"]
  health_city_for_year = health_city_for_year.sort_values(by=["PCT"], ascending=False)
  
  ## Borough Ward
  health_ward_pct_sorted = []
  for index, row in health_borough_ward_for_year.iterrows():
      health     = index
      health_pct = row.values[0]*100
      health_name_pct_fmt = "{} - [{:,.2f}%]".format(health, health_pct)
      health_ward_pct_sorted.append(health_name_pct_fmt)
  
  ## Borough
  health_borough_pct_sorted = []
  for index, row in health_borough_for_year.iterrows():
      health     = index
      health_pct = row.values[0]*100
      health_name_pct_fmt = "{} - [{:,.2f}%]".format(health, health_pct)
      health_borough_pct_sorted.append(health_name_pct_fmt)
  
  ## City
  health_city_pct_sorted = []
  for index, row in     health_city_for_year.iterrows():
      health     = index
      health_pct = row.values[0]*100
      health_name_pct_fmt = "{} - [{:,.2f}%]".format(health, health_pct)
      health_city_pct_sorted.append(health_name_pct_fmt)
  
  health_ward_borough_city_pct_ranked_merged = [health_ward_pct_sorted, health_borough_pct_sorted, health_city_pct_sorted]
  health_ranking_table = pd.DataFrame(data=health_ward_borough_city_pct_ranked_merged)
  
  ## Rotate 
  health_ranking_table = health_ranking_table.T
  health_ranking_table.columns = [f"{ward_name}",f"{borough}",f"{city}"]
  health_ranking_table.index   = [str(rank) for rank in range(1, len(health_ranking_table.index)+1)]

  ###
  ### BUILD HEALTH RANKING DISPLAY TABLE
  ###

  colour_change = []
  ## 0 == no change in that cell
  ## 1 == shade 1 change
  ## 2 == shade 2 change
  
  for index, row in health_ranking_table.iterrows():
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
  
  def health_ranking_cell_shading(row, cell_shading):
      ## Borough to City Check
      ward_val    = row.iloc[0].split(' - [')[0].strip()
      borough_val = row.iloc[1].split(' - [')[0].strip()
      city_val    = row.iloc[2].split(' - [')[0].strip()
      # log.debug(f"{ward_val}-{borough_val}-{city_val}")
  
      ward_val_cell_col = "" if ward_val     == city_val else "#EAFAF1" if ward_val == borough_val else "#D5F5E3"
      borough_val_col   = "" if borough_val  == city_val else "#EAFAF1"
      # log.debug(r[1])
      cell_shading.append([ward_val_cell_col, borough_val_col, ""])
  
  
  health_ranking_table_shading = []
  health_ranking_table.apply(lambda row: health_ranking_cell_shading(row, health_ranking_table_shading), axis=1)
  
  ####
  #### DELETE 
  ####
  # from IPython.display import HTML
  # styles = [
  #   dict(selector="tr", props=[("font-size", "110%"),
  #                              ("text-align", "right")])
  # ]
  # health_ward_borough_city_pct_ranked_merged_df_html = (health_ward_borough_city_pct_ranked_merged_df.style.set_table_styles(styles).apply(general_health_ranking_cell_shading, axis=1))
  # health_ranking_display_table_file_name = "{}/{}_health_ranking_display_table_{}_{}_{}.png".format(save_image_path, session_id, city, borough, ward_name) 
  # mlib.save_df(health_ward_borough_city_pct_ranked_merged_df_html, health_ranking_display_table_file_name, save_artefacts=True)
  # report_context["health_ranking_display_table"] = health_ranking_display_table_file_name
  ####
  #### DELETE 
  ####

  #
  ##
  ### ADD ITEM TO REPORT CONTEXT - HEALTH RANKING DISPLAY TABLE
  ##
  #
  ## ADD DATAFRAME
  report_context["health_ranking_table"] = health_ranking_table
  ## ADD DATAFRAME SHADING
  report_context["health_ranking_table_shading"] = health_ranking_table_shading
  
  
  ###
  ### BUILD HEALTH COMPARISON TABLE
  ###

  health_borough_ward_for_year_name_sorted = health_borough_ward_for_year.sort_index(ascending=True)
  health_borough_for_year_name_sorted      = health_borough_for_year.sort_index(ascending=True)
  health_city_for_year_name_sorted         = health_city_for_year.sort_index(ascending=True)
  
  health_borough_ward_for_year_name_sorted = health_borough_ward_for_year
  health_borough_for_year_name_sorted      = health_borough_for_year
  health_city_for_year_name_sorted         = health_city_for_year
  
  
  ## Borough Ward
  health_ward_name_sorted = []
  for index, row in health_borough_ward_for_year_name_sorted.iterrows():
      health_pct = row.values[0]*100
      health_pct_fmt = "{:,.2f}%".format(health_pct)
      health_ward_name_sorted.append(health_pct_fmt)
  
  ## Borough
  health_borough_name_sorted = []
  for index, row in health_borough_for_year_name_sorted.iterrows():
      health_pct = row.values[0]*100
      health_pct_fmt = "{:,.2f}%".format(health_pct)
      health_borough_name_sorted.append(health_pct_fmt)
  
  ## City
  health_city_name_sorted = []
  for index, row in health_city_for_year_name_sorted.iterrows():
      health_pct = row.values[0]*100
      health_pct_fmt = "{:,.2f}%".format(health_pct)
      health_city_name_sorted.append(health_pct_fmt)
  
  health_ward_borough_city_pct_name_merged = [health_ward_name_sorted, health_borough_name_sorted, health_city_name_sorted]
  health_comparison_table = pd.DataFrame(data=health_ward_borough_city_pct_name_merged)
  
  ## Rotate 
  health_comparison_table = health_comparison_table.T
  health_comparison_table.columns = [f"{ward_name}",f"{borough}",f"{city}"]
  health_comparison_table.index   = health_borough_ward_for_year_name_sorted.index
  health_comparison_table["Level"] = health_comparison_table.index

  ## Reorder the columns
  health_comparison_table = health_comparison_table[["Level", f"{ward_name}",f"{borough}",f"{city}"]]

  ###
  ### BUILD ETHNICITY COMPARISON DISPLAY TABLE
  ###

  def health_comparison_cell_shading(row, cell_shading):
      
      inc_shades =["", "#EAFAF1", "#D5F5E3", "#ABEBC6", "#82E0AA", "#58D68D"]
      dec_shades =["", "#F5EEF8", "#EBDEF0", "#D7BDE2", "#C39BD3", "#AF7AC5"]

      # log.debug(f"index:{row.name}")
      
      ## Borough to City Check
      name        = row.name
      ward_val    = float(row.iloc[1].split("%")[0].strip())
      borough_val = float(row.iloc[2].split("%")[0].strip())
      city_val    = float(row.iloc[3].split("%")[0].strip())
      
      if (name == "Very Good") or (name == "Good") or (name == "Fair"):
          # log.debug("Very Good, Good or Fair")
          ## It's more than the city so should be green
          if ward_val >= city_val:
              log.debug("Ward more so Green")
              diff = ward_val - city_val
              ward_val_cell_col = inc_shades[0] if (diff) < 1.0 else \
                                  inc_shades[1] if (diff) < 2.0 else \
                                  inc_shades[2] if (diff) < 3.0 else \
                                  inc_shades[3] if (diff) < 4.0 else \
                                  inc_shades[4] if (diff) < 5.0 else \
                                  inc_shades[5] 
              
          ## It's less than, so should be red
          else:
              # log.debug("Ward less so Red")
              #-ve then red shades
              diff = city_val - ward_val
              ward_val_cell_col = dec_shades[0] if (diff) < 1.0 else \
                                  dec_shades[0] if (diff) < 2.0 else \
                                  dec_shades[0] if (diff) < 3.0 else \
                                  dec_shades[0] if (diff) < 4.0 else \
                                  dec_shades[0] if (diff) < 5.0 else \
                                  dec_shades[0] 
             
          ## It's more than the city so should be green
          if borough_val >= city_val:
              log.debug("Borough more so Green")
              #+ve then green shades
              diff = borough_val - city_val
              borough_val_col   = inc_shades[0] if (diff) < 1.0 else \
                                  inc_shades[1] if (diff) < 2.0 else \
                                  inc_shades[2] if (diff) < 3.0 else \
                                  inc_shades[3] if (diff) < 4.0 else \
                                  inc_shades[4] if (diff) < 5.0 else \
                                  inc_shades[5] 
              
  
          ## It's less than, so should be red
          else:
              # log.debug("Borough less so Red")
              #-ve then red shades
              diff = city_val - borough_val
              borough_val_col   = dec_shades[0] if (diff) < 1.0 else \
                                  dec_shades[0] if (diff) < 2.0 else \
                                  dec_shades[0] if (diff) < 3.0 else \
                                  dec_shades[0] if (diff) < 4.0 else \
                                  dec_shades[0] if (diff) < 5.0 else \
                                  dec_shades[0] 
      
      ## It's Bad or Very Bad so opposite to the aboce
      else:
          # log.debug("Bad or Very Bad")
  
          ## It's more than the city so should be red
          if ward_val >= city_val:
              # log.debug("Ward more so Red")
              #-ve then red shades
              diff = ward_val - city_val
              ward_val_cell_col = dec_shades[0] if (diff) < 1.0 else \
                                  dec_shades[0] if (diff) < 2.0 else \
                                  dec_shades[0] if (diff) < 3.0 else \
                                  dec_shades[0] if (diff) < 4.0 else \
                                  dec_shades[0] if (diff) < 5.0 else \
                                  dec_shades[0] 
              
          ## It's less than, so should be green
          else:
              # log.debug("Ward less so Green")
              diff = city_val - ward_val
              ward_val_cell_col = inc_shades[0] if (diff) < 1.0 else \
                                  inc_shades[1] if (diff) < 2.0 else \
                                  inc_shades[2] if (diff) < 3.0 else \
                                  inc_shades[3] if (diff) < 4.0 else \
                                  inc_shades[4] if (diff) < 5.0 else \
                                  inc_shades[5] 
             
          ## It's more than the city so should be red
          if borough_val >= city_val:
              # log.debug("Borough more so Red")
              #-ve then red shades
              diff = borough_val - city_val
              borough_val_col   = dec_shades[0] if (diff) < 1.0 else \
                                  dec_shades[0] if (diff) < 2.0 else \
                                  dec_shades[0] if (diff) < 3.0 else \
                                  dec_shades[0] if (diff) < 4.0 else \
                                  dec_shades[0] if (diff) < 5.0 else \
                                  dec_shades[0] 
              
  
          ## It's less than, so should be green
          else:
              # log.debug("Borough less so Green")
              #+ve then green shades
              diff = city_val - borough_val
              borough_val_col   = inc_shades[0] if (diff) < 1.0 else \
                                  inc_shades[1] if (diff) < 2.0 else \
                                  inc_shades[2] if (diff) < 3.0 else \
                                  inc_shades[3] if (diff) < 4.0 else \
                                  inc_shades[4] if (diff) < 5.0 else \
                                  inc_shades[5] 
  
      cell_shading.append(["", ward_val_cell_col, borough_val_col, ""])
  
  health_comparison_table_shading = []
  health_comparison_table.apply(lambda row: health_comparison_cell_shading(row, health_comparison_table_shading), axis=1)

  ####
  #### DELETE 
  ####
  # from IPython.display import HTML
  # styles = [
  #   dict(selector="tr", props=[("font-size", "110%"),
  #                              ("text-align", "right")])
  # ]
  # health_comparison_table_html = (health_comparison_table.style.set_table_styles(styles).apply(health_comparison_cell_shading, axis=1))
  # health_comparison_display_table_file_name = "{}/{}_health_comparison_display_table_{}_{}_{}.png".format(save_image_path, session_id, city, borough, ward_name) 
  # mlib.save_df(health_comparison_table_html, health_comparison_display_table_file_name, save_artefacts=True)
  # report_context["health_comparison_display_table"] = health_comparison_display_table_file_name
  ####
  #### DELETE 
  ####

  #
  ##
  ### ADD ITEM TO REPORT CONTEXT - HEALTH COMPARISON DISPLAY TABLE
  ##
  #
  report_context["health_comparison_table"] = health_comparison_table
  report_context["health_comparison_table_shading"] = health_comparison_table_shading


  ###
  ### ETHNICITY NARRATIVE 02 
  ###

  health_narrative_02 = f"The table {{}} shows the percentage levels of general health (Very Good - Very Bad) in {ward_name}, {borough} and {city} in the year {health_year_to}" + \
  ". Value shading indicates a difference from the city level from 1 to 5 percent in 1 percent intervals." + \
  " The shade darkens with an increase in difference. Increases and decreases use different colours for clarity. Increases in Fair to Very Good are coloured the same as " + \
  "decreases in Bad and Very Bad."

  #
  ##
  ### ADD ITEM TO REPORT CONTEXT - HEALTH NARRATIVE 02
  ##
  #
  
  report_context["health_narrative_02"] = health_narrative_02

  db_conn.close()
  