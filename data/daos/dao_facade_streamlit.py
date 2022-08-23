from . import location_dao as loc_dao
from . import data_dao as dat_dao
import streamlit as st
import pyodbc as pyodbc 

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

## Define how Streamlit hashes py_conn db connections - i.e. it doesn't and shouldn't
def hash_db_conn(db_conn):
    return "X"

###
### Crime
###
@st.cache(hash_funcs={pyodbc.Connection: hash_db_conn})
def crime_min_max_year(db_conn):
  return dat_dao.crime_min_max_year(db_conn)

@st.cache(hash_funcs={pyodbc.Connection: hash_db_conn})
def crime_ranked_by_borough_years(db_conn):
    return dat_dao.crime_ranked_by_borough_years(db_conn)

@st.cache(hash_funcs={pyodbc.Connection: hash_db_conn})
def crime_ranked_by_borough_years(db_conn, search_term):
    return dat_dao.crime_ranked_by_borough_years(db_conn, search_term)

@st.cache(hash_funcs={pyodbc.Connection: hash_db_conn})
def crime_major_category_in_borough_years(db_conn, search_term):
  return dat_dao.crime_major_category_in_borough_years(db_conn, search_term)

###
### Earnings
###
@st.cache(hash_funcs={pyodbc.Connection: hash_db_conn})
def earnings_ranked_by_borough_years(db_conn, search_term):    
    return dat_dao.earnings_ranked_by_borough_years(db_conn, search_term)

###
### Ethnicity
###
@st.cache(hash_funcs={pyodbc.Connection: hash_db_conn})
def ethnicity_ratio_by_borough_years(db_conn, search_term):
  return dat_dao.ethnicity_ratio_by_borough_years(db_conn, search_term)

@st.cache(hash_funcs={pyodbc.Connection: hash_db_conn})
def ethnicity_ratio_by_borough_ward_years(db_conn, search_term):
  return dat_dao.ethnicity_ratio_by_borough_ward_years(db_conn, search_term)

@st.cache(hash_funcs={pyodbc.Connection: hash_db_conn})
def ethnicity_ratio_average_years(db_conn, search_term):
  return dat_dao.ethnicity_ratio_average_years(db_conn, search_term)

###
### Education
###
@st.cache(hash_funcs={pyodbc.Connection: hash_db_conn})
def education_ratio_by_borough_years(db_conn, search_term):
  return dat_dao.education_ratio_by_borough_years(db_conn, search_term)
  
@st.cache(hash_funcs={pyodbc.Connection: hash_db_conn})
def education_ratio_by_borough_ward_years(db_conn, search_term):
  return dat_dao.education_ratio_by_borough_ward_years(db_conn, search_term)

@st.cache(hash_funcs={pyodbc.Connection: hash_db_conn})
def education_ratio_average_years(db_conn, search_term):
    return dat_dao.education_ratio_average_years(db_conn, search_term)

###
### General Health
###
@st.cache(hash_funcs={pyodbc.Connection: hash_db_conn})
def general_health_ratio_by_borough_years(db_conn, search_term):
  return dat_dao.general_health_ratio_by_borough_years(db_conn, search_term)

@st.cache(hash_funcs={pyodbc.Connection: hash_db_conn})
def general_health_ratio_by_borough_ward_years(db_conn, search_term):
  return dat_dao.general_health_ratio_by_borough_ward_years(db_conn, search_term)

@st.cache(hash_funcs={pyodbc.Connection: hash_db_conn})
def general_health_ratio_average_years(db_conn, search_term):
  return dat_dao.general_health_ratio_average_years(db_conn, search_term)  

@st.cache(hash_funcs={pyodbc.Connection: hash_db_conn})
def city_yearly_population(db_conn, search_term):
  return dat_dao.city_yearly_population(db_conn, search_term)  

@st.cache(hash_funcs={pyodbc.Connection: hash_db_conn})
def borough_yearly_population(db_conn, search_term):
  return dat_dao.borough_yearly_population(db_conn, search_term)  

@st.cache(hash_funcs={pyodbc.Connection: hash_db_conn})
def city_boroughs_wards_postcodes(db_conn, search_term):
  return dat_dao.city_boroughs_wards_postcodes(db_conn, search_term)  

@st.cache(hash_funcs={pyodbc.Connection: hash_db_conn})
def ethnicity_min_max_year(db_conn):
  return dat_dao.ethnicity_min_max_year(db_conn)  

@st.cache(hash_funcs={pyodbc.Connection: hash_db_conn})
def general_health_min_max_year(db_conn):
  return dat_dao.general_health_min_max_year(db_conn)  

@st.cache(hash_funcs={pyodbc.Connection: hash_db_conn})
def qualifications_min_max_year(db_conn):
  return dat_dao.qualifications_min_max_year(db_conn)  

@st.cache(hash_funcs={pyodbc.Connection: hash_db_conn})
def earnings_min_max_year(db_conn):
  return dat_dao.earnings_min_max_year(db_conn)  
