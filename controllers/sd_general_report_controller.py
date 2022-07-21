import uuid
import logging
from data.daos import location_dao as loc_dao
from lib import masters_data_analytics_lib as lib

from managers import sd_general_report_manager as sd_gen_repo_man
from lib import masters_data_analytics_lib as mlib

log = logging.getLogger(__name__)

## Session ID - Fake here
session_id = str(uuid.uuid4())[:8]
session_id = "XX"



## Search term
## Search at the post code level
## Westminster       : SW1A 0RS
## Sutton            : E5 8ES
## City of London    : E1 6AN
## Greenwich         : SE18 4AF
city = "london"
borough = "Bromley"
ward = "Bromley Town"
post_code = ""

city = "london"
borough = "Merton"
ward = "Dundonald"
post_code = ""

city = "London"
borough = "City of London"
ward = "Lime Street"
# post_code = "IG11 7FD"
post_code = "SW20 8ED"

## Parameter to pass
search_term = {"city"      : city
             , "ward_name" : ward
             , "borough"   : borough
             , "post_code" : post_code}

log.info(f"search_term:{search_term}")

## Generate a context to place items in which is used when generating the report in the final step
report_context = {}

## This comes from Streamlit so fake here
properties = {"selenium":{"browser_pause_s":3},
              "reports_generation":{"clean_temp_files":True},
              "chrome":{"binary_location":"C:/DISTRIBUTIONS/ChromeDriver/chromedriver.exe"}}

log.info(f"properties:{properties}")

generated_report = sd_gen_repo_man.generate_report(session_id=session_id, search_term=search_term, report_context=report_context, lib=mlib, properties=properties)

print(generated_report)
