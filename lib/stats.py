import pandas as pd

def generate_stats(df, borough, ward_name, oacode, column):
    """
    Generate stats from a standardised data frame
    """
    oacode_lvl_sum  = df.loc[df["OAcode"] == oacode][column].values[0]
    
    ward_lvl_sum    = df.loc[(df["WARD_NAME"] == ward_name) \
                           & (df["borough"] == borough)].agg({column: ["sum"]}).values[0][0]
    
    borough_lvl_sum = df.loc[(df["borough"] == borough)].agg({column: ["sum"]}).values[0][0]
    
    city_lvl_mean   = df.groupby("borough").agg({column: ["sum"]}).mean().round(0).values[0].astype(int)
    
    city_lvl_sum    = df.groupby("borough").agg({column: ["sum"]}).sum().round(0).values[0].astype(int)

    return {
     "oacode_sum" : oacode_lvl_sum,
       "ward_sum" : ward_lvl_sum,
    "borough_sum" : borough_lvl_sum,
   "borough_mean" : city_lvl_mean,
       "city_sum" : city_lvl_sum
   }

def generate_rankings(df, borough, column, limit=5):
    """
    Generate ranking at borough level for a return first, last and requested stats
    """
    ## Create a reduced dataframe
    ranking_df = df[["WARD_NAME", "borough", column]]
    ranking_df_stats_ward = ranking_df.groupby(["borough", "WARD_NAME"]).agg(total=pd.NamedAgg(column=column, aggfunc="sum"))

    ## Don't use the column as an index
    ranking_df_stats_borough = ranking_df.groupby(["borough"], as_index=False).agg(total=pd.NamedAgg(column=column, aggfunc="sum"))
    ranking_df_stats_borough["rank"] = ranking_df_stats_borough["total"].rank(method="max", ascending=False)
    ranking_df_stats_borough = ranking_df_stats_borough.sort_values(by=["rank"], ascending=True)

    return ranking_df_stats_borough.head(limit), ranking_df_stats_borough.loc[ranking_df_stats_borough["borough"] == borough], ranking_df_stats_borough.tail(limit)
