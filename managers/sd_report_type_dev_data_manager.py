from data.daos import dao_facade_local as dao_fac
from lib import db_tools as db_tools
from lib import stats as stats
from lib import plot_tools as plttool
from lib import masters_data_analytics_lib as mlib
from lib import general_tools as gen_tools

import numpy as np
import pandas as pd

def generate_report_data(session_id
					   , search_term
					   , report_context
				   	 , properties
				   	 , dao_fac=dao_fac
					   , **kwargs):  
	"""
	Manager to create the formatted String data to include in the sd_general_report_data
	"""
	
	###
	### PLACE ALL THE STATS COLLECTED INTO THE REPORT_CONTEXT
	###
	report_context["name_of_text_in_context"] = u"Some Interesting Unecode Text"
	report_context["include_gender_mekko"] = False
	report_context["crime_flat"] = False
	report_context["crime_up"] = False
	report_context["crime_down"] = True
	report_context["crime_trend_text"] = u"SOME CRIME TeXT New"
	

