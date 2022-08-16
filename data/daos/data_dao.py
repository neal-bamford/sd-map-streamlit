import numpy as np
import logging
import numpy as np
import pandas as pd

# db_conn = db_tools.get_db_conn(properties[properties["database"]["flavour"]] )

log = logging.getLogger(__name__)

###
### CRIME - BOROUGH RANKING
###
def crime_ranked_by_borough_years(db_conn):
  logging.debug("Retrieving Crime Ranked By Borough Years")
  
  crime_ranked_by_borough_years_sql = """
---
--- CRIME - RANKED BY BOROUGH - ALL YEARS
---
WITH SUMMED_CRIME_BOROUGH AS (
  SELECT [LCR].[YEAR]       AS [YEAR], 
         [LCR].[LAD_CODE]   AS [LAD_CODE],
         [LCR].[LAD_NAME]   AS [LAD_NAME],
         SUM([LCR].[COUNT]) AS [BOROUGH_TOTAL_CRIME]
  FROM LONDON_CRIME_LDS            LCR
--  WHERE CONVERT(int,[LCR].[YEAR]) BETWEEN 2001 AND 2022
  GROUP BY [LCR].[YEAR], [LCR].[LAD_CODE], [LCR].[LAD_NAME]
)
SELECT [LCR].[YEAR]                                            AS [YEAR],
       [LCR].[LAD_CODE]                                        AS [LAD_CODE],
       [LCR].[LAD_NAME]                                        AS [LAD_NAME],
       [LCR].[BOROUGH_TOTAL_CRIME]                             AS [BOROUGH_TOTAL_CRIME],
       [LPE].[COUNT]                                           AS [BOROUGH_POPULATION],
       ROUND(([LCR].[BOROUGH_TOTAL_CRIME] / [LPE].[COUNT]), 5) AS [CRIMES_PER_PERSON],
       ROW_NUMBER() OVER(
               PARTITION BY [LCR].[YEAR]                              -- RESET WHEN YEAR CHANGES
               ORDER     BY [LCR].[YEAR] DESC                         -- ORDER BY YEAR DESCENDING
                          , ROUND(([LCR].[BOROUGH_TOTAL_CRIME] / [LPE].[COUNT]), 5) DESC) AS [RANK] -- RANKING COLUMN HIGHEST -> LOWEST
FROM SUMMED_CRIME_BOROUGH        [LCR],
     LONDON_POPULATION_ESTIMATED [LPE]
WHERE [LPE].[YEAR] = [LCR].[YEAR]
AND   [LPE].[LAD] = [LCR].[LAD_CODE]
-- AND   CONVERT(int,[LPE].[YEAR]) BETWEEN 2001 AND 2022
ORDER BY [LPE].[YEAR] DESC, [CRIMES_PER_PERSON] DESC, [LCR].[LAD_NAME] ASC     
"""  

  crime_ranked_by_borough_year_df = pd.read_sql_query(crime_ranked_by_borough_years_sql, db_conn, index_col=None)
  return crime_ranked_by_borough_year_df

###
### EARNINGS - BOROUGH RANKING
###
def earnings_ranked_by_borough_years(db_conn):
  logging.debug("Retrieving Crime Ranked By Borough Years")
  
  earnings_ranked_by_borough_years_sql = """
---
--- INCOME - RANKED BY BOROUGH - ALL YEARS
---
WITH RANKED_EARNINGS_LONDON_ONS  AS (
	SELECT [LEO].[Date]        AS [YEAR]
	     , [LEO].[BOROUGH]     AS [BOROUGH]
	     , [LEO].[MEAN_INCOME] AS [MEAN_INCOME_GBP_BOROUGH]
	     , ROW_NUMBER() OVER(
	     				PARTITION BY [Date] 
	     				ORDER BY [Date] DESC
	     				       , [LEO].[MEAN_INCOME] DESC) AS [RANK]
	FROM LONDON_EARNINGS_ON LEO
)
SELECT [REL].[YEAR]					    AS [YEAR]
     , [REL].[BOROUGH]                  AS [BOROUGH] 
     , [REL].[RANK]					    AS [RANK]
     , [REL].[MEAN_INCOME_GBP_BOROUGH]  AS [MEAN_INCOME_GBP_BOROUGH]
FROM RANKED_EARNINGS_LONDON_ONS REL
ORDER BY [YEAR] DESC, [RANK] ASC
"""
  earnings_ranked_by_borough_year_df = pd.read_sql_query(earnings_ranked_by_borough_years_sql, db_conn, index_col=None)
  return earnings_ranked_by_borough_year_df

