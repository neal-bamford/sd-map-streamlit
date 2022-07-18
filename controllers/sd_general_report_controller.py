import uuid

from managers import sd_general_report_manager as sd_gen_repo_man
from lib import masters_data_analytics_lib as mlib

## Session ID - Fake here
session_id = str(uuid.uuid4())[:8]



## Search term
## Search at the post code level
## Westminster       : SW1A 0RS
## Sutton            : E5 8ES
## City of London    : E1 6AN
## Greenwich         : SE18 4AF
city = "london"
ward = ""
borough = ""
post_code = "BR1 1AA"

## Parameter to pass
search_term = {"city"      : city
             , "ward"      : ward
             , "borough"   : borough
             , "post_code" : post_code}


## Generate a context to place items in which is used when generating the report in the final step
report_context = {}
report_context["template_processor_file_name"] = "./reports/processors/sd_general_report_data_manager.json"

## This comes from Streamlit so fake here
properties = {"selenium":{"browser_pause_s":3},
              "reports_generation":{"clean_temp_files":True},
              "chrome":{"binary_location":"C:/DISTRIBUTIONS/ChromeDriver/chromedriver.exe"}}

generated_report = sd_gen_repo_man.generate_report(session_id=session_id, search_term=search_term, report_context=report_context, lib=mlib, properties=properties)

print(report_context)
print(generated_report)
