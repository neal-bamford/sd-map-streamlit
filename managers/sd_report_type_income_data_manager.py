from lib import db_tools as db_tools
from lib import formatting as fmt
from lib import general_tools as gen_tools
from lib import masters_data_analytics_lib as mlib
from lib import plot_tools as plttool
from lib import stats as stats
from data.daos import location_dao as loc_dao

import logging
import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

def generate_report_data(session_id
					   , search_term
					   , report_context
				   	 , properties
					   , **kwargs):  
	"""
	Manager to create the formatted String data to include in the sd_general_report_data
	"""
	
	## These are the pandas dataframes used in this manager. They may be used in others too
	sd_london_postcodes_df         = kwargs["sd_london_postcodes_df"]
	sd_london_population_oa_df     = kwargs["sd_london_population_oa_df"]
	sd_london_household_oa_df      = kwargs["sd_london_household_oa_df"]
	sd_london_qualification_oa_df  = kwargs["sd_london_qualification_oa_df"] 

	## Validate the search term	
	validated_search_term = loc_dao.location_search(search_term, sd_london_postcodes_df)
	
	## Merge any non validated values with validated ones for future use	
	validated_search_term = gen_tools.merge_two_dicts(search_term, validated_search_term)
	report_context["validated_search_term"] = validated_search_term

	
	city      = validated_search_term["city"]
	borough   = validated_search_term["borough"]
	ward_name = validated_search_term["ward_name"]
	oacode    = validated_search_term["oacode"]
	post_code = validated_search_term["post_code"]
	
	year_from = validated_search_term["year_from"]
	year_to   = validated_search_term["year_to"]
	
	## These need to be behind DAOs
	all_ward_post_codes = loc_dao.list_post_codes_for_borough_ward_name(borough, ward_name, sd_london_postcodes_df)
	all_borough_wards   = loc_dao.list_wards_for_borough(borough, sd_london_postcodes_df)
	
	other_post_codes = all_ward_post_codes
	if post_code != "":
		other_post_codes = np.delete(all_ward_post_codes, np.where(all_ward_post_codes == post_code))
	
	other_wards = np.delete(all_borough_wards, np.where(all_borough_wards == ward_name))
	number_of_boroughs = len(loc_dao.list_boroughs_for_city(city, sd_london_postcodes_df))

	map_args = {}
	
	if post_code != "":
		post_code_combined = loc_dao.list_lat_long_postcode(validated_search_term, sd_london_postcodes_df)
		map_args["post_code"] = {"label":post_code, "lat_long":post_code_combined}
	
	ward_name_combined = loc_dao.list_lat_long_ward_name(validated_search_term, sd_london_postcodes_df)
	map_args["ward_name"] = {"label":ward_name, "lat_long":ward_name_combined}

	borough_combined = loc_dao.list_lat_long_borough(validated_search_term, sd_london_postcodes_df)
	map_args["borough"] = {"label":borough, "lat_long":borough_combined}

	report_context["map_args"] = map_args


	### Connect to the database and get some income data
 # year_from = 2012
 # year_to   = 2018


	db_conn = db_tools.get_db_conn(properties[properties["database"]["flavour"]] )

	city_income_min_max_avg_sql ="""
	SELECT [Date] 						                AS [Date]
	      , ROUND(AVG([total_annual_income_net_gbp]),0) AS [city_total_annual_income_net_gbp_avg]
	      , ROUND(MIN([total_annual_income_net_gbp]),0) AS [city_total_annual_income_net_gbp_min]
	      , ROUND(MAX([total_annual_income_net_gbp]),0) AS [city_total_annual_income_net_gbp_max]
	FROM income_uk_ons 		 INC
	WHERE [MSOA] IN (SELECT DISTINCT [LPC].[MSOA] FROM IDX_LONDONPOSTCODES LPC)
	AND   CONVERT(int, [Date]) BETWEEN {} AND {}
	GROUP BY [Date]
	ORDER BY [Date] ASC;
	""".format(year_from, year_to)
	
	city_min_max_avg_df = pd.read_sql_query(city_income_min_max_avg_sql, db_conn, index_col="Date")
	# log.debug(city_min_max_avg_df.head())
	
	ward_income_avg_sql = """
  SELECT [Date] 						                AS [Date]
        , ROUND(AVG([total_annual_income_net_gbp]),0) AS [ward_total_annual_income_net_gbp_avg]
  FROM income_uk_ons 		 INC
     , IDX_LONDONPOSTCODES LPC
  WHERE INC.[MSOA] = LPC.[MSOA]
  AND   INC.[LAD]  = LPC.[LAD]
  AND   LPC.[LAD_NAME] = '{}'
  AND   LPC.[WARD_NAME] = '{}'
  AND   CONVERT(int, [Date]) BETWEEN {} AND {}
  GROUP BY [Date];
  """.format(borough, ward_name, year_from, year_to)
  
  
	ward_income_avg_sql = """
  SELECT [Date] 						                       AS [Date]
     , ROUND(AVG([total_annual_income_net_gbp]),0) AS [ward_total_annual_income_net_gbp_avg]
    FROM income_uk_ons 		   INC
       , IDX_LONDONPOSTCODES LPC
    WHERE EXISTS (
        SELECT 1/0
        FROM IDX_LONDONPOSTCODES LPC
        WHERE [LPC].[MSOA] = INC.[MSOA]
        )
    AND   INC.[LAD]  = LPC.[LAD]
    AND   LPC.[LAD_NAME] = '{}'
    AND   LPC.[WARD_NAME] = '{}'
    AND   CONVERT(int, [Date]) BETWEEN {} AND {}
    GROUP BY [Date]
    ORDER BY [Date] DESC
    """.format(borough, ward_name, year_from, year_to)

	ward_avg_df = pd.read_sql_query(ward_income_avg_sql, db_conn, index_col="Date")
	
	
	city_ward_min_max_avg_wide_df = pd.concat([city_min_max_avg_df, ward_avg_df], axis=1)
	city_ward_min_max_avg_wide_df["Year"] = city_ward_min_max_avg_wide_df.index
	
	report_context["city_ward_min_max_avg_wide_df"] = city_ward_min_max_avg_wide_df
	
	###
	### Borough Rankings
	###
	
	borough_salary_ranking_by_year_sql = """
	WITH ranked_income_uk_ons AS (
	SELECT [INC].[Date]     AS [Date]
	     , [INC].[LAD]      AS [LAD]
	     , AVG([INC].[total_annual_income_net_gbp]) AS [total_annual_income_net_gbp_avg]
	FROM income_uk_ons INC
	WHERE [INC].[MSOA] IN (SELECT DISTINCT [LPC2].[MSOA] FROM IDX_LONDONPOSTCODES LPC2)
	GROUP BY [INC].[Date], [INC].[LAD]
	)
	SELECT [RINC].[Date]                                                 AS [Date]
	     , [RINC].[LAD]                                                  AS [LAD] 
	     , [LB].[borough]                                                AS [borough]
	     , [RINC].[total_annual_income_net_gbp_avg] 				     AS [total_annual_income_net_gbp_avg]
	     , ROW_NUMBER() OVER(
	     				PARTITION BY [Date] 
	     				ORDER BY [Date] DESC
	     				       , [total_annual_income_net_gbp_avg] DESC) AS RANK
	FROM ranked_income_uk_ons RINC
	CROSS APPLY(
		SELECT TOP 1 [LPC3].[LAD_NAME] AS [borough]
		FROM IDX_LONDONPOSTCODES LPC3
		WHERE [LPC3].[LAD] = [RINC].[LAD]) AS LB
	WHERE CONVERT(int, [Date]) BETWEEN {} AND {}
	ORDER BY [Date] DESC, [RANK] ASC"""
	
	borough_salary_ranking_by_year_df = pd.read_sql_query(borough_salary_ranking_by_year_sql.format(year_from, year_to), db_conn, index_col="Date")
	borough_salary_ranking_by_year_df["Year"] = borough_salary_ranking_by_year_df.index

	report_context["borough_salary_ranking_by_year_df"] = borough_salary_ranking_by_year_df
	

	db_conn.close()
