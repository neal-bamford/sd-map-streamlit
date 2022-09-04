import numpy as np
import pyodbc 

def location_search(search_term, data):
    
    search_city      = search_term["city"]
    search_borough   = search_term["borough"]
    search_ward_name = search_term["ward_name"]
    search_post_code = search_term["post_code"]
    
    validated_city   = ""
    validated_borough = ""
    validated_ward_name = ""
    validated_oacode = ""
    validated_post_code = ""
    
    if search_borough == "" and search_ward_name == "" and search_post_code == "":
            raise Exception("Please add some seach terms")
    
    ## Given a Postcode
    if search_post_code != "":
        search_post_code = search_post_code.upper()
        
        try:    
            post_code_results   = data.loc[data["Post_Code"].str.lower() == search_post_code.lower()]
            validated_post_code = post_code_results["Post_Code"].values[0]
            validated_ward_name = post_code_results["WARD_NAME"].values[0]
            validated_oacode    = post_code_results["OAcode"].values[0]
            validated_borough   = post_code_results["borough"].values[0]
            validated_city      = search_city.capitalize()
        except Exception as e:
            ## No match on postcode
            raise Exception(f"Unable to find post code {search_post_code}")

    ## No postcode but ward/borough or both
    else:
        ward_name_borough_unique = data[["WARD_NAME", "borough"]].drop_duplicates()
        ## Ward and Borough
        if search_ward_name != "" and search_borough != "":
            try:    
                ward_name_borough_results = ward_name_borough_unique.loc[(data["WARD_NAME"].str.lower() == search_ward_name.lower()) &
                                                                         (data["borough"].str.lower() == search_borough.lower())]
            except Exception as e:
                ## No match on postcode
                raise Exception(f"Unable to find ward and borough match for {search_ward_name} and {search_borough}")

            ## Non Unique match, shouldn't happen
            if len(ward_name_borough_results) == 0:
                raise Exception(f"Non ward name {search_ward_name} and borough {search_borough} match for city {search_city}.")

            ## Non Unique match, shouldn't happen
            if len(ward_name_borough_results) > 1:
                raise Exception(f"Non unique match for ward {search_ward_name} and borough {search_borough}, returned {ward_name_borough_results}. Add more search terms")
            
            validated_ward_name = ward_name_borough_results["WARD_NAME"].values[0]
            validated_borough   = ward_name_borough_results["borough"].values[0]
            validated_city      = search_city.capitalize()

        ## Ward no Borough
        elif search_ward_name != "" and search_borough == "":
            try:    
                ward_name_borough_results = ward_name_borough_unique.loc[(data["WARD_NAME"].str.lower() == search_ward_name.lower())]
            except Exception as e:
                ## No match on postcode
                raise Exception(f"Unable to find match for ward {search_ward_name}")

            if len(ward_name_borough_results) == 0:
                raise Exception(f"No ward name match for ward name {search_ward_name} .")
                
            ## Non Unique match, shouldn't happen
            if len(ward_name_borough_results) > 1:
                multiple_match = ward_name_borough_results[["WARD_NAME", "borough"]].drop_duplicates()
                multiple_match_list = multiple_match["borough"].tolist()
                raise Exception(f"Non unique ward name match for ward name {search_ward_name}. Add a borough from {multiple_match_list} to the search.")
            
            validated_ward_name = ward_name_borough_results["WARD_NAME"].values[0]
            validated_borough = ward_name_borough_results["borough"].values[0]
            validated_city      = search_city.capitalize()

        ## Borough no Ward
        else:
            try:    
                ward_name_borough_results = ward_name_borough_unique.loc[data["borough"].str.lower() == search_borough.lower()]
            except Exception as e:
                ## No match on borough
                raise Exception(f"Unable to find borough match for {search_borough}")

            ## No match            
            if len(ward_name_borough_results) == 0:
                raise Exception(f"Non borough match for borough {search_borough}.")

            ## Non Unique match, shouldn't happen
            if len(ward_name_borough_results) > 1:
                raise Exception(f"Non unique ward name match for borough {search_borough} add a ward name.")
            
            validated_ward_name = ward_name_borough_results["WARD_NAME"].values[0]
            validated_borough = ward_name_borough_results["borough"].values[0]

    return {"city"      :validated_city
          , "borough"   : validated_borough
          , "ward_name" :validated_ward_name
          , "oacode"    : validated_oacode
          , "post_code" :validated_post_code}
    
def list_post_codes_for_borough_ward_name(search_borough, search_ward_name, data):
    try:
        ret_list = data.loc[(data["borough"].str.lower() == search_borough.lower()) &
                            (data["WARD_NAME"].str.lower() == search_ward_name.lower())]["Post_Code"].to_numpy()
        return ret_list
    except Exception as e:
        raise Exception(f"No post codes found for Borough {search_borough} and Ward Name {search_ward_name}.")
    
    
def list_wards_for_borough(search_borough, data):
    try:
        ret_list = data.loc[(data["borough"].str.lower() == search_borough.lower())]["WARD_NAME"].drop_duplicates().to_numpy()
        return ret_list
    except Exception as e:
        raise Exception(f"No wards found for Borough {search_borough}.")

def list_boroughs_for_city(search_city, data):
    try:
        ret_list = data["borough"].drop_duplicates().to_numpy()
        return ret_list
    except Exception as e:
        raise Exception(f"No boroughs found for city {search_city}.")

def list_lat_long_postcode(search_term, data):
    search_post_code = search_term["post_code"]
    
    latitudes  = data.loc[data["Post_Code"] == search_post_code]["latitude"].to_numpy()
    longitudes = data.loc[data["Post_Code"] == search_post_code]["longitude"].to_numpy()

    combined   = np.column_stack((latitudes, longitudes))
    return combined
    
def list_lat_long_ward_name(search_term, data):    
    search_ward_name = search_term["ward_name"]
    search_borough   = search_term["borough"]
    
    latitudes = data.loc[(data["WARD_NAME"] == search_ward_name) &
                         (data["borough"] == search_borough)]["latitude"].to_numpy()
    longitudes = data.loc[(data["WARD_NAME"] == search_ward_name) &
                          (data["borough"] == search_borough)]["longitude"].to_numpy()
    
    combined   = np.column_stack((latitudes, longitudes))
    return combined

def list_lat_long_borough(search_term, data):
    search_borough = search_term["borough"]    

    latitudes = data.loc[(data["borough"] == search_borough)]["latitude"].to_numpy()
    longitudes = data.loc[(data["borough"] == search_borough)]["longitude"].to_numpy()
    
    combined   = np.column_stack((latitudes, longitudes))
    return combined
    
    
    
    