import sys
import numpy as np
import pandas as pd

from lib import masters_data_analytics_lib as mlib


def stats(df, borough, ward_name, oacode, column):

    oacode_lvl_sum  = df.loc[df["OAcode"] == oacode][column].values[0]
    
    ward_lvl_sum    = df.loc[(df["WARD_NAME"] == ward_name) \
                           & (df["borough"] == borough)].agg({column: ["sum"]}).values[0][0]
    
    borough_lvl_sum = df.loc[(df["borough"] == borough)].agg({column: ["sum"]}).values[0][0]
    
    city_lvl_mean   = df.groupby("borough").agg({column: ["sum"]}).mean().round(0).values[0].astype(int)

    return oacode_lvl_sum, ward_lvl_sum, borough_lvl_sum, city_lvl_mean

def post_code_fmt(post_codes):
    ret_str = ""
    for post_code in post_codes:
        ret_str += post_code + ", "
        
    ret_str = ret_str[0:len(ret_str)-2] 
    return ret_str

## Population Data    
bh_population_file = "data/bh_population.csv"

## Household Data
bh_household_file = "data/bh_household_small.csv"
bh_household_file = "data/bh_household.csv"

bh_population_df = mlib.csv_to_dataframe(bh_population_file)
bh_household_df = mlib.csv_to_dataframe(bh_household_file)

## City
city = "London"

##Search at the postcode level
post_code_search = "KT4 8NN"

## Obtain OACode for postcode - OACode is the level at which the data is set
OAcode = bh_household_df.loc[bh_household_df["postcode"] == post_code_search]["OAcode"].values[0]
other_post_codes = bh_household_df.loc[bh_household_df["OAcode"] == OAcode]["postcode"].to_numpy()
other_post_codes = np.delete(other_post_codes , np.where(other_post_codes == post_code_search))
number_of_boroughs = len(bh_household_df["borough"].unique())

## Obtain the ward_name from the OACode
ward_name = bh_household_df.loc[bh_household_df["OAcode"] == OAcode]["WARD_NAME"].values[0]
borough   = bh_household_df.loc[bh_household_df['OAcode'] == OAcode]["borough"].values[0]

## Create a copy of the dataframe and drop the duplicate OACode so we only have unique values

## Population
bh_population_drop_dup_df = bh_population_df.copy()
bh_population_drop_dup_df.drop_duplicates(subset="OAcode", keep='first', inplace=True)

## Household
bh_household_drop_dup_df = bh_household_df.copy()
bh_household_drop_dup_df.drop_duplicates(subset="OAcode", keep='first', inplace=True)


combined_str1 = "The post code {} belongs to the ward {} and borough {} within the city of {}. There are {} other post code{} which the following data is part of. These being {}".format(\
              post_code_search, ward_name, borough, city, len(other_post_codes), ("s" if len(other_post_codes) > 1 else ""), post_code_fmt(other_post_codes))

print(combined_str1)
print("\n")
print("\n")


print("post code    :{}".format(post_code_search))
print("OAcode       :{}".format(OAcode))
print("ward name    :{}".format(ward_name))
print("borough      :{}".format(borough))
print("----------------")
print("\n")
print("\n")

## Population Data
### All
pop_all_oa, pop_all_ward, pop_all_borough, pop_all_city = stats(bh_population_drop_dup_df, borough, ward_name, OAcode, "All")
print("Population")
print("===================")
print("oacode total :{}".format(pop_all_oa))
print("ward total   :{}".format(pop_all_ward))
print("borough total:{}".format(pop_all_borough))
print("borough mean :{}".format(pop_all_city))
print("----------------")

### Males
pop_male_oa, pop_male_ward, pop_male_borough, pop_male_city = stats(bh_population_drop_dup_df, borough, ward_name, OAcode, "Males")
print("Male Population")
print("===================")
print("oacode total :{}".format(pop_male_oa))
print("ward total   :{}".format(pop_male_ward))
print("borough total:{}".format(pop_male_borough))
print("borough mean :{}".format(pop_male_city))
print("----------------")