###
### ETHNICITY - BOROUGH
###
def ethnicity_ratio_by_borough_years(db_conn):
  logging.debug("ethnicity_ratio_by_borough_years")

  ethnicity_by_borough_year_sql = """
  ---
  --- ETHNICITY - BOROUGH
  ---
  WITH SUMMED_ETHNICITY_BOROUGH AS (
  SELECT [LETH].[YEAR]                                    AS [YEAR],
         [LU_LAD_OA].[LAD]                                AS [LAD],  
         [LU_LAD_OA].[LAD_NAME]                           AS [LAD_NAME],
         [LETH].[OAcode]                                  AS [OA],
         CONVERT(float, [LETH].[All])                     AS [ALL],
         CONVERT(float, [LETH].[White])                   AS [WHITE],
         CONVERT(float, [LETH].[Gypsy_Irish_Traveller])   AS [GYPSY_IRISH_TRAVELLER],
         CONVERT(float, [LETH].[Mixed_ethnic])            AS [MIXED_ETHNIC],
         CONVERT(float, [LETH].[British_Indian])          AS [BRITISH_INDIAN],
         CONVERT(float, [LETH].[British_Pakistani])       AS [BRITISH_PAKISTANI],
         CONVERT(float, [LETH].[British_Bangladeshi])     AS [BRITISH_BANGLADESHI],
         CONVERT(float, [LETH].[British_Chinese])         AS [BRITISH_CHINESE],
         CONVERT(float, [LETH].[British_Other_Asian])     AS [BRITISH_OTHER_ASIAN],
         CONVERT(float, [LETH].[Black_African_Caribbean]) AS [BLACK_AFRICAN_CARIBBEAN],
         CONVERT(float, [LETH].[Other_Ethnic])            AS [OTHER_ETHNIC]
  FROM [LondonEthnicity] [LETH], 
        LOOKUP_LAD_OA [LU_LAD_OA]
  WHERE [LETH].[OAcode] = [LU_LAD_OA].[OA]
  ) 
  SELECT [SEB].[YEAR]                                          AS [YEAR],
         [SEB].[LAD]                                           AS [LAD],
         [SEB].[LAD_NAME]                                      AS [LAD_NAME],
         SUM([SEB].[WHITE])/SUM([SEB].[ALL])                   AS [White],
         SUM([SEB].[GYPSY_IRISH_TRAVELLER])/SUM([SEB].[ALL])   AS [Gypsy Irish Traveller],
         SUM([SEB].[MIXED_ETHNIC])/SUM([SEB].[ALL])            AS [Mixed Ethnic],
         SUM([SEB].[BRITISH_INDIAN])/SUM([SEB].[ALL])          AS [British Indian],
         SUM([SEB].[BRITISH_PAKISTANI])/SUM([SEB].[ALL])       AS [British Pakistani],
         SUM([SEB].[BRITISH_BANGLADESHI])/SUM([SEB].[ALL])     AS [British Bangladeshi],
         SUM([SEB].[BRITISH_CHINESE])/SUM([SEB].[ALL])         AS [British Chinese],
         SUM([SEB].[BRITISH_OTHER_ASIAN])/SUM([SEB].[ALL])     AS [British Asian Other],
         SUM([SEB].[BLACK_AFRICAN_CARIBBEAN])/SUM([SEB].[ALL]) AS [Black African Caribbean],
         SUM([SEB].[OTHER_ETHNIC])/SUM([SEB].[ALL])            AS [Other]
  FROM [SUMMED_ETHNICITY_BOROUGH] AS [SEB]
  GROUP BY [YEAR], [LAD], [LAD_NAME]
  ORDER BY [YEAR] DESC, [LAD_NAME] ASC
  """
  
  ethncitiy_ratio_by_borough_year_df = pd.read_sql_query(ethnicity_by_borough_year_sql, db_conn, index_col=None)
  return ethncitiy_ratio_by_borough_year_df

###
### ETHNICITY - BOROUGH/WARD
###
def ethnicity_ratio_by_borough_ward_years(db_conn, search_term):
  logging.debug("ethnicity_ratio_by_borough_ward_years")

  borough = search_term["borough"]
  ward_name = search_term["ward_name"]
  
  ethnicity_by_borough_ward_year_sql = """
  ---
  --- ETHNICITY - BOROUGH/WARD
  ---
  WITH SUMMED_ETHNICITY_WARD AS (
  SELECT [LETH].[YEAR]                                    AS [YEAR],
         [LU_LAD_OA].[LAD]                                AS [LAD],  
         [LU_LAD_OA].[LAD_NAME]                           AS [LAD_NAME],
         [LU_WARD_OA].[WARD_CODE]                         AS [WARD_CODE],
         [LU_WARD_OA].[WARD_NAME]                         AS [WARD_NAME],
         [LETH].[OAcode]                                  AS [OA],
         CONVERT(float, [LETH].[All])                     AS [ALL],
         CONVERT(float, [LETH].[White])                   AS [WHITE],
         CONVERT(float, [LETH].[Gypsy_Irish_Traveller])   AS [GYPSY_IRISH_TRAVELLER],
         CONVERT(float, [LETH].[Mixed_ethnic])            AS [MIXED_ETHNIC],
         CONVERT(float, [LETH].[British_Indian])          AS [BRITISH_INDIAN],
         CONVERT(float, [LETH].[British_Pakistani])       AS [BRITISH_PAKISTANI],
         CONVERT(float, [LETH].[British_Bangladeshi])     AS [BRITISH_BANGLADESHI],
         CONVERT(float, [LETH].[British_Chinese])         AS [BRITISH_CHINESE],
         CONVERT(float, [LETH].[British_Other_Asian])     AS [BRITISH_OTHER_ASIAN],
         CONVERT(float, [LETH].[Black_African_Caribbean]) AS [BLACK_AFRICAN_CARIBBEAN],
         CONVERT(float, [LETH].[Other_Ethnic])            AS [OTHER_ETHNIC]
  FROM  [LondonEthnicity]                                 AS [LETH], 
        [LOOKUP_LAD_OA]                                   AS [LU_LAD_OA],
        [LOOKUP_WARD_CODE_OA]                             AS [LU_WARD_OA]
  WHERE [LETH].[OAcode] = [LU_LAD_OA].[OA]
  AND   [LU_LAD_OA].[OA] = [LU_WARD_OA].[OA]
  )
  SELECT [SEW].[YEAR]                                          AS [YEAR],
         [SEW].[LAD]                                           AS [LAD],
         [SEW].[LAD_NAME]                                      AS [LAD_NAME],
         [SEW].[WARD_CODE]                                     AS [WARD_CODE],
         [SEW].[WARD_NAME]                                     AS [WARD_NAME],
         SUM([SEW].[WHITE])/SUM([SEW].[ALL])                   AS [White],
         SUM([SEW].[GYPSY_IRISH_TRAVELLER])/SUM([SEW].[ALL])   AS [Gypsy Irish Traveller],
         SUM([SEW].[MIXED_ETHNIC])/SUM([SEW].[ALL])            AS [Mixed Ethnic],
         SUM([SEW].[BRITISH_INDIAN])/SUM([SEW].[ALL])          AS [British Indian],
         SUM([SEW].[BRITISH_PAKISTANI])/SUM([SEW].[ALL])       AS [British Pakistani],
         SUM([SEW].[BRITISH_BANGLADESHI])/SUM([SEW].[ALL])     AS [British Bangladeshi],
         SUM([SEW].[BRITISH_CHINESE])/SUM([SEW].[ALL])         AS [British Chinese],
         SUM([SEW].[BRITISH_OTHER_ASIAN])/SUM([SEW].[ALL])     AS [British Asian Other],
         SUM([SEW].[BLACK_AFRICAN_CARIBBEAN])/SUM([SEW].[ALL]) AS [Black African Caribbean],
         SUM([SEW].[OTHER_ETHNIC])/SUM([SEW].[ALL])            AS [Other]
  FROM [SUMMED_ETHNICITY_WARD] AS [SEW]
  WHERE  [LAD_NAME] = '{}' AND [WARD_NAME] = '{}' 
  GROUP BY [YEAR], [LAD], [LAD_NAME], [WARD_CODE], [WARD_NAME]
  ORDER BY [YEAR] DESC, [LAD_NAME] ASC
""".format(borough, ward_name)
  
  ethncitiy_ratio_by_borough_ward_year_df = pd.read_sql_query(ethnicity_by_borough_ward_year_sql, db_conn, index_col=None)
  return ethncitiy_ratio_by_borough_ward_year_df

