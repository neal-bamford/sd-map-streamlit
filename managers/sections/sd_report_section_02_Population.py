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

  log.debug("<<<<<<<<<<<<<<<<<<")
  log.debug(search_term)
  log.debug("<<<<<<<<<<<<<<<<<<")
  ## Get the search terms
  city      = search_term["city"]
  borough   = search_term["borough"]
  ward_name = search_term["ward_name"]
  
  year_from = search_term["year_from"]
  year_to   = search_term["year_to"]
  
  
  ###
  ### FETCH THE DATA
  ###
  
  population_year_from = year_from
  population_year_to   = year_to
  
  # What do we have? We are only using the max for now
  population_min_max_year_df = dao_fac.population_min_max_year(db_conn)
  
  population_year_min = population_min_max_year_df["MIN_YEAR"].values[0]
  population_year_max = population_min_max_year_df["MAX_YEAR"].values[0]
  
  population_year_from_orig = population_year_from
  population_year_to_orig = population_year_to
  
  if population_year_from < int(population_year_min):
      population_year_from = int(population_year_min)
  elif population_year_from > int(population_year_max):
      population_year_from = int(population_year_max)
  
  if population_year_to > int(population_year_max):
      population_year_to = int(population_year_max)
  elif population_year_to < int(population_year_min):
      population_year_to = int(population_year_min)
  
  log.debug(f"population orig_year_to    :{population_year_to_orig}")
  log.debug(f"population search_year_to  :{population_year_to}")
  
  search_term = {"year_from":population_year_from,
                 "year_to":population_year_to,
                 "borough":borough,
                 "ward_name":ward_name}
  
  log.debug(search_term)
  
  #####
  #####
  #####
  
  population_by_borough_ward_year_df = dao_fac.population_year(db_conn, search_term)
  
  #####
  #####
  #####

  ## BOROUGH WARD LEVEL
  
  ## PERCENTAGES MALE - FEMALE - STUDENT 
  ### make a copy so we can go back
  pct_population_by_borough_ward_year_df = population_by_borough_ward_year_df[["YEAR", "BOROUGH", "WARD_NAME", "ALL", "MALE", "FEMALE", "STUDENT"]].copy()
  pct_population_by_borough_ward_year_df["MALE"] = pct_population_by_borough_ward_year_df["MALE"]/pct_population_by_borough_ward_year_df["ALL"]
  pct_population_by_borough_ward_year_df["FEMALE"] = pct_population_by_borough_ward_year_df["FEMALE"]/pct_population_by_borough_ward_year_df["ALL"]
  pct_population_by_borough_ward_year_df["STUDENT"] = pct_population_by_borough_ward_year_df["STUDENT"]/pct_population_by_borough_ward_year_df["ALL"]  
  
  #####
  #####
  #####

  gender_population_by_borough_ward_year_filtered = pct_population_by_borough_ward_year_df.loc[(population_by_borough_ward_year_df["BOROUGH"]==borough)
                                                                                      & (population_by_borough_ward_year_df["WARD_NAME"]==ward_name)]
  
  gender_population_by_borough_ward_year_filtered = gender_population_by_borough_ward_year_filtered.drop(["YEAR","STUDENT"], axis=1)
  # gender_population_by_borough_ward_year_filtered.T

  #####
  #####
  #####

  ### There seem to be some extreme values in the ward level pph
  ### These will be removed when binning and if the value falls into that
  ### category then they will be in the highest bin
  
  pph_population_by_borough_ward_year_df = population_by_borough_ward_year_df[["YEAR", "BOROUGH", "WARD_NAME", "DENSITY_PPH"]].copy()
  
  min_borough_ward_density_pph = pph_population_by_borough_ward_year_df["DENSITY_PPH"].quantile(.01)
  max_borough_ward_density_pph = pph_population_by_borough_ward_year_df["DENSITY_PPH"].quantile(.99)
  
  log.debug(f"min_borough_ward_density_pph:{min_borough_ward_density_pph}")
  log.debug(f"max_borough_ward_density_pph:{max_borough_ward_density_pph}")
  
  ## Creat3 the labels and bin
  pph_population_by_borough_ward_lbls = ["Scarcely Populated", "Slightly Populated", "Averagely Populated", "Highly Populated",  "Very Highly Populated"]
  pph_population_by_borough_ward_bins = np.arange(min_borough_ward_density_pph
                                                , max_borough_ward_density_pph-min_borough_ward_density_pph
                                                , (max_borough_ward_density_pph-min_borough_ward_density_pph)/len(pph_population_by_borough_ward_lbls)+1).tolist()
  pph_population_by_borough_ward_bins.append(np.inf)
  log.debug(pph_population_by_borough_ward_bins)
  
  # log.debug(f"{(max_borough_ward_density_pph - min_borough_ward_density_pph)/len(pph_population_by_borough_ward_lbls)}")
  # log.debug(f"pph_population_by_borough_ward_lbls:{pph_population_by_borough_ward_lbls}")
  # log.debug(f"pph_population_by_borough_ward_bins:{pph_population_by_borough_ward_bins}")
  
  pph_population_by_borough_ward_year_df['POPULATION_STATUS'] = pd.cut(pph_population_by_borough_ward_year_df["DENSITY_PPH"], bins=pph_population_by_borough_ward_bins, labels=pph_population_by_borough_ward_lbls)

  #####
  #####
  #####
  
  ## Filter to just our borough and ward
  pph_population_by_borough_ward_year_filtered = pph_population_by_borough_ward_year_df.loc[(pph_population_by_borough_ward_year_df["BOROUGH"]==borough)
                                                                                          & (pph_population_by_borough_ward_year_df["WARD_NAME"]==ward_name)]
  
  pph_population_by_borough_ward_year_filtered = pph_population_by_borough_ward_year_filtered.drop(["YEAR"], axis=1)
  pph_population_by_borough_ward_year_filtered
  
  # ## Make a display version
  borough_ward_population_table = pph_population_by_borough_ward_year_filtered.copy()
  borough_ward_population_table["DENSITY_PPH"] = round(borough_ward_population_table["DENSITY_PPH"],2)
  borough_ward_population_table.columns = [["Borough", "Ward", "Persons per Hectare", "Population Level"]]

  report_context["borough_ward_population_table"] = borough_ward_population_table
  
  #####
  #####
  #####

  ## BOROUGH LEVEL
  population_by_borough_year_df = population_by_borough_ward_year_df.groupby(["YEAR", "BOROUGH"], as_index=False)\
                                                                    .agg({"ALL":"sum", "MALE":"sum", "FEMALE":"sum", "STUDENT":"sum", "DENSITY_PPH":"mean" })
  
  ## PERCENTAGES MALE - FEMALE - STUDENT 
  ### make a copy so we can go back
  pct_population_by_borough_year_df = population_by_borough_year_df[["YEAR", "BOROUGH", "ALL", "MALE", "FEMALE", "STUDENT"]].copy()
  pct_population_by_borough_year_df["MALE"] = pct_population_by_borough_year_df["MALE"]/pct_population_by_borough_year_df["ALL"].astype(float)
  pct_population_by_borough_year_df["FEMALE"] = pct_population_by_borough_year_df["FEMALE"]/pct_population_by_borough_year_df["ALL"].astype(float)
  pct_population_by_borough_year_df["STUDENT"] = pct_population_by_borough_year_df["STUDENT"]/pct_population_by_borough_year_df["ALL"].astype(float)    
  
  #####
  #####
  #####

  gender_population_by_borough_year_filtered = pct_population_by_borough_year_df.loc[(pct_population_by_borough_year_df["BOROUGH"]==borough)]
  gender_population_by_borough_year_filtered = gender_population_by_borough_year_filtered.drop(["YEAR","STUDENT"], axis=1)
  # gender_population_by_borough_year_filtered.T

  #####
  #####
  #####

  pph_population_by_borough_year_df = population_by_borough_year_df[["YEAR", "BOROUGH", "DENSITY_PPH"]].copy()
  pph_population_by_borough_year_df["DENSITY_PPH"] = pph_population_by_borough_year_df["DENSITY_PPH"].astype(float)
  
  
  min_borough_density_pph = pph_population_by_borough_year_df["DENSITY_PPH"].quantile(.01)
  max_borough_density_pph = pph_population_by_borough_year_df["DENSITY_PPH"].quantile(.99)
  
  
  # min_borough_density_pph = pph_population_by_borough_year_df.min().values[2]
  # max_borough_density_pph = pph_population_by_borough_year_df.max().values[2]
  
  log.debug(f"min_borough_density_pph:{min_borough_density_pph}")
  log.debug(f"max_borough_density_pph:{max_borough_density_pph}")
  
  ## Create the labels and bin
  pph_population_by_borough_lbls = ["Scarcely Populated", "Slightly Populated", "Averagely Populated", "Highly Populated",  "Very Highly Populated"]
  pph_population_by_borough_bins = np.arange((max_borough_density_pph-min_borough_density_pph)/len(pph_population_by_borough_lbls)-1, max_borough_density_pph-min_borough_density_pph, (max_borough_density_pph-min_borough_density_pph)/len(pph_population_by_borough_lbls)-1).tolist()
  pph_population_by_borough_bins.append(np.inf)
  
  # log.debug(pph_population_by_borough_bins)
  # log.debug(f"{(max_borough_density_pph - min_borough_density_pph)/len(pph_population_by_borough_lbls)}")
  # log.debug(f"pph_population_by_borough_lbls:{pph_population_by_borough_lbls}")
  # log.debug(f"pph_population_by_borough_bins:{pph_population_by_borough_bins}")
  
  pph_population_by_borough_year_df['POPULATION_STATUS'] = pd.cut(pph_population_by_borough_year_df["DENSITY_PPH"], bins=pph_population_by_borough_bins, labels=pph_population_by_borough_lbls)  

  #####
  #####
  #####

  ## Sort on population density
  pph_population_by_borough_year_df_sorted = pph_population_by_borough_year_df.sort_values(by=["DENSITY_PPH"], ascending=False).copy()
  ## Drop the Year
  pph_population_by_borough_year_df_sorted = pph_population_by_borough_year_df_sorted.drop(["YEAR"], axis=1)
  
  ## Make a display version
  borough_population_table = pph_population_by_borough_year_df_sorted.copy()
  borough_population_table["DENSITY_PPH"] = round(borough_population_table["DENSITY_PPH"],2)
  borough_population_table.columns = [["Borough", "Persons per Hectare", "Population Level"]]
  
  ## Create the shading
  def borough_population_shading(row, cell_shading, match, hex_colour):
      
      cell_colour = "" 
      borough_name = row.iloc[0]
      
      if borough_name == match:
          cell_colour = hex_colour
      
      cell_shading.append([cell_colour, cell_colour , cell_colour])
  
  borough_population_table_shading = []
  borough_population_table.apply(lambda row:  borough_population_shading(row, borough_population_table_shading, borough, "#F7DC6F"), axis=1)
  
  report_context["borough_population_table"] = borough_population_table
  report_context["borough_population_table_shading"] = borough_population_table_shading
  
  # borough_population_table_shading
  
  #####
  #####
  #####
  
  ## CITY LEVEL
  population_by_city_year_df = population_by_borough_ward_year_df.groupby(["YEAR"], as_index=False)\
                                                                    .agg({"ALL":"sum", "MALE":"sum", "FEMALE":"sum", "STUDENT":"sum", "DENSITY_PPH":"mean" })
  
  ## PERCENTAGES MALE - FEMALE - STUDENT 
  ### make a copy so we can go back
  pct_population_by_city_year_df = population_by_city_year_df[["YEAR", "ALL", "MALE", "FEMALE", "STUDENT"]].copy()
  pct_population_by_city_year_df["MALE"] = population_by_city_year_df["MALE"]/population_by_city_year_df["ALL"].astype(float)
  pct_population_by_city_year_df["FEMALE"] = population_by_city_year_df["FEMALE"]/population_by_city_year_df["ALL"].astype(float)
  pct_population_by_city_year_df["STUDENT"] = population_by_city_year_df["STUDENT"]/population_by_city_year_df["ALL"].astype(float)
  
  # pct_population_by_city_year_df

  #####
  #####
  #####

  gender_population_by_city_year_filtered = pct_population_by_city_year_df.copy()
  gender_population_by_city_year_filtered = gender_population_by_city_year_filtered.drop(["YEAR","STUDENT"], axis=1)
  # gender_population_by_city_year_filtered.T

  #####
  #####
  #####

  def pct_fmt(val):
      val_fmt = "{:,.2f}%".format(round(val*100),2)
      return val_fmt
  
  def gender_fmt(val):
      
      val_fmt = val.capitalize()
      return val_fmt
  
  ## WARD
  gender_pct_ward_table = gender_population_by_borough_ward_year_filtered.T[3:]
  gender_pct_ward_table.columns = [ward_name]
  gender_pct_ward_table[ward_name] = gender_pct_ward_table[ward_name].apply(lambda val: pct_fmt(val))
  
  
  ## Borough
  gender_pct_borough_table = gender_population_by_borough_year_filtered.T[2:]
  gender_pct_borough_table.columns = [borough]
  gender_pct_borough_table[borough] = gender_pct_borough_table[borough].apply(lambda val: pct_fmt(val))
  
  ## City
  gender_pct_city_table = gender_population_by_city_year_filtered.T[1:]
  gender_pct_city_table.columns = [city]
  gender_pct_city_table[city] = gender_pct_city_table[city].apply(lambda val: pct_fmt(val))
  
  gender_pct_city_table = pd.concat([gender_pct_ward_table, gender_pct_borough_table, gender_pct_city_table], axis=1)
  gender_pct_city_table["Gender"] = gender_pct_city_table.index
  gender_pct_city_table = gender_pct_city_table.reset_index(drop=True)
  
  gender_pct_city_table = gender_pct_city_table[["Gender", ward_name, borough, city]].sort_values(["Gender"])
  gender_pct_city_table["Gender"] = gender_pct_city_table["Gender"].apply(lambda val:gender_fmt(val))
  gender_pct_city_table
  report_context["gender_pct_city_table"] = gender_pct_city_table

  #####
  #####
  #####

  def gender_pct_comparison_cell_shading(row, cell_shading):
  
    inc_shades =["", "#EAFAF1", "#D5F5E3", "#ABEBC6", "#82E0AA", "#58D68D"]
    dec_shades =["", "#F5EEF8", "#EBDEF0", "#D7BDE2", "#C39BD3", "#AF7AC5"]
  
    ## Borough to City Check
    ward_val    = float(row.iloc[1].split("%")[0].strip())
    borough_val = float(row.iloc[2].split("%")[0].strip())
    city_val    = float(row.iloc[3].split("%")[0].strip())
  
    diff_ward = city_val - ward_val
    if diff_ward < 0:
        ward_shades = inc_shades 
    else:
        ward_shades = dec_shades 
  
    diff_borough =   city_val - borough_val
    if diff_borough >= 0:
        borough_shades = inc_shades 
    else:
        borough_shades = dec_shades 
  
    ward_val_cell_col = ward_shades[0] if abs(diff_ward) <  5.0 else \
                        ward_shades[1] if abs(diff_ward) < 10.0 else \
                        ward_shades[2] if abs(diff_ward) < 15.0 else \
                        ward_shades[3] if abs(diff_ward) < 20.0 else \
                        ward_shades[4]
  
    borough_val_col   = borough_shades[0] if abs(diff_borough) <  5.0 else \
                        borough_shades[1] if abs(diff_borough) < 10.0 else \
                        borough_shades[2] if abs(diff_borough) < 15.0 else \
                        borough_shades[3] if abs(diff_borough) < 20.0 else \
                        borough_shades[4] 
  
    cell_shading.append(["", ward_val_cell_col, borough_val_col, ""])
      
  gender_pct_city_table_shading = []
  gender_pct_city_table.apply(lambda row: gender_pct_comparison_cell_shading(row, gender_pct_city_table_shading), axis=1)
  
  report_context["gender_pct_city_table_shading"] = gender_pct_city_table_shading

  #####
  #####
  #####
  
  ###
  ### POPULATON NARRATIVE 01 
  ###
  
  population_narrative_01 = ""
  population_in_not_in = "in" if ((population_year_to >= population_year_from_orig) &
                               (population_year_to <= population_year_to)) else "outside"
  
  population_search_range = f"of {population_year_from_orig} to {population_year_to_orig}" if population_year_from_orig != population_year_to_orig else f"{population_year_to_orig}"
  population_narrative_search_criters = f"Using the latest population data from {population_year_to} which is {population_in_not_in} your search range {population_search_range}"
  
  ward_borough_population_level = pph_population_by_borough_ward_year_filtered["POPULATION_STATUS"].values[0]
  population_narrative_01 = f"{population_narrative_search_criters}. The table {{}} shows that {ward_name} in {borough} is {ward_borough_population_level} compared to other {city} wards."
  
  ###
  ### POPULATON NARRATIVE 02 
  ###
  
  borough_population_level = pph_population_by_borough_year_df_sorted.loc[pph_population_by_borough_year_df_sorted["BOROUGH"] == borough]["POPULATION_STATUS"].values[0]
  borough_to_ward_population_level = "are the same" if ward_borough_population_level == borough_population_level else "are at different levels"
  population_narrative_02 = f"The table {{}} shows that {borough} is {borough_population_level} compared to other {city} boroughs and where it ranks in persons per hectars." + \
                            f" The population level at ward and borough {borough_to_ward_population_level}."
  
  
  
  ###
  ### POPULATON NARRATIVE 03 
  ###
  
  population_narrative_03 = f"Currently gender is only recorded at a binary level and is something which will be addressed in future datasets. The {{}} table shows the percentage" + \
                            f" of males and females at the ward, borough and city levels. Value shading indicates a difference from the city level from 5 to 25 percent in 5 percent intervals." +  \
                            f" The shade darkens with an increase in difference. Increases and decreases use different colours for clarity."
    

  report_context["population_narrative_01"] = population_narrative_01
  report_context["population_narrative_02"] = population_narrative_02
  report_context["population_narrative_03"] = population_narrative_03
  
  
  db_conn.close()
  
  
  
  
  