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
  year_from = validated_search_term["year_from"]
  year_to   = validated_search_term["year_to"]
    
  ###
  ### ALL THE FORMATTED TEXT AND PLOT FILES TO GO INTO THE REPORT GENERATION
  ###
  report_context["city"] = city.capitalize()
  report_context["ward_name"] = ward_name
  report_context["borough"] = borough
  report_context["post_code"] = post_code
  report_context["post_code_or_ward_name"] = post_code if post_code != "" else ward_name

  report_context["general_information"] = "Income Report Placeholder Text"
  
  ## Retrieve our dataframe to make the plot from
  
  city_ward_min_max_avg_wide_df = report_context["city_ward_min_max_avg_wide_df"]
  

  ###
  ### Create the plot, this could probably go into the plot_tools library to make it more generalised solution
  ###
  
  from matplotlib import pyplot as plt
  import seaborn as sns
  import matplotlib.pyplot as plt
  
  x_fig_size = 10
  y_fig_size = 6
  
  ## Set the size
  sns.set(rc={"figure.figsize":(x_fig_size, y_fig_size)})
  
  ## Set the theme
  sns.set_style("whitegrid")
  
  # plot = sns.catplot(data=city_ward_min_max_avg_wide_df, x="Year", y="salary", hue="cols", kind="point", legend=False, height=y_fig_size, aspect=x_fig_size/y_fig_size)
  
  fig, ax = plt.subplots()
  sns.lineplot(data=city_ward_min_max_avg_wide_df, x="Year", y="city_total_annual_income_net_gbp_avg", ax=ax, label='City Avg.', color='red', marker='o')
  sns.lineplot(data=city_ward_min_max_avg_wide_df, x="Year", y="city_total_annual_income_net_gbp_min", ax=ax, label='City Min.', color='orange', marker='o')
  sns.lineplot(data=city_ward_min_max_avg_wide_df, x="Year", y="city_total_annual_income_net_gbp_max", ax=ax, label='City Max.', color='yellow', marker='o')
  sns.lineplot(data=city_ward_min_max_avg_wide_df, x="Year", y="ward_total_annual_income_net_gbp_avg", ax=ax, label='Ward Avg.', color='green', marker='o')
  
  # ax.set_title("Average Salary for Ward and City between {} and {}".format(year_from, year_to))
  ax.set_title("Average Salary for Ward and City between {} and {}".format(year_from, year_to))
  ax.set_ylabel("Salary")
  ax.legend(title="legend")
  ax.legend(loc="upper right")
  plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
  plt.tight_layout()

  income_plot_file_name = "./reports/generation/images/{}_line_income_borough_{}_{}_{}.png".format(session_id, city, borough, ward_name)
  mlib.save_plot_filename(plot=fig, filename=income_plot_file_name, save_artefacts=True)
  
  report_context["income_plot_file_name"] = income_plot_file_name
