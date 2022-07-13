-- LONDONPOSTCODES reduced
CREATE OR ALTER 
VIEW [streamlit_london_postcodes_oa] AS
SELECT 'London'                      AS [City],
	  LPC.[PCD]			             AS [Post_Code],
	  OPGE.[latitude]                AS [latitude],
	  OPGE.[longitude]               AS [longitude],
	  OPGE.[easting]                 AS [easting],
	  OPGE.[northing]                AS [northing],
      LPC.[OA]			             AS [OAcode],
	  LPC.[WARD_NAME]			     AS [WARD_NAME],
	  LPC.[LAD_NAME]			     AS [borough]
FROM IDX_LONDONPOSTCODES LPC 
INNER JOIN open_postcode_geo_england OPGE ON LPC.[PCD]  = OPGE.[postcode];

-- There are 143964 missing postcodes in postcodelatlng which exist in LONDONDPOSTCODES
SELECT COUNT(SLPOA.[Post_Code]) FROM streamlit_london_postcodes_oa SLPOA WHERE SLPOA.[Post_Code] NOT IN (SELECT p.[postcode] FROM postcodelatlng p)

-- There are 0 missing postcodes in open_postcode_geo_england which exist in LONDONDPOSTCODES
SELECT COUNT(SLPOA.[Post_Code]) FROM streamlit_london_postcodes_oa SLPOA WHERE SLPOA.[Post_Code] NOT IN (SELECT OPG.[postcode] FROM open_postcode_geo_england OPG)

-- Count of OAcode
SELECT COUNT(DISTINCT SLPOA.[OAcode]) FROM streamlit_london_postcodes_oa SLPOA; -- 25,031
--
-- Conclusion - There are missing rows from postcodelatlng
--

ALTER TABLE IDX_LONDONPOSTCODES
ALTER COLUMN OA NVARCHAR(20);

--
--
-- LondonHousehold-LondonPopulation-LONDONPOSTCODES
CREATE OR ALTER 
VIEW [streamlit_london_household_population_oa] AS
SELECT 'London'                                 AS [City],
	   LHD.[date]                               AS [date],
	   LHD.[OAcode]                             AS [OAcode],
	   LPC.[WARD_NAME]			                AS [WARD_NAME],
	   LPC.[LAD_NAME]			                AS [borough],
	   CAST(LPO.[All] AS int)			        AS [OApopulation],
	   CAST(LHD.[All] AS int)                   AS [All],
	   CAST(LHD.[Unshared] AS int)              AS [Unshared],
	   CAST(LHD.[Shared] AS int)                AS [Shared],
	   CAST(LHD.[Sharedhouse] AS int)           AS [Sharedhouse],
	   CAST(LHD.[Householdwithresident] AS int) AS [HouseholdWithResident],
	   CAST(LHD.[Householdnoresidents] AS int)  AS [HouseholdNoResidents],
	   CAST(LHD.[Detached] AS int) +
	   CAST(LHD.[Semi-detached] AS int) +
	   CAST(LHD.[Terraced] AS int) +
	   CAST(LHD.[Flat] AS int)				      AS [Dwelling_Total],
	   CAST(LHD.[Detached] AS int)     		      AS [Detached],	
	   CAST(LHD.[Semi-detached] AS int)           AS [Semi_detached],
	   CAST(LHD.[Terraced] AS int)                AS [Terraced],
	   CAST(LHD.[Flat] AS int)                    AS [Flat],
	   CAST(LHD.[Commercial building] AS int)     AS [CommercialBuilding],
	   CAST(LHD.[MobileBuilding] AS int)          AS [MobileBuilding]
FROM (LondonHousehold LHD
INNER JOIN LondonPopulation LPO ON LEFT(LPO.[date], 4) = LHD.[date] AND
                                   LPO.[OAcode] = LHD.OAcode) 
CROSS APPLY(
	SELECT TOP 1 LPCCA.[WARD_NAME],
	             LPCCA.[LAD_NAME]	     
	FROM IDX_LONDONPOSTCODES LPCCA
	WHERE LPCCA.[OA] = LHD.[OACode]
) LPC;
-- Count of OAcode
SELECT COUNT(SLHPOA.[OAcode]) FROM streamlit_london_household_population_oa SLHPOA; --25,031