### 
### ETHNICITY - AVERAGE
###
def ethnicity_ratio_average_years(db_conn):
  logging.debug("ethnicity_ratio_average_years")

  ethnicity_ratio_average_years_sql = """
  ---
  --- ETHNICITY AVERAGE
  ---
  WITH SUMMED_ETHNICITY_WARD AS 
  (
      SELECT [LETH].[YEAR]                                    AS [YEAR],
             [LU_LAD_OA].[LAD]                                AS [LAD],  
             [LU_LAD_OA].[LAD_NAME]                           AS [LAD_NAME],
             [LU_WARD_OA].[WARD_CODE]                         AS [WARD_CODE],
             [LU_WARD_OA].[WARD_NAME]                         AS [WARD_NAME],
             [LETH].[OAcode]                                  AS [OA],
             CONVERT(float, [LETH].[All])                     AS [ALL],
             CONVERT(float, [LETH].[White])                   AS [WHITE],
             CONVERT(float, [LETH].[Gypsy_Irish_Traveller])   AS [GYPSY_IRISH_TRAVELLER],
             CONVERT(float, [LETH].[Mixed_ethnic])            AS [MIXED_ETHNIC],
             CONVERT(float, [LETH].[British_Indian])          AS [BRITISH_INDIAN],
             CONVERT(float, [LETH].[British_Pakistani])       AS [BRITISH_PAKISTANI],
             CONVERT(float, [LETH].[British_Bangladeshi])     AS [BRITISH_BANGLADESHI],
             CONVERT(float, [LETH].[British_Chinese])         AS [BRITISH_CHINESE],
             CONVERT(float, [LETH].[British_Other_Asian])     AS [BRITISH_OTHER_ASIAN],
             CONVERT(float, [LETH].[Black_African_Caribbean]) AS [BLACK_AFRICAN_CARIBBEAN],
             CONVERT(float, [LETH].[Other_Ethnic])            AS [OTHER_ETHNIC]
      FROM  [LondonEthnicity]                                 AS [LETH], 
            [LOOKUP_LAD_OA]                                   AS [LU_LAD_OA],
            [LOOKUP_WARD_CODE_OA]                             AS [LU_WARD_OA]
      WHERE [LETH].[OAcode] = [LU_LAD_OA].[OA]
      AND   [LU_LAD_OA].[OA] = [LU_WARD_OA].[OA]
  ), 
  GROUPED_ETHNICITY_WARD AS
  (
      SELECT [SEW].[YEAR]                                          AS [YEAR],
             [SEW].[LAD]                                           AS [LAD],
             [SEW].[LAD_NAME]                                      AS [LAD_NAME],
             [SEW].[WARD_CODE]                                     AS [WARD_CODE],
             [SEW].[WARD_NAME]                                     AS [WARD_NAME],
             SUM([SEW].[WHITE])/SUM([SEW].[ALL])                   AS [WHITE_RATIO_BOROUGH],
             SUM([SEW].[GYPSY_IRISH_TRAVELLER])/SUM([SEW].[ALL])   AS [GYPSY_IRISH_TRAVELLER_RATIO_BOROUGH],
             SUM([SEW].[MIXED_ETHNIC])/SUM([SEW].[ALL])            AS [MIXED_ETHNIC_RATIO_BOROUGH],
             SUM([SEW].[BRITISH_INDIAN])/SUM([SEW].[ALL])          AS [BRITISH_INDIAN_RATIO_BOROUGH],
             SUM([SEW].[BRITISH_PAKISTANI])/SUM([SEW].[ALL])       AS [BRITISH_PAKISTANI_RATIO_BOROUGH],
             SUM([SEW].[BRITISH_BANGLADESHI])/SUM([SEW].[ALL])     AS [BRITISH_BANGLADESHI_RATIO_BOROUGH],
             SUM([SEW].[BRITISH_CHINESE])/SUM([SEW].[ALL])         AS [BRITISH_CHINESE_RATIO_BOROUGH],
             SUM([SEW].[BRITISH_OTHER_ASIAN])/SUM([SEW].[ALL])     AS [BRITISH_OTHER_ASIAN_RATIO_BOROUGH],
             SUM([SEW].[BLACK_AFRICAN_CARIBBEAN])/SUM([SEW].[ALL]) AS [BLACK_AFRICAN_CARIBBEAN_RATIO_BOROUGH],
             SUM([SEW].[OTHER_ETHNIC])/SUM([SEW].[ALL])            AS [OTHER_ETHNIC_BOROUGH]
      FROM [SUMMED_ETHNICITY_WARD] AS [SEW]
      GROUP BY [SEW].[YEAR],
               [SEW].[LAD], 
               [SEW].[LAD_NAME], 
               [SEW].[WARD_CODE], 
               [SEW].[WARD_NAME]
  )
  SELECT [GEW].[YEAR]                                              AS [YEAR],
         AVG([GEW].[WHITE_RATIO_BOROUGH])                          AS [White],
         AVG([GEW].[GYPSY_IRISH_TRAVELLER_RATIO_BOROUGH])          AS [Gypsy Irish Traveller],
         AVG([GEW].[MIXED_ETHNIC_RATIO_BOROUGH])                   AS [Mixed Ethnic],
         AVG([GEW].[BRITISH_INDIAN_RATIO_BOROUGH])                 AS [British Indian],
         AVG([GEW].[BRITISH_PAKISTANI_RATIO_BOROUGH])              AS [British Pakistani],
         AVG([GEW].[BRITISH_BANGLADESHI_RATIO_BOROUGH])            AS [British Bangladeshi],
         AVG([GEW].[BRITISH_CHINESE_RATIO_BOROUGH])                AS [British Chinese],
         AVG([GEW].[BRITISH_OTHER_ASIAN_RATIO_BOROUGH])            AS [British Asian Other],
         AVG([GEW].[BLACK_AFRICAN_CARIBBEAN_RATIO_BOROUGH])        AS [Black African Caribbean],
         AVG([GEW].[OTHER_ETHNIC_BOROUGH])                         AS [Other]
  FROM [GROUPED_ETHNICITY_WARD]                                    AS [GEW]
  GROUP BY [GEW].[YEAR]
  ORDER BY [GEW].[YEAR] DESC;
"""
  
  ethnicity_ratio_average_years_df = pd.read_sql_query(ethnicity_ratio_average_years_sql, db_conn, index_col=None)
  return ethnicity_ratio_average_years_df

