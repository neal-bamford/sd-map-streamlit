from lib import masters_data_analytics_lib as mlib

import logging
import uuid

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
ward_name = "Bromley Town"
post_code = ""

city = "london"
borough = "Hackney"
ward_name = "Brownswood"
post_code = ""

# borough = "Islington"
# ward_name = "Holloway"

year_from=2001
year_to=2022

# city = "London"
# borough = "City of London"
# ward_name = "Lime Street"
# post_code = "IG11 7FD"
# # post_code = ""

## Parameter to pass
search_term = {"city"      : city
             , "ward_name" : ward_name
             , "borough"   : borough
             , "post_code" : post_code
             , "year_from" : year_from
             , "year_to"   : year_to}

log.info(f"search_term:{search_term}")

## Generate a context to place items in which is used when generating the report in the final step
report_context = {}
report_context["report_option"] = "Condensed Report"
report_context["report_option"] = "Full Report"
import toml
properties = toml.load("./.streamlit/secrets.toml")
## This comes from Streamlit so fake here
# properties = {"selenium":{"browser_pause_s":3},
#               "reports_generation":{"clean_temp_files":True},
#               "chrome":{"binary_location":"C:/DISTRIBUTIONS/ChromeDriver/chromedriver.exe"}}

log.info(f"properties:{properties}")

def call_controller(sd_report_man):
  log.debug("CONTROLLER STARTED")
  generated_report = sd_report_man.generate_report(session_id=session_id, search_term=search_term, report_context=report_context, lib=mlib, properties=properties)
  log.info(generated_report)
  # log.info(report_context)
  log.debug("CONTROLLER FINISHED")