--
--
-- LondonHousehold-LondonPopulation-LONDONPOSTCODES
CREATE OR ALTER 
VIEW [streamlit_london_qualifictation_population_oa]   AS
SELECT 'London'                                        AS [City],
	  LQL.[date]                                       AS [date],
	  LQL.[OAcode]                                     AS [OAcode],
	  LPC.[WARD_NAME]			                       AS [WARD_NAME],
	  LPC.[LAD_NAME]			                       AS [borough],
	  CAST(LPO.[All] AS int)			               AS [OApopulation],
	  CAST(LQL.[All] AS int)                           AS [All],
	  CAST(LPO.[All] AS int) -
	  CAST(LQL.[All] AS int) 						   AS [UnkownQualification],
	  CAST(LQL.[NoQualification] AS int)               AS [NoQualification],
	  CAST(LQL.[Level1] AS int)                        AS [Level1],
      CAST(LQL.[Level2] AS int)                        AS [Level2],
      CAST(LQL.[Level3] AS int)                        AS [Level3],
      CAST(LQL.[Level4] AS int)                        AS [Level4],
      CAST(LQL.[OtherQualifications] AS int)           AS [OtherQualifications],
      CAST(LQL.[Apprenticeship] AS int)                AS [Apprenticeship],
      CAST(LQL.[FTStudents16-17] AS int)               AS [FTStudents16_17],
      CAST(LQL.[FTStudents18above] AS int)             AS [FTStudents18Above],
      CAST(LQL.[FTStudents18aboveinEmp] AS int)        AS [FTStudents18AboveInEmp],
      CAST(LQL.[FTStudents18aboveinUnemp] AS int)      AS [FTStudents18AboveInUnemp],
      CAST(LQL.[FTStudents18aboveinECinactive] AS int) AS [FTStudents18AboveInECInactive]
      FROM (LondonQualification LQL
INNER JOIN LondonPopulation LPO ON LEFT(LPO.[date], 4) = LQL.[date] AND
                                   LPO.[OAcode] = LQL.OAcode) 
CROSS APPLY(
	SELECT TOP 1 LPCCA.[WARD_NAME],
	             LPCCA.[LAD_NAME]	     
	FROM IDX_LONDONPOSTCODES LPCCA
	WHERE LPCCA.[OA] = LQL.[OACode]
) LPC;
-- Count of OAcode
SELECT COUNT(SLQPOA.[OAcode]) FROM streamlit_london_qualifictation_population_oa SLQPOA; -- 25,031

--
--
-- LondonPopulation-LONDONPOSTCODES
CREATE OR ALTER 
VIEW [streamlit_london_population_oa]   			  AS
SELECT 'London'                                       AS [City],
	  LPO.[date]                                      AS [date],
	  LPO.[OAcode]                                    AS [OAcode],
	  LPC.[WARD_NAME]			                      AS [WARD_NAME],
	  LPC.[LAD_NAME]			                      AS [borough],
	  CAST(LPO.[All] AS int)			              AS [All],
	  CAST(LPO.[Males] AS int)			              AS [Males],
	  CAST(LPO.[Females] AS int)			          AS [Females],
	  CAST(LPO.[Livesinhousehold] AS int)			  AS [Livesinhousehold],
	  CAST(LPO.[Livesincommunalestablishment] AS int) AS [LivesInCommunalEstablishment],
      CAST(LPO.[student] AS int)			          AS [student],
      CAST(LPO.[AreaHectares] AS float)			      AS [AreaHectares],
      CAST(LPO.[DensityPPH] AS float)			      AS [DensityPPH]
      FROM LondonPopulation LPO
CROSS APPLY(
	SELECT TOP 1 LPCCA.[WARD_NAME],
	             LPCCA.[LAD_NAME]	     
	FROM IDX_LONDONPOSTCODES LPCCA
	WHERE LPCCA.[OA] = LPO.[OACode]
) LPC;
-- Count of OAcode
SELECT COUNT(SLPOA.[OAcode]) FROM streamlit_london_population_oa SLPOA; -- 25,031