###
### EDUCATION - BOROUGH
###
def education_ratio_by_borough_years(db_conn):
  logging.debug("education_ratio_by_borough_years")

  education_by_borough_year_sql = """
  ---
  --- EDUCATION - BOROUGH
  ---
  WITH SUMMED_EDUCATION_BOROUGH AS (
  SELECT [LQUAL].[Date]                                          AS [YEAR],
         [LU_LAD_OA].[LAD]                                       AS [LAD],  
         [LU_LAD_OA].[LAD_NAME]                                  AS [LAD_NAME],
         [LQUAL].[OAcode]                                        AS [OA],
	     CONVERT(float, [LQUAL].[All])                           AS [All],
	     CONVERT(float, [LQUAL].[NoQualification])               AS [NoQualification],
	     CONVERT(float, [LQUAL].[Level1])                        AS [Level1],
	     CONVERT(float, [LQUAL].[Level2])                        AS [Level2],
	     CONVERT(float, [LQUAL].[Level3])                        AS [Level3],
	     CONVERT(float, [LQUAL].[Level4])                        AS [Level4],
	     CONVERT(float, [LQUAL].[OtherQualifications])           AS [OtherQualifications],
	     CONVERT(float, [LQUAL].[Apprenticeship])                AS [Apprenticeship],
	     CONVERT(float, [LQUAL].[FTStudents16-17])               AS [FTStudents16-17],
	     CONVERT(float, [LQUAL].[FTStudents18above])             AS [FTStudents18above],
	     CONVERT(float, [LQUAL].[FTStudents18aboveinEmp])        AS [FTStudents18aboveinEmp],
	     CONVERT(float, [LQUAL].[FTStudents18aboveinUnemp])      AS [FTStudents18aboveinUnemp],
	     CONVERT(float, [LQUAL].[FTStudents18aboveinECinactive]) AS [FTStudents18aboveinECinactive]
  FROM [LondonQualification] 							         AS [LQUAL],
        LOOKUP_LAD_OA [LU_LAD_OA]
  WHERE [LQUAL].[OAcode] = [LU_LAD_OA].[OA]
  ) 
  SELECT [SEB].[YEAR]                                           AS [YEAR],
         [SEB].[LAD]                                            AS [LAD],
         [SEB].[LAD_NAME]                                       AS [LAD_NAME],
         SUM([SEB].[NoQualification])         /SUM([SEB].[All]) AS [None],
         SUM([SEB].[Level1])                  /SUM([SEB].[All]) AS [Level 1],
         SUM([SEB].[Level2])                  /SUM([SEB].[All]) AS [Level 2],
         SUM([SEB].[Level3])                  /SUM([SEB].[All]) AS [Level 3], 
         SUM([SEB].[Level4])                  /SUM([SEB].[All]) AS [Level 4],
         SUM([SEB].[OtherQualifications])     /SUM([SEB].[All]) AS [Other],
         SUM([SEB].[Apprenticeship])          /SUM([SEB].[All]) AS [Apprenticeship],
         SUM([SEB].[FTStudents16-17])         /SUM([SEB].[All]) AS [FT Student 16 17],
         SUM([SEB].[FTStudents18above])       /SUM([SEB].[All]) AS [FT Student 18+],
         SUM([SEB].[FTStudents18aboveinEmp])  /SUM([SEB].[All]) AS [FT Student 18+ Employed],	
         SUM([SEB].[FTStudents18aboveinUnemp])/SUM([SEB].[All]) AS [FT Student 18+ Unemployed]
  FROM [SUMMED_EDUCATION_BOROUGH] AS [SEB]
  GROUP BY [SEB].[YEAR],
           [SEB].[LAD], 
           [SEB].[LAD_NAME]
  ORDER BY [YEAR] DESC, [LAD_NAME] ASC
"""
  
  education_ratio_by_borough_year_df = pd.read_sql_query(education_by_borough_year_sql, db_conn, index_col=None)
  return education_ratio_by_borough_year_df

