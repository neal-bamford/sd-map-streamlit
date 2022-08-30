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
  
  ethnicity_year_from = year_from
  ethnicity_year_to   = year_to
  
  # What do we have? We are only using the max for now
  ethnicity_min_max_year_df = dao_fac.ethnicity_min_max_year(db_conn)
  
  ethnicity_year_min = ethnicity_min_max_year_df["MIN_YEAR"].values[0]
  ethnicity_year_max = ethnicity_min_max_year_df["MAX_YEAR"].values[0]
  
  ethnicity_year_from_orig = ethnicity_year_from
  ethnicity_year_to_orig = ethnicity_year_to
  
  if ethnicity_year_from < int(ethnicity_year_min):
      ethnicity_year_from = int(ethnicity_year_min)
  elif ethnicity_year_from > int(ethnicity_year_max):
      ethnicity_year_from = int(ethnicity_year_max)
  
  if ethnicity_year_to > int(ethnicity_year_max):
      ethnicity_year_to = int(ethnicity_year_max)
  elif ethnicity_year_to < int(ethnicity_year_min):
      ethnicity_year_to = int(ethnicity_year_min)
  
  search_term = {"year_from":ethnicity_year_from,
                 "year_to":ethnicity_year_to,
                 "borough":borough,
                 "ward_name":ward_name}
  
  ## City
  ethnicity_average_year_df = dao_fac.ethnicity_ratio_average_years(db_conn, search_term)
  ## Borough
  ethnicity_by_borough_year_df = dao_fac.ethnicity_ratio_by_borough_years(db_conn, search_term)
  ## Ward
  ethnicity_by_borough_ward_year_df = dao_fac.ethnicity_ratio_by_borough_ward_years(db_conn, search_term)                          
  
  ###
  ### ETHNICITY NARRATIVE 01 
  ###
  
  ethnicity_narrative_01 = ""
  ethnicity_in_not_in = "in" if ((ethnicity_year_to >= ethnicity_year_from_orig) &
                                 (ethnicity_year_to <= ethnicity_year_to)) else "outside"
  
  ethnicity_search_range = f"of {ethnicity_year_from_orig} to {ethnicity_year_to_orig}" if ethnicity_year_from_orig != ethnicity_year_to_orig else f"{ethnicity_year_to_orig}"
  ethnicity_narrative_search_criters = f"Using the latest ethnicity data from {ethnicity_year_to} which is {ethnicity_in_not_in} your search range {ethnicity_search_range}"
  
  ethnicity_narrative_01 = f"{ethnicity_narrative_search_criters}. The table {{}} ranks ethnicity in {ward_name}, {borough} and {city}. " + \
  "The ranking is highest to lowest percentage from top to bottom. Where there is a difference in ethnicity the cell is shaded, a darker " + \
  "shade denotes a difference between borough and ward. Values in [] give the percentage value." 
  
  
  #
  ##
  ### ADD ITEM TO REPORT CONTEXT - ETHNICITY NARRATIVE 01
  ##
  #
  
  report_context["ethnicity_narrative_01"] = ethnicity_narrative_01
  
  ###
  ### BUILD ETHNICITY RANKING DATA TABLE
  ###
  
  ## Borough & Ward
  ethnicity_borough_ward_for_year = ethnicity_by_borough_ward_year_df.copy()
  ethnicity_borough_ward_for_year = ethnicity_borough_ward_for_year.drop(["YEAR", "LAD", "LAD_NAME", "WARD_CODE", "WARD_NAME"], axis=1)
  ethnicity_borough_ward_for_year = ethnicity_borough_ward_for_year.T.copy()
  ethnicity_borough_ward_for_year.columns = ["PCT"]
  ethnicity_borough_ward_for_year = ethnicity_borough_ward_for_year.sort_values(by=["PCT"], ascending=False)
  
  ## Borough
  ethnicity_borough_for_year = ethnicity_by_borough_year_df[ethnicity_by_borough_year_df["LAD_NAME"] == borough].copy()
  ethnicity_borough_for_year = ethnicity_borough_for_year.drop(["YEAR", "LAD", "LAD_NAME"], axis=1)
  ethnicity_borough_for_year = ethnicity_borough_for_year.T.copy()
  ethnicity_borough_for_year.columns = ["PCT"]
  ethnicity_borough_for_year = ethnicity_borough_for_year.sort_values(by=["PCT"], ascending=False)
  
  ## City
  ethnicity_city_for_year = ethnicity_average_year_df.copy()
  ethnicity_city_for_year
  ethnicity_city_for_year = ethnicity_city_for_year.drop(["YEAR"], axis=1)
  ethnicity_city_for_year = ethnicity_city_for_year.T.copy()
  ethnicity_city_for_year.columns = ["PCT"]
  ethnicity_city_for_year = ethnicity_city_for_year.sort_values(by=["PCT"], ascending=False)
  
  ## Borough Ward
  ethnicity_ward_pct_sorted = []
  for index, row in ethnicity_borough_ward_for_year.iterrows():
      ethnicity     = index
      ethncity_pct = row.values[0]*100
      ethnicity_name_pct_fmt = "{} - [{:,.2f}%]".format(ethnicity, ethncity_pct)
      ethnicity_ward_pct_sorted.append(ethnicity_name_pct_fmt)
  
  ## Borough
  ethnicity_borough_pct_sorted = []
  for index, row in ethnicity_borough_for_year.iterrows():
      ethnicity     = index
      ethncity_pct = row.values[0]*100
      ethnicity_name_pct_fmt = "{} - [{:,.2f}%]".format(ethnicity, ethncity_pct)
      ethnicity_borough_pct_sorted.append(ethnicity_name_pct_fmt)
  
  ## City
  ethnicity_city_pct_sorted = []
  for index, row in     ethnicity_city_for_year.iterrows():
      ethnicity     = index
      ethncity_pct = row.values[0]*100
      ethnicity_name_pct_fmt = "{} - [{:,.2f}%]".format(ethnicity, ethncity_pct)
      ethnicity_city_pct_sorted.append(ethnicity_name_pct_fmt)
  
  ethnicity_ward_borough_city_pct_ranked_merged = [ethnicity_ward_pct_sorted, ethnicity_borough_pct_sorted, ethnicity_city_pct_sorted]
  ethnicity_pct_ranking_table = pd.DataFrame(data=ethnicity_ward_borough_city_pct_ranked_merged)
  
  ## Rotate 
  ethnicity_pct_ranking_table = ethnicity_pct_ranking_table.T
  ethnicity_pct_ranking_table.columns = [f"{ward_name}",f"{borough}",f"{city}"]
  ethnicity_pct_ranking_table.index   = [str(rank) for rank in range(1, len(ethnicity_pct_ranking_table.index)+1)]
  
  ###
  ### BUILD ETHNICITY RANKING DISPLAY TABLE
  ###
  
  colour_change = []
  ## 0 == no change in that cell
  ## 1 == shade 1 change
  ## 2 == shade 2 change
  
  for index, row in ethnicity_pct_ranking_table.iterrows():
      colour_change_row =[]
      
      ## Borough to City Check
      ward_val    = row.iloc[0].split(' - [')[0].strip()
      borough_val = row.iloc[1].split(' - [')[0].strip()
      city_val    = row.iloc[2].split(' - [')[0].strip()
  
      ward_val_cell_col = 0 if ward_val     == city_val else 1 if ward_val == borough_val else 2
      borough_val_col   = 0 if borough_val  == city_val else 1
      cityl_col         = 0
      
      colour_change_row.append(ward_val_cell_col)
      colour_change_row.append(borough_val_col)
      colour_change_row.append(cityl_col)
      colour_change.append(colour_change_row)
  
  def ethnicity_pct_ranking_cell_shading(row, cell_shading):
    
      ## Borough to City Check
      ward_val    = row.iloc[0].split(' - [')[0].strip()
      borough_val = row.iloc[1].split(' - [')[0].strip()
      city_val    = row.iloc[2].split(' - [')[0].strip()
  
      ward_val_cell_col = "" if ward_val     == city_val else "#EAFAF1" if ward_val == borough_val else "#D5F5E3"
      borough_val_col   = "" if borough_val  == city_val else "#EAFAF1"

      ## No index column, just ward and borough
      cell_shading.append([ward_val_cell_col, borough_val_col, ""])
  
  ethnicity_pct_ranking_table_shading = []
  ethnicity_pct_ranking_table.apply(lambda row: ethnicity_pct_ranking_cell_shading(row, ethnicity_pct_ranking_table_shading), axis=1)
  
  #
  ##
  ### ADD ITEM TO REPORT CONTEXT
  ##
  #

  ## ADD DATAFRAME
  report_context["ethnicity_pct_ranking_table"] = ethnicity_pct_ranking_table
  ## ADD DATAFRAME SHADING
  report_context["ethnicity_pct_ranking_table_shading"] = ethnicity_pct_ranking_table_shading

  
  ####
  #### DELETE 
  ####
  # from IPython.display import HTML
  # styles = [
  #   dict(selector="tr", props=[("font-size", "110%"),
  #                              ("text-align", "right")])
  # ]
  #
  # ethnicity_ward_borough_city_pct_ranked_merged_df_html = (ethnicity_pct_ranking_table.style.set_table_styles(styles).apply(ethnicity_ranking_cell_shading, axis=1))
  ####
  #### DELETE 
  ####
  
  #
  ##
  ### ADD ITEM TO REPORT CONTEXT - ETHNICITY RANKING DISPLAY TABLE
  ##
  #
    
  ####
  #### DELETE 
  ####
  # ethnicity_ranking_display_table_file_name = "{}/{}_ethnicity_ranking_display_table_{}_{}_{}.png".format(save_image_path, session_id, city, borough, ward_name) 
  # mlib.save_df(ethnicity_ward_borough_city_pct_ranked_merged_df_html, ethnicity_ranking_display_table_file_name, save_artefacts=True)
  # report_context["ethnicity_ranking_display_table"] = ethnicity_ranking_display_table_file_name
  ####
  #### DELETE 
  ####
  
  ###
  ### BUILD ETHNICITY COMPARISSON TABLE
  ###

  ethnicity_borough_ward_for_year_name_sorted = ethnicity_borough_ward_for_year.sort_index(ascending=True)
  ethnicity_borough_for_year_name_sorted      = ethnicity_borough_for_year.sort_index(ascending=True)
  ethnciity_city_for_year_name_sorted         = ethnicity_city_for_year.sort_index(ascending=True)
  
  
  ## Borough Ward
  ethnicity_ward_name_sorted = []
  for index, row in ethnicity_borough_ward_for_year_name_sorted.iterrows():
      ethnciity_pct = row.values[0]*100
      ethnicity_pct_fmt = "{:,.2f}%".format(ethnciity_pct)
      ethnicity_ward_name_sorted.append(ethnicity_pct_fmt)
  
  ## Borough
  ethnicity_borough_name_sorted = []
  for index, row in ethnicity_borough_for_year_name_sorted.iterrows():
      ethnciity_pct = row.values[0]*100
      ethnicity_pct_fmt = "{:,.2f}%".format(ethnciity_pct)
      ethnicity_borough_name_sorted.append(ethnicity_pct_fmt)
  
  ## City
  ethnicity_city_name_sorted = []
  for index, row in ethnciity_city_for_year_name_sorted.iterrows():
      ethnicity_pct = row.values[0]*100
      ethnicity_pct_fmt = "{:,.2f}%".format(ethnicity_pct)
      ethnicity_city_name_sorted.append(ethnicity_pct_fmt)
  
  ethnicity_ward_borough_city_pct_name_merged = [ethnicity_ward_name_sorted, ethnicity_borough_name_sorted, ethnicity_city_name_sorted]
  ethnicity_pct_comparison_table = pd.DataFrame(data=ethnicity_ward_borough_city_pct_name_merged)
  
  ## Rotate 
  ethnicity_pct_comparison_table = ethnicity_pct_comparison_table.T
  ethnicity_pct_comparison_table.columns = [f"{ward_name}",f"{borough}",f"{city}"]
  ethnicity_pct_comparison_table.index   = ethnicity_borough_ward_for_year_name_sorted.index
  ethnicity_pct_comparison_table["Ethnicity"] = ethnicity_pct_comparison_table.index
  
  ## Reorder the columns
  ethnicity_pct_comparison_table = ethnicity_pct_comparison_table[["Ethnicity", f"{ward_name}",f"{borough}",f"{city}"]]
  # education_comparison_table
  
  ##
  ##
  
  def ethnicity_pct_comparison_cell_shading(row, cell_shading):
    
      inc_dec_shades =["", "#EAFAF1", "#D5F5E3", "#ABEBC6", "#82E0AA", "#58D68D"]
    
      ## Borough to City Check
      ward_val    = float(row.iloc[1].split("%")[0].strip())
      borough_val = float(row.iloc[2].split("%")[0].strip())
      city_val    = float(row.iloc[3].split("%")[0].strip())
      
      ward_diff    = city_val - ward_val
      borough_diff = city_val - borough_val
      
      ward_val_cell_col = inc_dec_shades[0] if abs(ward_diff) <  5.0 else \
                          inc_dec_shades[1] if abs(ward_diff) < 10.0 else \
                          inc_dec_shades[2] if abs(ward_diff) < 15.0 else \
                          inc_dec_shades[3] if abs(ward_diff) < 20.0 else \
                          inc_dec_shades[4]
      
      borough_val_col   = inc_dec_shades[0] if abs(borough_diff) <  5.0 else \
                          inc_dec_shades[1] if abs(borough_diff) < 10.0 else \
                          inc_dec_shades[2] if abs(borough_diff) < 15.0 else \
                          inc_dec_shades[3] if abs(borough_diff) < 20.0 else \
                          inc_dec_shades[4] 
                          
      ethnicity = row.iloc[0]
      # log.debug(f"ethnicity:{ethnicity} - ward_diff:{ward_diff}[{ward_val_cell_col}] - borough_diff:{borough_diff}[{borough_val_col}]")
      
      cell_shading.append(["", ward_val_cell_col, borough_val_col, inc_dec_shades[0]])
  
  ethnicity_pct_comparison_table_shading = []
  ethnicity_pct_comparison_table.apply(lambda row: ethnicity_pct_comparison_cell_shading(row, ethnicity_pct_comparison_table_shading), axis=1)
  #
  ##
  ### ADD ITEM TO REPORT CONTEXT
  ##
  #
  report_context["ethnicity_pct_comparison_table"] = ethnicity_pct_comparison_table
  report_context["ethnicity_pct_comparison_table_shading"] = ethnicity_pct_comparison_table_shading
  
  ##
  ##
  
  #### DELETE 
  ####
  # from IPython.display import HTML
  # styles = [
  #   dict(selector="tr", props=[("font-size", "110%"),
  #                              ("text-align", "right")])
  # ]
  # ethnicity_ward_borough_city_pct_name_merged_df_html = (ethnicity_ward_borough_city_pct_name_merged_df.style.set_table_styles(styles).apply(ethnicity_comparison_cell_shading, axis=1))
  #
  # ethnicity_comparison_display_table_file_name = "{}/{}_ethnicity_comparison_display_table_{}_{}_{}.png".format(save_image_path, session_id, city, borough, ward_name) 
  # mlib.save_df(ethnicity_ward_borough_city_pct_name_merged_df_html, ethnicity_comparison_display_table_file_name, save_artefacts=True)
  # report_context["ethnicity_comparison_display_table"] = ethnicity_comparison_display_table_file_name
  ####
  #### DELETE 
  ####

  #
  ##
  ### ADD ITEM TO REPORT CONTEXT - ETHNICITY COMPARISON DISPLAY TABLE
  ##
  #

  
  ###
  ### ETHNICITY NARRATIVE 02 
  ###
  
  ethnicity_narrative_02 = f"The table {{}} shows the percentage levels of ethnicity in {ward_name}, {borough} and {city} in {ethnicity_year_to}." + \
" The order of ethnicity is alphabetical. Value shading indicates a difference from the city level from 5 to 20 percent in 5 percent intervals." + \
" The shade darkens with an increase in difference. Indication of the direction of the difference is intentionally not made."

  #
  ##
  ### ADD ITEM TO REPORT CONTEXT - ETHNICITY NARRATIVE 02
  ##
  #
  
  report_context["ethnicity_narrative_02"] = ethnicity_narrative_02
  
  
  db_conn.close()
  
  
  
  
  