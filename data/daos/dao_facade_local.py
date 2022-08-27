from . import location_dao as loc_dao
from . import data_dao as dat_dao

import logging

log = logging.getLogger(__name__)

### LOCATION DAO
###
def location_search(search_term, data):
  return loc_dao.location_search(search_term, data)

def list_post_codes_for_borough_ward_name(search_borough, search_ward_name, data):
  return loc_dao.list_post_codes_for_borough_ward_name(search_borough, search_ward_name, data)

def list_wards_for_borough(search_borough, data):
  return loc_dao.list_wards_for_borough(search_borough, data)

def list_boroughs_for_city(search_city, data):
  return loc_dao.list_boroughs_for_city(search_city, data)

def list_lat_long_postcode(search_term, data):
  return loc_dao.list_lat_long_postcode(search_term, data)

def list_lat_long_ward_name(search_term, data):    
  return loc_dao.list_lat_long_ward_name(search_term, data)

def list_lat_long_borough(search_term, data):
  return loc_dao.list_lat_long_borough(search_term, data)


###
### DATA DAO
###

## Simple cache 

from cacheout import Cache

cache = Cache()

###
### Crime
###
@cache.memoize()
def crime_min_max_year(db_conn):
  return dat_dao.crime_min_max_year(db_conn)

@cache.memoize()
def crime_ranked_by_borough_years(db_conn):
  return dat_dao.crime_ranked_by_borough_years(db_conn)
    
@cache.memoize()
def crime_ranked_by_borough_years(db_conn, search_term):
  return dat_dao.crime_ranked_by_borough_years(db_conn, search_term)
    
@cache.memoize()
def crime_major_category_in_borough_years(db_conn, search_term):
  return dat_dao.crime_major_category_in_borough_years(db_conn, search_term)
    
###
### Earnings
###
@cache.memoize()    
def earnings_ranked_by_borough_years(db_conn, search_term):    
  return dat_dao.earnings_ranked_by_borough_years(db_conn, search_term)
  
###
### Ethnicity
###
@cache.memoize()    
def ethnicity_ratio_by_borough_years(db_conn, search_term):
  return dat_dao.ethnicity_ratio_by_borough_years(db_conn, search_term)

@cache.memoize()    
def ethnicity_ratio_by_borough_ward_years(db_conn, search_term):
  return dat_dao.ethnicity_ratio_by_borough_ward_years(db_conn, search_term)

@cache.memoize()
def ethnicity_ratio_average_years(db_conn, search_term):
  return dat_dao.ethnicity_ratio_average_years(db_conn, search_term)

###
### Education
###
@cache.memoize()
def education_ratio_by_borough_years(db_conn, search_term):
  return dat_dao.education_ratio_by_borough_years(db_conn, search_term)
  
@cache.memoize()
def education_ratio_by_borough_ward_years(db_conn, search_term):
  return dat_dao.education_ratio_by_borough_ward_years(db_conn, search_term)

@cache.memoize()
def education_ratio_average_years(db_conn, search_term):
    return dat_dao.education_ratio_average_years(db_conn, search_term)

###
### General Health
###
@cache.memoize()
def general_health_ratio_by_borough_years(db_conn, search_term):
  return dat_dao.general_health_ratio_by_borough_years(db_conn, search_term)

@cache.memoize()
def general_health_ratio_by_borough_ward_years(db_conn, search_term):
  return dat_dao.general_health_ratio_by_borough_ward_years(db_conn, search_term)

@cache.memoize()
def general_health_ratio_average_years(db_conn, search_term):
  return dat_dao.general_health_ratio_average_years(db_conn, search_term)

@cache.memoize()
def city_yearly_population(db_conn, search_term):
  return dat_dao.city_yearly_population(db_conn, search_term)  

@cache.memoize()
def borough_yearly_population(db_conn, search_term):
  return dat_dao.borough_yearly_population(db_conn, search_term)  

@cache.memoize()
def city_boroughs_wards_postcodes(db_conn, search_term):
  return dat_dao.city_boroughs_wards_postcodes(db_conn, search_term)  

@cache.memoize()
def ethnicity_min_max_year(db_conn):
  return dat_dao.ethnicity_min_max_year(db_conn)  

@cache.memoize()
def general_health_min_max_year(db_conn):
  return dat_dao.general_health_min_max_year(db_conn)  

@cache.memoize()
def qualifications_min_max_year(db_conn):
  return dat_dao.qualifications_min_max_year(db_conn)  

@cache.memoize()
def earnings_min_max_year(db_conn):
  return dat_dao.earnings_min_max_year(db_conn)  

@cache.memoize()
def uk_earnings_year(db_conn, search_term):
  return dat_dao.uk_earnings_year(db_conn, search_term) 

@cache.memoize()
def population_year(db_conn, search_term):
  return dat_dao.population_year(db_conn, search_term) 