###
### EDUCATION - BOROUGH/WARD
###
def education_ratio_by_borough_ward_years(db_conn, search_term):
  logging.debug("education_ratio_by_borough_ward_years")

  borough = search_term["borough"]
  ward_name = search_term["ward_name"]
  
  education_by_borough_ward_year_sql = """
  ---
  --- EDUCATION - BOROUGH/WARD
  ---
  WITH BOROUGH_EDUCATION_CONVERTED AS(
  SELECT [LQUAL].[date]				                             AS [YEAR],
         [LU_LAD_OA].[LAD]                                       AS [LAD],  
         [LU_LAD_OA].[LAD_NAME]                                  AS [LAD_NAME],
         [LU_WARD_OA].[WARD_CODE]							     AS [WARD_CODE],
         [LU_WARD_OA].[WARD_NAME]							     AS [WARD_NAME],
         [LQUAL].[OAcode]				                         AS [OA],
         CONVERT(float, [LQUAL].[All])                           AS [All],
         CONVERT(float, [LQUAL].[NoQualification])               AS [NoQualification],
         CONVERT(float, [LQUAL].[Level1])                        AS [Level1],
         CONVERT(float, [LQUAL].[Level2])                        AS [Level2],
         CONVERT(float, [LQUAL].[Level3])                        AS [Level3],
         CONVERT(float, [LQUAL].[Level4])                        AS [Level4],
         CONVERT(float, [LQUAL].[OtherQualifications])           AS [OtherQualifications],
         CONVERT(float, [LQUAL].[Apprenticeship])                AS [Apprenticeship],
         CONVERT(float, [LQUAL].[FTStudents16-17])               AS [FTStudents16-17],
         CONVERT(float, [LQUAL].[FTStudents18above])             AS [FTStudents18above],
         CONVERT(float, [LQUAL].[FTStudents18aboveinEmp])        AS [FTStudents18aboveinEmp],
         CONVERT(float, [LQUAL].[FTStudents18aboveinUnemp])      AS [FTStudents18aboveinUnemp],
         CONVERT(float, [LQUAL].[FTStudents18aboveinECinactive]) AS [FTStudents18aboveinECinactive]
  FROM  [LondonQualification] 							         AS [LQUAL],
        [LOOKUP_LAD_OA]                                          AS [LU_LAD_OA],
        [LOOKUP_WARD_CODE_OA]                                    AS [LU_WARD_OA]
  WHERE [LQUAL].[OAcode]  = [LU_LAD_OA].[OA]
  AND   [LU_LAD_OA].[OA] = [LU_WARD_OA].[OA]
  ),
  BOROUGH_EDUCATION_RATIO AS(
      SELECT [BEC].[YEAR],
             [BEC].[LAD]                                                     AS [LAD],  
             [BEC].[LAD_NAME]                                                AS [LAD_NAME],
             [BEC].[WARD_CODE]							                     AS [WARD_CODE],
             [BEC].[WARD_NAME]							                     AS [WARD_NAME],
             SUM([BEC].[NoQualification])         /SUM([BEC].[All])          AS [NO_QUALIFICATION_RATIO],
             SUM([BEC].[Level1])                  /SUM([BEC].[All])          AS [LEVEL1_RATIO],	
             SUM([BEC].[Level2])                  /SUM([BEC].[All])          AS [LEVEL2_RATIO],
             SUM([BEC].[Level3])                  /SUM([BEC].[All])          AS [LEVEL3_RATIO],
             SUM([BEC].[Level4])                  /SUM([BEC].[All])          AS [LEVEL4_RATIO],
             SUM([BEC].[OtherQualifications])     /SUM([BEC].[All])          AS [OTHER_QUALIFICATIONS_RATIO],
             SUM([BEC].[Apprenticeship])          /SUM([BEC].[All])          AS [APPRENTICESHIP_RATIO],
             SUM([BEC].[FTStudents16-17])         /SUM([BEC].[All])          AS [FTSTUDENTS16_17_RATIO],
             SUM([BEC].[FTStudents18above])       /SUM([BEC].[All])          AS [FT_STUDENTS_18_ABOVE_RATIO],
             SUM([BEC].[FTStudents18aboveinEmp])  /SUM([BEC].[All])          AS [FT_STUDENTS_18_ABOVE_IN_EMP_RATIO],	
             SUM([BEC].[FTStudents18aboveinUnemp])/SUM([BEC].[All])          AS [FT_STUDENTS_18_ABOVE_IN_UNEMP_RATIO]
      FROM [BOROUGH_EDUCATION_CONVERTED] AS [BEC]
      GROUP BY [BEC].[YEAR], 
               [BEC].[LAD], 
               [BEC].[LAD_NAME], 
               [BEC].[WARD_CODE], 
               [BEC].[WARD_NAME]
  )
  SELECT [BER].[YEAR]                                AS [YEAR],
         [BER].[LAD]                                 AS [LAD],
         [BER].[LAD_NAME]                            AS [LAD_NAME],
         [BER].[WARD_CODE]                           AS [WARD_CODE],
         [BER].[WARD_NAME]                           AS [WARD_NAME],
         [BER].[NO_QUALIFICATION_RATIO]              AS [None],
         [BER].[LEVEL1_RATIO]                        AS [Level 1],
         [BER].[LEVEL2_RATIO]                        AS [Level 2],
         [BER].[LEVEL3_RATIO]                        AS [Level 3], 
         [BER].[LEVEL4_RATIO]                        AS [Level 4],
         [BER].[OTHER_QUALIFICATIONS_RATIO]          AS [Other],
         [BER].[APPRENTICESHIP_RATIO]                AS [Apprenticeship],
         [BER].[FTSTUDENTS16_17_RATIO]               AS [FT Student 16 17],
         [BER].[FT_STUDENTS_18_ABOVE_RATIO]          AS [FT Student 18+],
         [BER].[FT_STUDENTS_18_ABOVE_IN_EMP_RATIO]   AS [FT Student 18+ Employed],	
         [BER].[FT_STUDENTS_18_ABOVE_IN_UNEMP_RATIO] AS [FT Student 18+ Unemployed]
  FROM [BOROUGH_EDUCATION_RATIO] AS [BER]
  WHERE  [LAD_NAME] = '{}' AND [WARD_NAME] = '{}' 
  ORDER BY [BER].[YEAR],
           [BER].[LAD_NAME], 
           [BER].[WARD_NAME]
""".format(borough, ward_name)
  
  education_ratio_by_borough_ward_year_df = pd.read_sql_query(education_by_borough_ward_year_sql, db_conn, index_col=None)
  return education_ratio_by_borough_ward_year_df

