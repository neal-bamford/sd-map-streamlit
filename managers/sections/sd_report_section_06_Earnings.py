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

GBP_SYMBOL = u"\xA3"

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
  
  # # index = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]
  # data = [[2010, 25370], [2011, 25896], [2012, 26312], [2013, 26884], [2014, 26936], [2015, 27404], [2016, 28028], \
  #         [2017, 28600], [2018, 29536], [2019, 30420], [2020,30472], [2021, 31772]]
  #
  # average_country_earnings_df = pd.DataFrame(data=data, columns=["YEAR", "MEAN_INCOME_GBP_COUNTRY"])

  ##
  ##
  
  earnings_min_max_year_df = dao_fac.earnings_min_max_year(db_conn)

  log.debug(earnings_min_max_year_df)
  
  earnings_year_from = year_from
  earnings_year_to   = year_to
  
  earnings_year_min = earnings_min_max_year_df["MIN_YEAR"].values[0]
  earnings_year_max = earnings_min_max_year_df["MAX_YEAR"].values[0]
  
  earnings_year_from_orig = earnings_year_from
  earnings_year_to_orig = earnings_year_to
  
  if earnings_year_from < int(earnings_year_min):
      earnings_year_from = int(earnings_year_min)
  elif earnings_year_from > int(earnings_year_max):
      earnings_year_from = int(earnings_year_max)
  
  if earnings_year_to > int(earnings_year_max):
      earnings_year_to = int(earnings_year_max)
  elif earnings_year_to < int(earnings_year_min):
      earnings_year_to = int(earnings_year_min)
  
  log.debug(f"earnings orig_year_to    :{earnings_year_to_orig}")
  log.debug(f"earnings search_year_to  :{earnings_year_to}")
  
  search_term = {"year_from":earnings_year_from,
                 "year_to"  :earnings_year_to,
                 "borough"  :borough,
                 "ward_name":ward_name}
  
  ## Get the UK Average Earnings
  average_country_earnings_df = dao_fac.uk_earnings_year(db_conn, search_term)

  ## DATAFRAME
  borough_earnings_ranking_by_year_df = dao_fac.earnings_ranked_by_borough_years(db_conn, search_term)
  
  ## MIN TO MAX YEARS TO SCROLL THROUGH
  unique_years = borough_earnings_ranking_by_year_df["YEAR"].unique().tolist()
  
  # average_country_earnings_df.info()
  
  ##
  ##
  
  earnings_changed_search_date_dates     = f"The new date is {earnings_year_to}" if earnings_year_from == earnings_year_to else \
                                           f"The new dates are {earnings_year_from} to {earnings_year_to}"

  earnings_changed_search_s              = f" was" if earnings_year_from == earnings_year_to else \
                                           f"s were"
  
  earnings_narrative_01 = f"Your original search date{earnings_changed_search_s} changed to match the date range of the earnings data. {earnings_changed_search_date_dates}. " \
                                           if ((earnings_year_from != earnings_year_from_orig) or \
                                               (earnings_year_to   != earnings_year_to_orig)) else ""
  
  report_context["earnings_narrative_01"] = earnings_narrative_01

  ##
  ##
  
  index = []
  data  = []
  columns = ["CITY_MAX_IN_YEAR", "CITY_MEAN_IN_YEAR", "CITY_MIN_IN_YEAR", "BOROUGH_MEAN_IN_YEAR", "ACTUAL_ESTIMATE", "COUNTRY_MEAN_IN_YEAR"]
  
  unique_years_plot = sorted(unique_years)
  
  for year in unique_years_plot:
      data_row = []
      city_max_in_year     = borough_earnings_ranking_by_year_df[borough_earnings_ranking_by_year_df["YEAR"] == year]["MEAN_INCOME_GBP_BOROUGH"].max()
      city_mean_in_year    = borough_earnings_ranking_by_year_df[borough_earnings_ranking_by_year_df["YEAR"] == year]["MEAN_INCOME_GBP_BOROUGH"].mean()
      city_min_in_year     = borough_earnings_ranking_by_year_df[borough_earnings_ranking_by_year_df["YEAR"] == year]["MEAN_INCOME_GBP_BOROUGH"].min()
      borough_mean_in_year = borough_earnings_ranking_by_year_df[(borough_earnings_ranking_by_year_df["YEAR"] == year) &
                                                               (borough_earnings_ranking_by_year_df["BOROUGH"] == borough)]["MEAN_INCOME_GBP_BOROUGH"].values[0]
      borough_actual_estimate_in_year = borough_earnings_ranking_by_year_df[(borough_earnings_ranking_by_year_df["YEAR"] == year) &
                                                               (borough_earnings_ranking_by_year_df["BOROUGH"] == borough)]["MEAN_INCOME_ACTUAL_ESTIMATED"].values[0]
      # country_mean_in_year = average_country_earnings_df[average_country_earnings_df["YEAR"] == int(year)]["MEAN_INCOME_GBP_COUNTRY"].values[0]
      country_mean_in_year = average_country_earnings_df[average_country_earnings_df["YEAR"].astype(int) == int(year)]["MEAN_INCOME_GBP_COUNTRY"].values[0]
          
      max_in_year_fmt          = "{}{:,.0f}".format(GBP_SYMBOL, city_max_in_year)
      mean_in_year_fmt         = "{}{:,.0f}".format(GBP_SYMBOL, city_mean_in_year)
      min_in_year_fmt          = "{}{:,.0f}".format(GBP_SYMBOL, city_min_in_year)
      borough_mean_in_year_fmt = "{}{:,.0f}".format(GBP_SYMBOL, borough_mean_in_year)
      country_mean_in_year_fmt = "{}{:,.0f}".format(GBP_SYMBOL, country_mean_in_year)
          
      index.append(year)
      data_row.append(city_max_in_year)
      data_row.append(city_mean_in_year)
      data_row.append(city_min_in_year)
      data_row.append(borough_mean_in_year)
      data_row.append(borough_actual_estimate_in_year)
      data_row.append(country_mean_in_year)
      data.append(data_row)
      # log.debug(f"[{borough}]-{year} - borough mean:{borough_mean_in_year_fmt} - city max:{max_in_year_fmt} - city mean:{mean_in_year_fmt} - city min:{min_in_year_fmt} - country mean:{country_mean_in_year_fmt}")
      
  earning_ts_df = pd.DataFrame(data=data, index=index, columns=columns)    
  earning_ts_df["Year"] = earning_ts_df.index
  
  ## Estimated or Actual
  earning_ts_estimated_df = None
  earning_ts_estimated_df = earning_ts_df[earning_ts_df["ACTUAL_ESTIMATE"] == "e"][["BOROUGH_MEAN_IN_YEAR", "ACTUAL_ESTIMATE"]]
  earning_ts_estimated_df["Year"] = earning_ts_estimated_df.index

  ##
  ##
  
  earnings_plot_desctiption_year_range = f"between {earnings_year_from} and {earnings_year_to}" if earnings_year_to != earnings_year_from else f"for {earnings_year_to}"
  earnings_narrative_02 = f"The graph {{}} compares the average earnings in the {city} borough of {borough} {earnings_plot_desctiption_year_range} with the {city} maximum, minimum and average and with the country average."
  report_context["earnings_narrative_02"] = earnings_narrative_02
  
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
  sns.lineplot(data=earning_ts_df, x="Year", y="CITY_MAX_IN_YEAR",     ax=ax, label=f"{city} Max.",   color='blue', marker=marker)
  sns.lineplot(data=earning_ts_df, x="Year", y="CITY_MEAN_IN_YEAR",    ax=ax, label=f"{city} Avg.",    color='green', marker=marker)
  sns.lineplot(data=earning_ts_df, x="Year", y="CITY_MIN_IN_YEAR",     ax=ax, label=f"{city} Min.",    color='red', marker=marker)
  sns.lineplot(data=earning_ts_df, x="Year", y="BOROUGH_MEAN_IN_YEAR", ax=ax, label=f"{borough} Avg.", color='orange', marker=marker)
  sns.scatterplot(data=earning_ts_estimated_df, x="Year", y="BOROUGH_MEAN_IN_YEAR", ax=ax, label=f"{borough} Avg. Estimated", color="orange", s=200)
  sns.lineplot(data=earning_ts_df, x="Year", y="COUNTRY_MEAN_IN_YEAR", ax=ax, label=f"Country Avg.", color='grey', marker=marker)
  
  plot_title = "Earnings  between {} and {}".format(earnings_year_from, earnings_year_to) if earnings_year_from != earnings_year_to else \
               "Earnings for {}".format(earnings_year_to)
  
  ax.set_title(plot_title, fontsize=20)
  ax.set_ylabel("Earnings (GBP)", fontsize=20)
  ax.set_xlabel("Year", fontsize=20)
  ax.tick_params(axis="x", labelrotation=45)
  
  ax.legend(title="legend")
  ax.legend(loc="upper right")
  plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
  
  ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
  
  for line in ax.get_lines():
      line.set_linewidth(5)
      line.set_ms(10)
  
  ax.grid(False)
  plt.yticks(fontsize=20)
  plt.xticks(fontsize=20)
  
  plt.tight_layout()
  
  earnings_time_series_plot = plt.gcf()
  
  earnings_time_series_plot_file = "{}/{}_earnings_time_series_plot_{}_{}_{}.png".format(save_image_path, session_id, city, year_from, year_to)
  mlib.save_plot_filename(plot=earnings_time_series_plot, filename=earnings_time_series_plot_file, save_artefacts=True)
  report_context["earnings_time_series_plot"] = earnings_time_series_plot_file
  
  ##
  ##
  
  ## The maximum year from the data set
  earnings_latest_year = average_country_earnings_df["YEAR"].max()
  earnings_latest_year = year_to
  
  ## The Average earnings across all the boroughs for that year
  borough_earnings_ranking_filtered_max_year_df =  borough_earnings_ranking_by_year_df[borough_earnings_ranking_by_year_df["YEAR"].astype(int) == earnings_year_to]
  
  
  latest_city_max_mean_salary     = borough_earnings_ranking_filtered_max_year_df["MEAN_INCOME_GBP_BOROUGH"].max()
  latest_city_mean_mean_salary    = borough_earnings_ranking_filtered_max_year_df["MEAN_INCOME_GBP_BOROUGH"].mean()
  latest_borough_mean_salary      = borough_earnings_ranking_filtered_max_year_df[borough_earnings_ranking_filtered_max_year_df["BOROUGH"] == borough]["MEAN_INCOME_GBP_BOROUGH"].values[0]
  latest_city_min_mean_salary     = borough_earnings_ranking_filtered_max_year_df["MEAN_INCOME_GBP_BOROUGH"].min()
  latest_country_mean_mean_salary = average_country_earnings_df[average_country_earnings_df["YEAR"] == earnings_year_to]["MEAN_INCOME_GBP_COUNTRY"].values[0]
  
  
  def prepend(a, b):
    ret_val = ""
    if a > b:
      ret_val = "significantly " if a/b >= 2.0 else ""
    elif a < b:
      ret_val = "significantly " if b/a >= 2.0 else ""
    return ret_val
  
  def above_below_equal(a, b):
      ret_val = ""
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
  
      return ret_val
  
  
  ## Format the latest for the text
  ### City
  latest_city_max_mean_salary_fmt     = "{}{:,.0f}".format(GBP_SYMBOL, float(latest_city_max_mean_salary))
  latest_city_mean_mean_salary_fmt    = "{}{:,.0f}".format(GBP_SYMBOL, float(latest_city_mean_mean_salary))
  latest_borough_mean_salary_fmt      = "{}{:,.0f}".format(GBP_SYMBOL, float(latest_borough_mean_salary))
  latest_city_min_mean_salary_fmt     = "{}{:,.0f}".format(GBP_SYMBOL, float(latest_city_min_mean_salary))
  ### Country
  latest_country_mean_mean_salary_fmt = "{}{:,.0f}".format(GBP_SYMBOL, float(latest_country_mean_mean_salary))
  
  ## Preamble
  part_01 = f"The {earnings_year_to} earnings in {borough} are {latest_borough_mean_salary_fmt}"
  
  ## CITY BOROUGH MEAN COMPARE TO CITY MEAN MEAN [X]
  mean_explanation = f"{prepend(latest_borough_mean_salary, latest_city_mean_mean_salary)}{above_below_equal(latest_borough_mean_salary, latest_city_mean_mean_salary)}"
  part_02 = f". This is {mean_explanation} the average for {city} in the same period of {latest_city_mean_mean_salary_fmt}"
  
  # CITY BOROUGH MEAN COMPARE TO CITY MAX MEAN [X]
  max_explanation = f"{prepend(latest_borough_mean_salary, latest_city_max_mean_salary)}{above_below_equal(latest_borough_mean_salary, latest_city_max_mean_salary)}"
  part_03 = f" and is {max_explanation} the average maximum of {latest_city_max_mean_salary_fmt}"
  
  # average across {city} for the same period of {latest_city_max_mean_salary_fmt}"
  
  ## CITY BOROUGH MEAN COMPARE TO CITY MIN MEAN [X]
  min_explanation = f"{prepend(latest_borough_mean_salary, latest_city_min_mean_salary)}{above_below_equal(latest_borough_mean_salary, latest_city_min_mean_salary)}"
  part_04 = f". It is {min_explanation} the average minimum of {latest_city_min_mean_salary_fmt}"
  
  ## CITY BOROUGH MEAN COMPARE TO COUNTRY MEAN MEAN [X] 
  country_mean_explanation = f"{prepend(latest_borough_mean_salary, latest_country_mean_mean_salary)}{above_below_equal(latest_borough_mean_salary, latest_country_mean_mean_salary)}"
  part_05 = f" and is {country_mean_explanation} the country average of {latest_country_mean_mean_salary_fmt}."
  
  from scipy import stats
 
  y  = [earning_ts_df["BOROUGH_MEAN_IN_YEAR"].tolist()]
  x  = earning_ts_df.index.astype(int).tolist()
  
  part_06 = ""
  
  if len(x) >= 3:
  
      log.debug(y)
      log.debug(x)
  
  
      slope, intercept, r, p, std_err = stats.linregress(x, y)
      ## Round to nearest pound
      # slope = round(slope,0)
      log.debug(f"slope:{slope}")

      ## Remained level
      if slope == 0.0:
          rate = "have remained level"
      ## Decreased
      elif slope < 0.0:
          rate = "have decreased"
      ## Increased
      else:
          rate = "have risen"
  
      part_06 = f" Over the period {earnings_year_from} to {earnings_year_to} average earnings in {borough} {rate}."
  
  part_07 = f""
  
  if not earning_ts_estimated_df.empty:
      estimated_list = earning_ts_estimated_df.index.to_list()
      year_prefix = "the " if len(estimated_list) == 1 else ""
      year_suffix = "" if len(estimated_list) == 1 else "s"
      estimated_prefix = "is" if len(estimated_list) == 1 else "are"
      
      part_07 = f" Please note that the earnings for {year_prefix}year{year_suffix} {sd_formatting.series_format(estimated_list)} {estimated_prefix} estimated."
      
  ### Put them all together  [ ]
  earnings_narrative_03 = f"{earnings_narrative_01}{part_01}{part_02}{part_03}{part_04}{part_05}{part_06}{part_07}"

  report_context["earnings_narrative_03"] = earnings_narrative_03
  
  ##
  ##
  
  years_sorted = borough_earnings_ranking_by_year_df["YEAR"].sort_values().drop_duplicates()
  first_year = years_sorted.iloc[0]
  borough_sort_order = borough_earnings_ranking_by_year_df.loc[borough_earnings_ranking_by_year_df["YEAR"]==first_year]["BOROUGH"]
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
  
          borough_ranking_for_year = borough_earnings_ranking_by_year_df.loc[(borough_earnings_ranking_by_year_df["BOROUGH"]==_borough) &
                                                                             (borough_earnings_ranking_by_year_df["YEAR"]==year)]["RANK"].values[0]
  
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
  title = f"Borough Rankings of Average Earnings {earnings_year_from} and {earnings_year_to}" if earnings_year_from != earnings_year_to else \
          f"Borough Rankings of Average Earnings in {earnings_year_to}"
  
  ax.set_title(title, fontsize=20)
  
  plt.xticks(fontsize=10)
  
  ## Generate labels from the Borough names for the Y Axis
  plt.yticks(range(1, len(borough_sort_order)+1), [borough_sort_order.iloc[i] for i in range(len(borough_sort_order))])
  plt.yticks(fontsize=15)
  
  ## Secondary Y axis to show top middle and bottom
  ax2 = ax.secondary_yaxis("right")
  ax2.tick_params(labelsize = 20, length=0)
  ax2.set_yticks(ax.get_yticks().tolist())
  ax2.set_yticklabels(["Top", "", "", "", "", "", "", "", "", "", "", "Middle", "", "", "", "", "", "", "", "", "", "", "Bottom", "", "", "", "", "", "", "", "", "",""])
  ax2.minorticks_off()

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
  
  earnings_bump_chart_plot = plt.gcf()           
  
  earnings_bump_chart_plot_file = "{}/{}_earnings_bump_chart_plot_{}_{}_{}.png".format(save_image_path, session_id, city, year_from, year_to)
  mlib.save_plot_filename(plot=earnings_bump_chart_plot, filename=earnings_bump_chart_plot_file, save_artefacts=True)
  report_context["earnings_bump_chart_plot"] = earnings_bump_chart_plot_file
  
  ##
  ##
  
  earnings_bump_chart_date_range = f"over the period {earnings_year_from} to {earnings_year_to}" if earnings_year_from != earnings_year_to else f"for {earnings_year_to}"
  earnings_bump_chart_narrative_01 = f"How {borough} ranks with the other {city} boroughs {earnings_bump_chart_date_range} can be seen {{}}. Ranking is top to bottom, with the top representing the highest earnings."

  report_context["earnings_bump_chart_narrative_01"] = earnings_bump_chart_narrative_01
  
  ##
  ##
  
  earnings_benchmark_data = []
  
  ## Loop through the years to create our data frame for benchmarking
  
  unique_years_bench = sorted(unique_years, reverse=True)
  
  for year in unique_years_bench:
    ## Vertical Slice  
    borough_year_data = all_borough_ranking_by_year_df[year] 
    ## Loop through each borough
    idx = 0;
    
    ## Add uear to the dataframe row
    earnings_benchmark_data_row = []
    earnings_benchmark_data_row.append(str(year))
  
    for earnings_borough in borough_year_data.index:
      ranking = borough_year_data[idx]     
      borough_max_min_earnings_year = earning_ts_df[earning_ts_df["Year"].astype(int) == int(year)][["CITY_MAX_IN_YEAR", "CITY_MIN_IN_YEAR"]]
      
      max_borough_earnings_for_year = borough_max_min_earnings_year["CITY_MAX_IN_YEAR"]
      max_borough_earnings_for_year_fmt = "{}{:,.0f}".format(GBP_SYMBOL, float(max_borough_earnings_for_year))
      
      min_borough_earnings_for_year = borough_max_min_earnings_year["CITY_MIN_IN_YEAR"]
      min_borough_earnings_for_year_fmt = "{}{:,.0f}".format(GBP_SYMBOL, float(min_borough_earnings_for_year))
  
      # log.debug(ranking)
      if ranking == 1:
        max_str = f"{earnings_borough} - {max_borough_earnings_for_year_fmt}"
      
      if ranking == 33:
        min_str = f"{earnings_borough} - {min_borough_earnings_for_year_fmt}"
      
      idx += 1
      
    ## Lowest borough in year
    earnings_benchmark_data_row.append(min_str)
    
    ## Our borough's 
    search_borough_avg_earnings_year = earning_ts_df[earning_ts_df["Year"] == year]["BOROUGH_MEAN_IN_YEAR"].values[0]
    search_borough_avg_earnings_year_fmt = "{}{:,.0f}".format(GBP_SYMBOL, float(search_borough_avg_earnings_year))
    earnings_benchmark_data_row.append(search_borough_avg_earnings_year_fmt)
  
    ## Highest borough in year
    earnings_benchmark_data_row.append(max_str)
    
    earnings_benchmark_data.append(earnings_benchmark_data_row)
    
    earnings_benchmark_table = pd.DataFrame(data=earnings_benchmark_data, columns=["Year", "Borough with Lowest Avg. Earnings", f"{borough} Avg. Earnings", "Borough with Highest Avg. Earnings"])
    # earnings_benchmark_table = earnings_benchmark_table.set_index("Year")
    
    report_context["earnings_benchmark_table"] = earnings_benchmark_table
    
    
  earnings_narrative_04 = f"The {{}} table shows the boroughs with the lowest and highest average earning boroughs in the same period. The middle column shows the average earnings in {borough} for the same year."
  report_context["earnings_narrative_04"] = earnings_narrative_04
      
  #
  ## BUMP CHART NARRATIVE TO EXPLAIN WHERE IT RANKS IN THE THREE BANDS
  #

  ## Leave it blank if only one year's worth of data
  earnings_bump_chart_narrative_02 = "" 
  
  ## Can only analyse if we have at least two years
  if year_from != year_to:
      borough_yearly_rankings = all_borough_ranking_by_year_df[all_borough_ranking_by_year_df.index == borough]
      
      top = 0
      middle = 0
      bottom = 0

      above = 0
      same  = 0
      below = 0
      start_rank = None

      for column in borough_yearly_rankings:
          rank = borough_yearly_rankings[column].values[0]
          if rank <= 11:
              top += 1
          elif rank >= 23:
              bottom +=1
          else:
              middle += 1


          if start_rank == None:
              start_rank = rank
          else:    
              if rank > start_rank:
                  below += 1
              elif rank < start_rank:
                  above += 1
              else:
                  same +=1

      all = top + middle + bottom
      top_pct = round((top/all*100),0)
      middle_pct = round((middle/all*100),0)
      bottom_pct = round((bottom/all*100),0)

      all = above + same + below
      above_pct = round((above/all*100),0)
      same_pct  = round((same/all*100),0)
      below_pct  = round((below/all*100),0)

      def place(pct, list=["never", "occasionally", "frequently", "constantly", "always"]):
          ret_val = list[0] if pct ==  0 else \
                    list[1] if pct <  25 else \
                    list[2] if pct <  50 else \
                    list[3] if pct < 100 else \
                    list[4]
          
          return ret_val

      def not_empty_count(list_items):
          not_empty_count = 0
          for item in list_items:
              if not item:
                  not_empty_count +=1
          return not_empty_count

      def stf(str_list):
          ret_val = 0
          ret_val += 4 if str_list[0] else 0
          ret_val += 2 if str_list[1] else 0
          ret_val += 1 if str_list[2] else 0

          return ret_val

      earnings_vertical_narrative_top    = "" if top_pct == 0 else f" {place(top_pct)} in the higher earning boroughs"
      middle_inc_earnings_rate_borough   = "" if "earning boroughs" in earnings_vertical_narrative_top else " earning boroughs" 
      earnings_vertical_narrative_middle = "" if middle_pct == 0 else f" {place(middle_pct)} in the middle{middle_inc_earnings_rate_borough}"
      bottom_inc_earnings_rate_borough   = "" if ("earning boroughs" in earnings_vertical_narrative_middle) or ("earning boroughs" in earnings_vertical_narrative_top) else " earning boroughs" 
      earnings_vertical_narrative_bottom = "" if bottom_pct == 0 else f" {place(bottom_pct)} in the bottom{bottom_inc_earnings_rate_borough}"
      
      ## The sentance has the same set of punctuations, but with differening needs for spaces 
      v_punct_list_pos_1 = ["", "", "", "", "", " and", ", "]
      v_punct_list_pos_2 = ["", "", " and", "", " and is ", "", " and"]
      
      h_punct_list_pos_1 = ["", "", "", "", "", " and ", ", "]
      h_punct_list_pos_2 = ["", "", " and ", "", " and ", "", " and "]

      comma_or_and_1_v = v_punct_list_pos_1[stf([earnings_vertical_narrative_top,earnings_vertical_narrative_middle, earnings_vertical_narrative_bottom])-1]
      comma_or_and_2_v = v_punct_list_pos_2[stf([earnings_vertical_narrative_top,earnings_vertical_narrative_middle, earnings_vertical_narrative_bottom])-1]

      earnings_vertical_narrative = f"{borough} is{earnings_vertical_narrative_top}{comma_or_and_1_v}{earnings_vertical_narrative_middle}{comma_or_and_2_v}{earnings_vertical_narrative_bottom}"

      earnings_horizontal_up   = "" if "never" in place(above_pct) else f"{place(above_pct, list=['never', 'sometimes', 'frequently', 'very frequently', 'always'])} moves up"
      earnings_horizontal_same = "" if "never" in place(same_pct)  else f"{place(same_pct,  list=['never', 'sometimes', 'frequently', 'very frequently', 'always'])} stays level"
      earnings_horizontal_down = "" if "never" in place(below_pct) else f"{place(below_pct, list=['never', 'sometimes', 'frequently', 'very frequently', 'always'])} moves down"

      comma_or_and_1_h = h_punct_list_pos_1[stf([earnings_horizontal_up, earnings_horizontal_same, earnings_horizontal_down])-1]
      comma_or_and_2_h = h_punct_list_pos_2[stf([earnings_horizontal_up, earnings_horizontal_same, earnings_horizontal_down])-1]

      earnings_horizontal_narrative = f"{earnings_horizontal_up}{comma_or_and_1_h}{earnings_horizontal_same}{comma_or_and_2_h}{earnings_horizontal_down}"
      # log.debug(earnings_vertical_narrative)
      # log.debug(earnings_horizontal_narrative)

      earnings_bump_chart_narrative_02 = f"{earnings_vertical_narrative}. Where it {earnings_horizontal_narrative} with respect to its starting rank."  
      
  report_context["earnings_bump_chart_narrative_02"] = earnings_bump_chart_narrative_02
  
  db_conn.close()
  