### Females
pop_female_oa, pop_female_ward, pop_female_borough, pop_female_city = stats(bh_population_drop_dup_df, borough, ward_name, OAcode, "Females")
print("Female Population")
print("===================")
print("oacode total :{}".format(pop_female_oa))
print("ward total   :{}".format(pop_female_ward))
print("borough total:{}".format(pop_female_borough))
print("borough mean :{}".format(pop_female_city))
print("----------------")

print("\n")
print("\n")
## Household Data
### Commercial Buildings
hh_cb_oa, hh_cb_ward, hh_cb_borough, hh_cb_city = stats(bh_household_drop_dup_df, borough, ward_name, OAcode, "Commercial building")
print("Commercial building")
print("===================")
print("oacode total :{}".format(hh_cb_oa))
print("ward total   :{}".format(hh_cb_ward))
print("borough total:{}".format(hh_cb_borough))
print("borough mean :{}".format(hh_cb_city))
print("----------------")

### Detached
hh_det_oa, hh_det_ward, hh_det_borough, hh_det_city = stats(bh_household_drop_dup_df, borough, ward_name, OAcode, "Detached")
print("Detached")
print("===================")
print("oacode total :{}".format(hh_det_oa))
print("ward total   :{}".format(hh_det_ward))
print("borough total:{}".format(hh_det_borough))
print("borough mean :{}".format(hh_det_city))
print("----------------")

### Flat
hh_flt_oa, hh_flt_ward, hh_flt_borough, hh_flt_city = stats(bh_household_drop_dup_df, borough, ward_name, OAcode, "Flat")
print("Flat")
print("===================")
print("oacode total :{}".format(hh_flt_oa))
print("ward total   :{}".format(hh_flt_ward))
print("borough total:{}".format(hh_flt_borough))
print("borough mean :{}".format(hh_flt_city))
print("----------------")

### Semi-Detached
hh_sem_oa, hh_sem_ward, hh_sem_borough, hh_sem_city = stats(bh_household_drop_dup_df, borough, ward_name, OAcode, "Semi-detached")
print("Semi-detached")
print("===================")
print("oacode total :{}".format(hh_sem_oa))
print("ward total   :{}".format(hh_sem_ward))
print("borough total:{}".format(hh_sem_borough))
print("borough mean :{}".format(hh_sem_city))
print("----------------")


### Terraced
hh_ter_oa, hh_ter_ward, hh_ter_borough, hh_ter_city = stats(bh_household_drop_dup_df, borough, ward_name, OAcode, "Terraced")
print("Terraced")
print("===================")
print("oacode total :{}".format(hh_ter_oa))
print("ward total   :{}".format(hh_ter_ward))
print("borough total:{}".format(hh_ter_borough))
print("borough mean :{}".format(hh_ter_city))
print("----------------")

## Create a data frame of the findings
household_location_stats_columns = ["household_type", "d_nd", "oacode_total", "ward_total", "borough_total", "borough_mean" ]
household_location_stats_data    = [["commercial", "nd", hh_cb_oa, hh_cb_ward, hh_cb_borough, hh_cb_city],
                                    ["detached", "d", hh_det_oa, hh_det_ward, hh_det_borough, hh_det_city],
                                    ["flat", "d", hh_flt_oa, hh_flt_ward, hh_flt_borough, hh_flt_city],
                                    ["semi-detached", "d", hh_sem_oa, hh_sem_ward, hh_sem_borough, hh_sem_city],
                                    ["terraced", "d", hh_ter_oa, hh_ter_ward, hh_ter_borough, hh_ter_city]]

household_location_stats_df = pd.DataFrame(household_location_stats_data, columns=household_location_stats_columns)

## Remove the non dwelling data i.e. Commercial buildings
## And sort descending
household_location_d_stats_df = household_location_stats_df.loc[household_location_stats_df["d_nd"] == "d"]
household_location_d_stats_df = household_location_d_stats_df.sort_values(by=["oacode_total"], ascending=False)

print(household_location_d_stats_df)