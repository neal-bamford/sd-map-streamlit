from data.daos import location_dao as loc_dao
from lib import masters_data_analytics_lib as lib

search_term = {"city"      : "london"
            , "ward_name"  : ""
             , "borough"   : ""
             , "post_code" : "BR1 1AA"}


sd_london_postcodes_file = "./data/streamlit_{}_postcodes_oa.csv".format(search_term["city"])
data                     = lib.csv_to_dataframe(sd_london_postcodes_file)


result = loc_dao.location_search(search_term, data)

print(result)

search_city      = "London"
search_borough   = "Bromley"
search_ward_name = "Bromley Town"
post_codes = loc_dao.list_post_codes_for_borough_ward_name(search_borough, search_ward_name, data)
print(post_codes)

wards = loc_dao.list_wards_for_borough(search_borough, data)
print(wards)

boroughs = loc_dao.list_boroughs_for_city(search_city, data)
print(boroughs)