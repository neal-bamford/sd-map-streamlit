from lib import masters_data_analytics_lib as mlib

import logging

log = logging.getLogger(__name__)

def generate_report_artefacts(session_id
                 , report_context
                 , properties
                 , **kwargs):  
  """
  Manager to create the formatted String data to include in the sd_general_report_data
  """

  report_context["name_of_image_in_context_1"] = "reports/images/plot-example.jpg"
  report_context["name_of_image_in_context_2"] = "reports/images/plot-example.png"
  