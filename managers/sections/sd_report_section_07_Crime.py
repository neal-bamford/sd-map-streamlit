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
  borough_crime_min_max_year_df = dao_fac.crime_min_max_year(db_conn)
  
  crime_year_from = year_from
  crime_year_to   = year_to
  
  crime_year_min = borough_crime_min_max_year_df["MIN_YEAR"].values[0]
  crime_year_max = borough_crime_min_max_year_df["MAX_YEAR"].values[0]
  
  log.debug(crime_year_min)
  log.debug(crime_year_max)
  
  
  crime_year_from_orig = crime_year_from
  crime_year_to_orig = crime_year_to
  
  if crime_year_from < int(crime_year_min):
      crime_year_from = int(crime_year_min)
  elif crime_year_from > int(crime_year_max):
      crime_year_from = int(crime_year_max)
  
  if crime_year_to > int(crime_year_max):
      crime_year_to = int(crime_year_max)
  elif crime_year_to < int(crime_year_min):
      crime_year_to = int(crime_year_min)
  
  log.debug(f"earnings orig_year_to    :{crime_year_to_orig}")
  log.debug(f"earnings search_year_to  :{crime_year_to}")
  
  search_term = {"year_from":crime_year_from,
                 "year_to"  :crime_year_to,
                 "borough"  :borough,
                 "ward_name":ward_name}
  
  ### Now we have a date range that's validated, apply it to the crim data
  log.debug("QRY Started")
  borough_crime_per_capita_by_year_df = dao_fac.crime_ranked_by_borough_years(db_conn, search_term)
  log.debug("QRY Ended")
  # log.debug(borough_crime_per_capita_by_year_df)
  
  ## Years are in descending order
  unique_years = borough_crime_per_capita_by_year_df["YEAR"].unique().tolist()
  
  ## Move this to the populatkon section
  ## City Population
  city_yearly_population_df = dao_fac.city_yearly_population(db_conn, search_term)
  
  # ## Borough Population
  borough_yearly_population_df = dao_fac.borough_yearly_population(db_conn, search_term)
  
  city_yearly_population_ts_df = city_yearly_population_df.copy()
  borough_yearly_population_ts_df = borough_yearly_population_df.copy()
  
  city_yearly_population_ts_df = city_yearly_population_ts_df.set_index("YEAR")
  city_yearly_population_ts_df["Year"] = city_yearly_population_ts_df.index
  
  borough_yearly_population_ts_df = borough_yearly_population_ts_df.set_index("YEAR")
  borough_yearly_population_ts_df["Year"] = borough_yearly_population_ts_df.index

  ##
  ##
  
  index = []
  data  = []
  columns = ["CITY_MAX_IN_YEAR", "CITY_MEAN_IN_YEAR", "CITY_MIN_IN_YEAR", "BOROUGH_MEAN_IN_YEAR"]
  
  unique_years_plot = sorted(unique_years)
  
  for year in unique_years_plot:
      data_row = []
      city_max_in_year     = borough_crime_per_capita_by_year_df[borough_crime_per_capita_by_year_df["YEAR"] == year]["CRIMES_PER_PERSON"].max()
      city_mean_in_year    = borough_crime_per_capita_by_year_df[borough_crime_per_capita_by_year_df["YEAR"] == year]["CRIMES_PER_PERSON"].mean()
      city_min_in_year     = borough_crime_per_capita_by_year_df[borough_crime_per_capita_by_year_df["YEAR"] == year]["CRIMES_PER_PERSON"].min()
      borough_mean_in_year = borough_crime_per_capita_by_year_df[(borough_crime_per_capita_by_year_df["YEAR"] == year) &
                                                               (borough_crime_per_capita_by_year_df["BOROUGH"] == borough)]["CRIMES_PER_PERSON"].values[0]
          
      index.append(year)
      data_row.append(city_max_in_year)
      data_row.append(city_mean_in_year)
      data_row.append(city_min_in_year)
      data_row.append(borough_mean_in_year)
      data.append(data_row)
      # log.debug(f"[{borough}]-{year} - borough mean:{borough_mean_in_year_fmt} - city max:{max_in_year_fmt} - city mean:{mean_in_year_fmt} - city min:{min_in_year_fmt} - country mean:{country_mean_in_year_fmt}")
      
  crime_ts_df = pd.DataFrame(data=data, index=index, columns=columns)    
  crime_ts_df["Year"] = crime_ts_df.index

  ##
  ##
  import seaborn as sns
  import matplotlib.pyplot as plt
  import matplotlib.ticker as ticker
  
  
  x_fig_size = 15
  y_fig_size = 8
  
  ## Set the size
  sns.set(rc={"figure.figsize":(x_fig_size, y_fig_size)})
  
  ## Set the theme
  sns.set_style("whitegrid")
  
  marker = "" if year_from != year_to else "o"
  
  fig, ax = plt.subplots()
  sns.lineplot(data=crime_ts_df, x="Year", y="CITY_MAX_IN_YEAR",     ax=ax, label=f"{city} Max.",    color='blue', marker=marker)
  sns.lineplot(data=crime_ts_df, x="Year", y="CITY_MEAN_IN_YEAR",    ax=ax, label=f"{city} Avg.",    color='green', marker=marker)
  sns.lineplot(data=crime_ts_df, x="Year", y="CITY_MIN_IN_YEAR",     ax=ax, label=f"{city} Min.",    color='red', marker=marker)
  sns.lineplot(data=crime_ts_df, x="Year", y="BOROUGH_MEAN_IN_YEAR", ax=ax, label=f"{borough} Avg.", color='orange', marker=marker)
  
  plot_title = "Crimes per Person between {} and {}".format(year_from, year_to) if year_from != year_to else \
               "Crimes per Person for {}".format(year_to)
  
  ax.set_title(plot_title, fontsize=20)
  ax.set_ylabel("Crimes per Person", fontsize=20)
  ax.set_xlabel("Year", fontsize=20)
  
  ax.legend(title="legend")
  ax.legend(loc="upper right")
  plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
  
  for line in ax.get_lines():
      line.set_linewidth(5)
      line.set_ms(10)
  
  ax.grid(False)
  plt.yticks(fontsize=20)
  plt.xticks(fontsize=20)
  
  # ax2 = plt.twinx()
  # ax2.grid(False)
  # # sns.lineplot(data=city_yearly_population_ts_df, x="Year", y="POPULATION_FOR_YEAR_CITY" , color="b", ax=ax2)
  # sns.lineplot(data=borough_yearly_population_ts_df, x="Year", y="POPULATION_FOR_YEAR_CITY" , color="b", ax=ax2)
  
  plt.tight_layout()
  
  crime_time_series_plot = plt.gcf()
  
  crime_time_series_plot_file = "{}/{}_crime_time_series_plot_{}_{}_{}.png".format(save_image_path, session_id, city, year_from, year_to)
  mlib.save_plot_filename(plot=crime_time_series_plot, filename=crime_time_series_plot_file, save_artefacts=True)
  report_context["crime_time_series_plot"] = crime_time_series_plot_file


  ##
  ##

  crime_changed_search_date_dates     = f"The new date is {crime_year_to}" if crime_year_from == crime_year_to else \
                                           f"The new dates are {crime_year_from} to {crime_year_to}"
  
  crime_changed_search_s              = f" was" if crime_year_from == crime_year_to else \
                                           f"s were"
  
  crime_narrative_01 = f"Your original search date{crime_changed_search_s} changed to match the date range of the earnings data. {crime_changed_search_date_dates}" \
                                           if ((crime_year_from != crime_year_from_orig) or \
                                               (crime_year_to   != crime_year_to_orig)) else ""

  report_context["crime_narrative_01"] = crime_narrative_01  
  
  ##
  ##
  
  ## The maximum year from the data set
  crime_latest_year = borough_crime_per_capita_by_year_df["YEAR"].max()
  crime_latest_year = year_to
  
  ## The Average earnings across all the boroughs for that year
  borough_crime_ranking_filtered_max_year_df =  borough_crime_per_capita_by_year_df[borough_crime_per_capita_by_year_df["YEAR"].astype(int) == crime_latest_year]
  
  
  latest_city_max_mean_crime_pp     = borough_crime_ranking_filtered_max_year_df["CRIMES_PER_PERSON"].max()
  latest_city_mean_mean_crime_pp    = borough_crime_ranking_filtered_max_year_df["CRIMES_PER_PERSON"].mean()
  latest_borough_mean_crime_pp      = borough_crime_ranking_filtered_max_year_df[borough_crime_ranking_filtered_max_year_df["BOROUGH"] == borough]["CRIMES_PER_PERSON"].values[0]
  latest_city_min_mean_crime_pp     = borough_crime_ranking_filtered_max_year_df["CRIMES_PER_PERSON"].min()
  
  def prepend(a, b):
    ret_val = ""
    if b != 0:
        if a > b:
          ret_val = "significantly " if a/b >= 2.0 else ""
        elif a < b:
          ret_val = "significantly " if b/a >= 2.0 else ""
    return ret_val
  
  def above_below_equal(a, b):
      ret_val = ""
      if b != 0:
          if a > b:
              if a/b <= 1.1:
                  ret_val = "comparable to"
              else:
                  ret_val = "above"
          elif a < b:
              if b/a <= 1.1:
                  ret_val = "comparable to"
              else:
                  ret_val = "below"
          else:
              ret_val = "equal to"
      else:
          ret_val = "above"
  
      return ret_val
  
  ## Format the latest for the text
  ### City
  latest_city_max_mean_crime_pp_fmt     = "{:,.4f}".format(float(latest_city_max_mean_crime_pp))
  latest_city_mean_mean_crime_pp_fmt    = "{:,.4f}".format(float(latest_city_mean_mean_crime_pp))
  latest_borough_mean_crime_pp_fmt      = "{:,.4f}".format(float(latest_borough_mean_crime_pp))
  latest_city_min_mean_crime_pp_fmt     = "{:,.4f}".format(float(latest_city_min_mean_crime_pp))
  
  ## Preamble
  part_01 = f"The {crime_latest_year} crimes per person in {borough} is {latest_borough_mean_crime_pp_fmt}"
  
  ## CITY BOROUGH MEAN COMPARE TO CITY MEAN MEAN [X]
  mean_explanation = f"{prepend(latest_borough_mean_crime_pp, latest_city_mean_mean_crime_pp)}{above_below_equal(latest_borough_mean_crime_pp, latest_city_mean_mean_crime_pp)}"
  part_02 = f". This is {mean_explanation} the average for {city} in the same period of {latest_city_mean_mean_crime_pp_fmt}"
  
  
  # CITY BOROUGH MEAN COMPARE TO CITY MAX MEAN [X]
  max_explanation = f"{prepend(latest_borough_mean_crime_pp, latest_city_max_mean_crime_pp)}{above_below_equal(latest_borough_mean_crime_pp, latest_city_max_mean_crime_pp)}"
  part_03 = f" and is {max_explanation} the maximum of {latest_city_max_mean_crime_pp_fmt}"
  
  
  ## CITY BOROUGH MEAN COMPARE TO CITY MIN MEAN [X]
  min_explanation = f"{prepend(latest_borough_mean_crime_pp, latest_city_min_mean_crime_pp)}{above_below_equal(latest_borough_mean_crime_pp, latest_city_min_mean_crime_pp)}"
  part_04 = f". It is {min_explanation} the minimum of {latest_city_min_mean_crime_pp_fmt}"
  
  from scipy import stats
  y = [crime_ts_df["BOROUGH_MEAN_IN_YEAR"].tolist()]
  x = crime_ts_df.index.astype(int).tolist()
  
  part_05 = ""
  
  if len(x) >= 3:
  
      # log.debug(y)
      # log.debug(x)
  
      slope, intercept, r, p, std_err = stats.linregress(x, y)
  
      if slope == 0:
          rate = "has remained level"
      elif slope > 0:    
          if slope >= 0.1:
              rate = "has slightly increased"
          elif slope >=  0.5:
              rate = "has moderatly increased"
          else:
              rate = "has greatly increased"
      else:
          if slope <= - 0.1:
              rate = "has slightly decreased"
          elif slope <= - 0.5:
              rate = "has moderatly decreased"
          else:
              rate = "has greatly decreased"
  
      part_05 = f". Over the period {year_from} to {year_to} crimes per person in {borough} {rate}."
  
  ## Borough population trend 
  part_06 = ""
  part_07 = ""
  
  y = [borough_yearly_population_df["POPULATION_FOR_YEAR_CITY"].tolist()]
  x = borough_yearly_population_df.index.astype(int).tolist()
  
  if len(x) >= 3:
  
      ## Borough population trend.
      borough_population_start = y[0][0]
      borough_population_start_fmt = "{:,.0f}".format(borough_population_start)
      
      borough_population_end = y[0][-1]
      borough_population_end_fmt = "{:,.0f}".format(borough_population_end)
      
      slope, intercept, r, p, std_err = stats.linregress(x, y)
  
      inc_dec_narrative = ""
      if slope == 0:
          rate = "has remained level"
      elif slope > 0:    
          inc_dec = borough_population_end - borough_population_start
          inc_dec_fmt = "{:,.0f}".format(inc_dec)
          inc_dec_narrative = f" which is an increase of {inc_dec_fmt}"
          
          if slope >= 0.1:
              rate = "has slightly increased"
          elif slope >=  0.5:
              rate = "has moderatly increased"
          else:
              rate = "has greatly increased"
      else:
          inc_dec = borough_population_start - borough_population_end 
          inc_dec_fmt = "{:,.0f}".format(inc_dec)
          inc_dec_narrative = f" which is a decrease of {inc_dec_fmt}"
          
          if slope <= - 0.1:
              rate = "has slightly decreased"
          elif slope <= - 0.5:
              rate = "has moderatly decreased"
          else:
              rate = "has greatly decreased"
  
      part_06 = f" Over the same period the population of {borough} {rate} from {borough_population_start_fmt} to {borough_population_end_fmt} {inc_dec_narrative}."
  
      ## City population trend
      y = [city_yearly_population_ts_df["POPULATION_FOR_YEAR_CITY"].tolist()]
      x = city_yearly_population_ts_df.index.astype(int).tolist()
  
      city_population_start = y[0][0]
      city_population_start_fmt = "{:,.0f}".format(city_population_start)
      
      city_population_end = y[0][-1]
      city_population_end_fmt = "{:,.0f}".format(city_population_end)
      
      slope, intercept, r, p, std_err = stats.linregress(x, y)
  
      inc_dec_narrative = ""
      if slope == 0:
          rate = "has remained level"
      elif slope > 0:    
          inc_dec = city_population_end - city_population_start
          inc_dec_fmt = "{:,.0f}".format(inc_dec)
          inc_dec_narrative = f" which is an increase of {inc_dec_fmt}"
          
          if slope >= 0.1:
              rate = "has slightly increased"
          elif slope >=  0.5:
              rate = "has moderatly increased"
          else:
              rate = "has greatly increased"
      else:
          inc_dec = city_population_start - city_population_end 
          inc_dec_fmt = "{:,.0f}".format(inc_dec)
          inc_dec_narrative = f" which is a decrease of {inc_dec_fmt}"
          
          if slope <= - 0.1:
              rate = "has slightly decreased"
          elif slope <= - 0.5:
              rate = "has moderatly decreased"
          else:
              rate = "has greatly decreased"
  
      part_07 = f" {city}'s population {rate} from {city_population_start_fmt} and ending at {city_population_end_fmt}{inc_dec_narrative}."
      
      
  ### Put them all together  [ ]
  crime_narrative_02 = f"{part_01}{part_02}{part_03}{part_04}{part_05}{part_06}{part_07}"

  report_context["crime_narrative_02"] = crime_narrative_02

  ##
  ##
  
  years_sorted = borough_crime_per_capita_by_year_df["YEAR"].sort_values().drop_duplicates()
  first_year = years_sorted.iloc[0]
  borough_sort_order = borough_crime_per_capita_by_year_df.loc[borough_crime_per_capita_by_year_df["YEAR"]==first_year]["BOROUGH"]
  top_borough = borough_sort_order.iloc[0]
  mid_borough = borough_sort_order.iloc[16]
  bottom_borough = borough_sort_order.iloc[-1]
  
  ## Loop through the boroughs in the sort order of first year
  all_borough_ranking_by_year = []
  
  ## BOROUGH LOOP
  for _borough in borough_sort_order:
  
      borough_ranking_by_year_list = []
  
      ## Add the Borough
      borough_ranking_by_year_list.append(_borough)
  
      ## YEAR LOOP
      for year in years_sorted:
  
          borough_ranking_for_year = borough_crime_per_capita_by_year_df.loc[(borough_crime_per_capita_by_year_df["BOROUGH"]==_borough) &
                                        (borough_crime_per_capita_by_year_df["YEAR"]==year)]["RANK"].values[0]
  
          borough_ranking_by_year_list.append(borough_ranking_for_year)
  
      all_borough_ranking_by_year.append(borough_ranking_by_year_list)
  
  columns = ["Borough"] + list(years_sorted)
  
  all_borough_ranking_by_year_df = pd.DataFrame(all_borough_ranking_by_year, columns=columns).set_index("Borough")
  
  tmb_borough_ranking_by_year_df = all_borough_ranking_by_year_df.copy()
  
  ##
  ##
  
  palette = sns.color_palette(cc.glasbey, n_colors=len(borough_sort_order))
  my_cmap = ListedColormap(sns.color_palette(palette).as_hex())
  ax = all_borough_ranking_by_year_df.T.plot(figsize=(20, 10), marker="o",  ms=5, cmap=my_cmap)
  
  ax.grid(False)
  title = f"Borough Rankings of Crimes per Person {crime_year_from} and {crime_year_to}" if crime_year_from != crime_year_to else \
          f"Borough Rankings of Crimes per Person in {crime_year_to}"
  
  ax.set_title(title, fontsize=20)
  
  plt.xticks(fontsize=10)
  
  ## Generate labels from the Borough names for the Y Axis
  plt.yticks(range(1, len(borough_sort_order)+1), [borough_sort_order.iloc[i] for i in range(len(borough_sort_order))])
  plt.yticks(fontsize=15)
  
  plt.gca().invert_yaxis()
  plt.gca().get_legend().remove()
  
  for line in ax.get_lines():
      # if (line.get_label() == borough) or (line.get_label() == top_borough) or (line.get_label() == mid_borough) or (line.get_label() == bottom_borough):
      if (line.get_label() == borough) or (line.get_label() == top_borough) or (line.get_label() == bottom_borough):
          line.set_linewidth(5)
          line.set_ms(10)
      else:
          line.set_linewidth(2)
          line.set_ms(4)
          line.set_alpha(0.3)
  
  crime_bump_chart_plot = plt.gcf()         
      
  crime_bump_chart_plot_file = "{}/{}_crime_bump_chart_plot_{}_{}_{}.png".format(save_image_path, session_id, city, year_from, year_to)
  mlib.save_plot_filename(plot=crime_bump_chart_plot, filename=crime_bump_chart_plot_file, save_artefacts=True)
  report_context["crime_bump_chart_plot"] = crime_bump_chart_plot_file
  
  
  
  crime_bump_chart_date_range = f"over the period {crime_year_from} to {crime_year_to}" if crime_year_from != crime_year_to else f"for {crime_year_to}"
  crime_bump_chart_narrative = f"How {borough} ranks with the other {city} boroughs {crime_bump_chart_date_range} can be seen {{}}. Ranking is top to bottom, with the top representing the highest crime per person rate."

  report_context["crime_bump_chart_narrative"] = crime_bump_chart_narrative
  
  ##
  ##
  
  ## Change the order of unique years back to Descednding
  unique_years_bump = sorted(unique_years, reverse=True)
  
  crime_benchmark_data = []
  
  ## Loop through the years to create our data frame for benchmarking
  
  ## Using the Bump Chart Data
  for year in unique_years_bump:
      ## Vertical Slice  
      borough_year_data = tmb_borough_ranking_by_year_df[year] 
  
      ## Loop through each borough
      idx = 0;
  
      ## Add uear to the dataframe row
      crime_benchmark_data_row = []
      crime_benchmark_data_row.append(str(year))
  
      for borough_year in borough_year_data.index:
          ranking = borough_year_data[idx]     
          
          borough_max_min_crime_year = crime_ts_df[crime_ts_df["Year"].astype(int) == int(year)][["CITY_MAX_IN_YEAR", "CITY_MIN_IN_YEAR"]]
  
          max_borough_crime_for_year = borough_max_min_crime_year["CITY_MAX_IN_YEAR"]
          max_borough_crime_for_year_fmt = "{:,.4f}".format(float(max_borough_crime_for_year))
  
          min_borough_crime_for_year = borough_max_min_crime_year["CITY_MIN_IN_YEAR"]
          min_borough_crime_for_year_fmt = "{:,.4f}".format(float(min_borough_crime_for_year))
  
          # log.debug(ranking)
          if ranking == 1:
            max_str = f"{borough_year} - {max_borough_crime_for_year_fmt}"
  
          if ranking == 33:
            min_str = f"{borough_year} - {min_borough_crime_for_year_fmt}"
  
          idx += 1
  
      ## Min
      crime_benchmark_data_row.append(min_str)
      
      ## Our borough's 
      search_borough_crime_for_year = crime_ts_df[crime_ts_df["Year"] == year]["BOROUGH_MEAN_IN_YEAR"].values[0]
      search_borough_crime_for_year_fmt = "{:,.4f}".format(float(search_borough_crime_for_year))
      crime_benchmark_data_row.append(search_borough_crime_for_year_fmt)
  
      ## Max
      crime_benchmark_data_row.append(max_str)
      
      crime_benchmark_data.append(crime_benchmark_data_row)
  
  crime_benchmark_table = pd.DataFrame(data=crime_benchmark_data, columns=["Year", "Borough with Lowest Crime per Person", f"{borough} Crime per Person", "Borough with Highest Crime per Person"])
  report_context["crime_benchmark_table"] = crime_benchmark_table


  crime_narrative_04 = f"The {{}} table shows the boroughs with the lowest and highest crimes per person in the same period. The middle column shows the crimes per person in {borough} for the same year."
  report_context["crime_narrative_04"] = crime_narrative_04

  # crime_benchmark_data_df = crime_benchmark_data_df.set_index("Year")
  
  ####
  #### DELETE 
  ####
  # from IPython.display import HTML
  # styles = [
  #   dict(selector="tr", props=[("font-size", "120%"),
  #                              ("text-align", "right")])
  # ]
  #
  # crime_benchmark_data_df_html = (crime_benchmark_data_df.style.set_table_styles(styles))
  #
  #
  # crime_benchmark_display_table_file_name = "{}/{}_crime_benchmark_display_table_{}_{}_{}.png".format(save_image_path, session_id, city, borough, ward_name) 
  #mlib.save_df(crime_benchmark_data_df_html, crime_benchmark_display_table_file_name, save_artefacts=True)
  ####
  #### DELETE 
  ####
  
  ###
  ### IF YOU USE THE RENDERED VERSION IT CAUSES AN EXCEPTION - SAME AS BELOW
  ### 
  
  # mlib.save_df(crime_benchmark_data_df, crime_benchmark_display_table_file_name, save_artefacts=True)
  # report_context["crime_benchmark_display_table"] = crime_benchmark_display_table_file_name
  
  ##
  ##
  
  borough_top_crime_per_by_year_df = dao_fac.crime_major_category_in_borough_years(db_conn, search_term)

  ##
  ##

  columns = ["Year", "1st", "2nd", "3rd", "4th", "5th"]
  borough_top_crime_data = []
  
  unique_years_cat = sorted(unique_years, reverse=True)
  
  for year in unique_years_cat:
      borough_top_crime_data_row = []
      borough_top_crime_per_by_year = borough_top_crime_per_by_year_df[borough_top_crime_per_by_year_df["YEAR"] == year]
  
      borough_top_crime_data_row.append(str(year))
      for i in range(0,5):
          try:
              major_category = borough_top_crime_per_by_year[i:i+1]["MAJOR_CATEGORY"].values[0]
              borough_total_crime = borough_top_crime_per_by_year[i:i+1]["BOROUGH_TOTAL_CRIME"].values[0]
              borough_total_crime_fmt = "{:,.0f}".format(borough_total_crime)
              maj_cat_tot = f"{major_category} - [{borough_total_crime_fmt}]"
              borough_top_crime_data_row.append(maj_cat_tot)
          except:
              borough_top_crime_data_row.append("-NA-")
  
      borough_top_crime_data.append(borough_top_crime_data_row)
  
  borough_top_crime_table = pd.DataFrame(data=borough_top_crime_data, columns=columns)
  report_context["borough_top_crime_table"] = borough_top_crime_table
  
  borough_top_crime_table_narrative_date = "between {} and {}".format(year_from, year_to) if year_from != year_to else \
                                           "in {}".format(year_to)
  
  borough_top_crime_table_narrative = f"The {{}} table shows the top 5 crimes in {borough} {borough_top_crime_table_narrative_date}. Bracketed values are the reported number of that crime."
  report_context["borough_top_crime_table_narrative"] = borough_top_crime_table_narrative 
    
  # borough_top_crime_data_df = borough_top_crime_data_df.set_index("Year")
  
  ## Sort in descending date order
  # borough_top_crime_data_df.sort_index(ascending=False)
  
  # from IPython.display import HTML
  # styles = [
  #   dict(selector="tr", props=[("font-size", "110%"),
  #                              ("text-align", "right")])
  # ]
  #
  # borough_top_crime_data_df_html = (borough_top_crime_data_df.style.set_table_styles(styles))
  # crime_top_crimes_display_table_file_name = "{}/{}_crime_top_crimes_display_table_{}_{}_{}.png".format(save_image_path, session_id, city, borough, ward_name) 
  # mlib.save_df(borough_top_crime_data_df, crime_top_crimes_display_table_file_name, save_artefacts=True)
  # report_context["crime_top_crimes_display_table"] = crime_top_crimes_display_table_file_name
  
  ###
  ### IF YOU USE THE RENDERED VERSION IT CAUSES AN EXCEPTION - SAME AS ABOVE
  ### 
  ## Change this back 
  # mlib.save_df(borough_top_crime_data_df_html, crime_top_crimes_display_table_file_name, save_artefacts=True)
  
  db_conn.close()
  