### 
### EDUCATION - AVERAGE
###
def education_ratio_average_years(db_conn):
  logging.debug("education_ratio_average_years")

  education_ratio_average_years_sql = """
  ---
  --- EDUCATION - AVERAGE
  ---
  WITH SUMMED_EDUCATION_WARD AS 
  (
      SELECT [LQUAL].[Date]                                          AS [YEAR],
             [LU_LAD_OA].[LAD]                                       AS [LAD],  
             [LU_LAD_OA].[LAD_NAME]                                  AS [LAD_NAME],
             [LU_WARD_OA].[WARD_CODE]                                AS [WARD_CODE],
             [LU_WARD_OA].[WARD_NAME]                                AS [WARD_NAME],
             [LQUAL].[OAcode]                                        AS [OA],
	         CONVERT(float, [LQUAL].[All])                           AS [All],
	         CONVERT(float, [LQUAL].[NoQualification])               AS [NoQualification],
	         CONVERT(float, [LQUAL].[Level1])                        AS [Level1],
	         CONVERT(float, [LQUAL].[Level2])                        AS [Level2],
	         CONVERT(float, [LQUAL].[Level3])                        AS [Level3],
	         CONVERT(float, [LQUAL].[Level4])                        AS [Level4],
	         CONVERT(float, [LQUAL].[OtherQualifications])           AS [OtherQualifications],
	         CONVERT(float, [LQUAL].[Apprenticeship])                AS [Apprenticeship],
	         CONVERT(float, [LQUAL].[FTStudents16-17])               AS [FTStudents16-17],
	         CONVERT(float, [LQUAL].[FTStudents18above])             AS [FTStudents18above],
	         CONVERT(float, [LQUAL].[FTStudents18aboveinEmp])        AS [FTStudents18aboveinEmp],
	         CONVERT(float, [LQUAL].[FTStudents18aboveinUnemp])      AS [FTStudents18aboveinUnemp],
	         CONVERT(float, [LQUAL].[FTStudents18aboveinECinactive]) AS [FTStudents18aboveinECinactive]
		FROM [LondonQualification] 							         AS [LQUAL],
             [LOOKUP_LAD_OA]                                         AS [LU_LAD_OA],
             [LOOKUP_WARD_CODE_OA]                                   AS [LU_WARD_OA]
      WHERE [LQUAL].[OAcode] = [LU_LAD_OA].[OA]
      AND   [LU_LAD_OA].[OA] = [LU_WARD_OA].[OA]
  ), 
  GROUPED_EDUCATION_WARD AS
  (
      SELECT [SEW].[YEAR]                                           AS [YEAR],
             [SEW].[LAD]                                            AS [LAD],
             [SEW].[LAD_NAME]                                       AS [LAD_NAME],
             [SEW].[WARD_CODE]                                      AS [WARD_CODE],
             [SEW].[WARD_NAME]                                      AS [WARD_NAME],
             SUM([SEW].[NoQualification])         /SUM([SEW].[All]) AS [NO_QUALIFICATION_RATIO],
             SUM([SEW].[Level1])                  /SUM([SEW].[All]) AS [LEVEL1_RATIO],	
             SUM([SEW].[Level2])                  /SUM([SEW].[All]) AS [LEVEL2_RATIO],
             SUM([SEW].[Level3])                  /SUM([SEW].[All]) AS [LEVEL3_RATIO],
             SUM([SEW].[Level4])                  /SUM([SEW].[All]) AS [LEVEL4_RATIO],
             SUM([SEW].[OtherQualifications])     /SUM([SEW].[All]) AS [OTHER_QUALIFICATIONS_RATIO],
             SUM([SEW].[Apprenticeship])          /SUM([SEW].[All]) AS [APPRENTICESHIP_RATIO],
             SUM([SEW].[FTStudents16-17])         /SUM([SEW].[All]) AS [FTSTUDENTS16_17_RATIO],
             SUM([SEW].[FTStudents18above])       /SUM([SEW].[All]) AS [FT_STUDENTS_18_ABOVE_RATIO],
             SUM([SEW].[FTStudents18aboveinEmp])  /SUM([SEW].[All]) AS [FT_STUDENTS_18_ABOVE_IN_EMP_RATIO],	
             SUM([SEW].[FTStudents18aboveinUnemp])/SUM([SEW].[All]) AS [FT_STUDENTS_18_ABOVE_IN_UNEMP_RATIO]
      FROM [SUMMED_EDUCATION_WARD] AS [SEW]
      GROUP BY [SEW].[YEAR],
               [SEW].[LAD], 
               [SEW].[LAD_NAME], 
               [SEW].[WARD_CODE], 
               [SEW].[WARD_NAME]
  )
  SELECT [GEW].[YEAR]                                     AS [YEAR],
         AVG([GEW].[NO_QUALIFICATION_RATIO])              AS [None],
         AVG([GEW].[LEVEL1_RATIO])                        AS [Level 1],
         AVG([GEW].[LEVEL2_RATIO])                        AS [Level 2],
         AVG([GEW].[LEVEL3_RATIO])                        AS [Level 3], 
         AVG([GEW].[LEVEL4_RATIO])                        AS [Level 4],
         AVG([GEW].[OTHER_QUALIFICATIONS_RATIO])          AS [Other],
         AVG([GEW].[APPRENTICESHIP_RATIO])                AS [Apprenticeship],
         AVG([GEW].[FTSTUDENTS16_17_RATIO])               AS [FT Student 16 17],
         AVG([GEW].[FT_STUDENTS_18_ABOVE_RATIO])          AS [FT Student 18+],
         AVG([GEW].[FT_STUDENTS_18_ABOVE_IN_EMP_RATIO])   AS [FT Student 18+ Employed],	
         AVG([GEW].[FT_STUDENTS_18_ABOVE_IN_UNEMP_RATIO]) AS [FT Student 18+ Unemployed]
  FROM [GROUPED_EDUCATION_WARD]                           AS [GEW]
  GROUP BY [GEW].[YEAR]
  ORDER BY [GEW].[YEAR] DESC;         
"""
  
  education_ratio_average_years_df = pd.read_sql_query(education_ratio_average_years_sql, db_conn, index_col=None)
  return education_ratio_average_years_df


