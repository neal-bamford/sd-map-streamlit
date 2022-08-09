from managers import sd_report_manager_new as sd_rep_man

import config_logging
import logging
import toml
# from scratch import code_executor

properties = toml.load("./.streamlit/secrets.toml")
log = logging.getLogger(__name__)

session_id = "XX"

report_context = {}
report_context["template_processor_file_name"] = "./reports/processors/sd_new_manager_template.json"
report_context["report_option"] = 2

## Set up the images
report_context["name_of_image_in_context_1"] = "./reports/generation/images/XX_bump_borough_crime_per_capita_ranking_filtered_London_2010_2021.png"
report_context["name_of_image_in_context_2"] = "./reports/generation/images/XX_mekko_gender_borough_London_Islington_Holloway.png"

## Set up the text
report_context["text_example"] = "This is some text which is generated"
report_context["name_of_text_in_context"] = "Some Text to place in the Table Cell"

generated_report_file = sd_rep_man.generate_report(session_id,
                                                   report_context,
                                                   properties)

log.debug(generated_report_file)