###
### GENERAL_HEALTH - BOROUGH
###
def general_health_ratio_by_borough_years(db_conn):
  logging.debug("genearl_health_ratio_by_borough_years")

  general_health_by_borough_year_sql = """
  ---
  --- GENERAL_HEALTH - BOROUGH
  ---
 WITH SUMMED_GENERAL_HEALTH_BOROUGH AS (
  SELECT [LGENH].[Date]                                          AS [Date],
       CAST(Year([LGENH].[Date]) AS int)              AS [Year],
         [LU_LAD_OA].[LAD]                                       AS [LAD],  
         [LU_LAD_OA].[LAD_NAME]                                  AS [LAD_NAME],
         [LGENH].[OAcode]                                        AS [OA],
       CONVERT(float, [LGENH].[levcel1]) + 
       CONVERT(float, [LGENH].[levcel2]) + 
       CONVERT(float, [LGENH].[levcel3]) + 
       CONVERT(float, [LGENH].[levcel4]) + 
       CONVERT(float, [LGENH].[levcel5]) + 
       CONVERT(float, [LGENH].[levcel6])                       AS [All], 
       CONVERT(float, [LGENH].[levcel1])                       AS [Level_1],
       CONVERT(float, [LGENH].[levcel2])                       AS [Level_2],
       CONVERT(float, [LGENH].[levcel3])                       AS [Level_3],
       CONVERT(float, [LGENH].[levcel4])                       AS [Level_4],
       CONVERT(float, [LGENH].[levcel5])                       AS [Level_5],
       CONVERT(float, [LGENH].[levcel6])                       AS [Level_6]
  FROM [LondonGeneralhealth]                        AS [LGENH],
        LOOKUP_LAD_OA [LU_LAD_OA]
  WHERE [LGENH].[OAcode] = [LU_LAD_OA].[OA]
  ) 
  SELECT [SGHB].[YEAR]                                           AS [YEAR],
         [SGHB].[LAD]                                            AS [LAD],
         [SGHB].[LAD_NAME]                                       AS [LAD_NAME],
         ROUND(SUM([SGHB].[Level_1]) /SUM([SGHB].[All]),4)     AS [Level 1],
         ROUND(SUM([SGHB].[Level_2]) /SUM([SGHB].[All]),4)     AS [Level 2],
         ROUND(SUM([SGHB].[Level_3]) /SUM([SGHB].[All]),4)     AS [Level 3],
         ROUND(SUM([SGHB].[Level_4]) /SUM([SGHB].[All]),4)     AS [Level 4],
         ROUND(SUM([SGHB].[Level_5]) /SUM([SGHB].[All]),4)     AS [Level 5],
         ROUND(SUM([SGHB].[Level_6]) /SUM([SGHB].[All]),4)     AS [Level 6]
  FROM [SUMMED_GENERAL_HEALTH_BOROUGH] AS [SGHB]
  GROUP BY [SGHB].[YEAR],
           [SGHB].[LAD], 
           [SGHB].[LAD_NAME]
  ORDER BY [YEAR] DESC, [LAD_NAME] ASC
  """
  
  general_health_ratio_by_borough_year_df = pd.read_sql_query(general_health_by_borough_year_sql, db_conn, index_col=None)
  return general_health_ratio_by_borough_year_df

###
### GENERAL_HEALTH - BOROUGH/WARD
###
def general_health_ratio_by_borough_ward_years(db_conn, search_term):
  logging.debug("general_health_ratio_by_borough_ward_years")

  borough = search_term["borough"]
  ward_name = search_term["ward_name"]
  
  general_health_by_borough_ward_year_sql = """
  ---
  --- GENERAL_HEALTH - BOROUGH/WARD
  ---
  WITH SUMMED_GENERAL_HEALTH_BOROUGH AS (
  SELECT [LGENH].[Date]                                          AS [Date],
       CAST(Year([LGENH].[Date]) AS int)              AS [Year],
         [LU_LAD_OA].[LAD]                                       AS [LAD],  
         [LU_LAD_OA].[LAD_NAME]                                  AS [LAD_NAME],
         [LU_WARD_OA].[WARD_CODE]                                AS [WARD_CODE],
         [LU_WARD_OA].[WARD_NAME]                                AS [WARD_NAME],
         [LGENH].[OAcode]                                        AS [OA],
       CONVERT(float, [LGENH].[levcel1]) + 
       CONVERT(float, [LGENH].[levcel2]) + 
       CONVERT(float, [LGENH].[levcel3]) + 
       CONVERT(float, [LGENH].[levcel4]) + 
       CONVERT(float, [LGENH].[levcel5]) + 
       CONVERT(float, [LGENH].[levcel6])                       AS [All], 
       CONVERT(float, [LGENH].[levcel1])                       AS [Level_1],
       CONVERT(float, [LGENH].[levcel2])                       AS [Level_2],
       CONVERT(float, [LGENH].[levcel3])                       AS [Level_3],
       CONVERT(float, [LGENH].[levcel4])                       AS [Level_4],
       CONVERT(float, [LGENH].[levcel5])                       AS [Level_5],
       CONVERT(float, [LGENH].[levcel6])                       AS [Level_6]
  FROM [LondonGeneralhealth]                        AS [LGENH],
        [LOOKUP_LAD_OA]                                          AS [LU_LAD_OA],
        [LOOKUP_WARD_CODE_OA]                                    AS [LU_WARD_OA]
  WHERE [LGENH].[OAcode] = [LU_LAD_OA].[OA]
  AND   [LU_LAD_OA].[OA] = [LU_WARD_OA].[OA]
  ) 
  SELECT [SGHB].[YEAR]                                           AS [YEAR],
         [SGHB].[LAD]                                            AS [LAD],
         [SGHB].[LAD_NAME]                                       AS [LAD_NAME],
         [SGHB].[WARD_CODE]                                      AS [WARD_CODE],
         [SGHB].[WARD_NAME]                                      AS [WARD_NAME],
         SUM([SGHB].[Level_1]) /SUM([SGHB].[All])              AS [Level 1],
         SUM([SGHB].[Level_2]) /SUM([SGHB].[All])              AS [Level 2],
         SUM([SGHB].[Level_3]) /SUM([SGHB].[All])              AS [Level 3],
         SUM([SGHB].[Level_4]) /SUM([SGHB].[All])              AS [Level 4],
         SUM([SGHB].[Level_5]) /SUM([SGHB].[All])              AS [Level 5],
         SUM([SGHB].[Level_6]) /SUM([SGHB].[All])              AS [Level 6]
  FROM [SUMMED_GENERAL_HEALTH_BOROUGH] AS [SGHB]
  WHERE  [LAD_NAME] = '{}' AND [WARD_NAME] = '{}' 
  GROUP BY [YEAR], [LAD], [LAD_NAME], [WARD_CODE], [WARD_NAME]
  ORDER BY [YEAR] DESC, [LAD_NAME] ASC
""".format(borough, ward_name)

  general_health_ratio_by_borough_ward_year_df = pd.read_sql_query(general_health_by_borough_ward_year_sql, db_conn, index_col=None)
  return general_health_ratio_by_borough_ward_year_df

### 
### GENERAL_HEALTH - AVERAGE
###
def general_health_ratio_average_years(db_conn):
  logging.debug("general_health_ratio_average_years")

  general_health_ratio_average_years_sql = """
  ---
  --- GENERAL_HEALTH AVERAGE
  ---
  ---
  --- GENERAL_HEALTH - BOROUGH/WARD
  ---
  WITH SUMMED_GENERAL_HEALTH_BOROUGH AS (
  SELECT [LGENH].[Date]                                          AS [Date],
       CAST(Year([LGENH].[Date]) AS int)              AS [Year],
         [LU_LAD_OA].[LAD]                                       AS [LAD],  
         [LU_LAD_OA].[LAD_NAME]                                  AS [LAD_NAME],
         [LU_WARD_OA].[WARD_CODE]                                AS [WARD_CODE],
         [LU_WARD_OA].[WARD_NAME]                                AS [WARD_NAME],
         [LGENH].[OAcode]                                        AS [OA],
       CONVERT(float, [LGENH].[levcel1]) + 
       CONVERT(float, [LGENH].[levcel2]) + 
       CONVERT(float, [LGENH].[levcel3]) + 
       CONVERT(float, [LGENH].[levcel4]) + 
       CONVERT(float, [LGENH].[levcel5]) + 
       CONVERT(float, [LGENH].[levcel6])                       AS [All], 
       CONVERT(float, [LGENH].[levcel1])                       AS [Level_1],
       CONVERT(float, [LGENH].[levcel2])                       AS [Level_2],
       CONVERT(float, [LGENH].[levcel3])                       AS [Level_3],
       CONVERT(float, [LGENH].[levcel4])                       AS [Level_4],
       CONVERT(float, [LGENH].[levcel5])                       AS [Level_5],
       CONVERT(float, [LGENH].[levcel6])                       AS [Level_6]
  FROM [LondonGeneralhealth]                        AS [LGENH],
        [LOOKUP_LAD_OA]                                          AS [LU_LAD_OA],
        [LOOKUP_WARD_CODE_OA]                                    AS [LU_WARD_OA]
  WHERE [LGENH].[OAcode] = [LU_LAD_OA].[OA]
  AND   [LU_LAD_OA].[OA] = [LU_WARD_OA].[OA]
  ) 
  SELECT [SGHB].[YEAR]                                       AS [YEAR],
         AVG([SGHB].[Level_1] /[SGHB].[All])              AS [Level 1],
         AVG([SGHB].[Level_2] /[SGHB].[All])              AS [Level 2],
         AVG([SGHB].[Level_3] /[SGHB].[All])              AS [Level 3],
         AVG([SGHB].[Level_4] /[SGHB].[All])              AS [Level 4],
         AVG([SGHB].[Level_5] /[SGHB].[All])              AS [Level 5],
         AVG([SGHB].[Level_6] /[SGHB].[All])              AS [Level 6]
  FROM [SUMMED_GENERAL_HEALTH_BOROUGH] AS [SGHB]
  GROUP BY [YEAR]
  ORDER BY [YEAR] DESC
"""
  
  general_health_ratio_average_years_df = pd.read_sql_query(general_health_ratio_average_years_sql, db_conn, index_col=None)
  return general_health_ratio_average_years_df