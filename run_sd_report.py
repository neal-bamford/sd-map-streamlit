from data.daos import dao_facade_local as dao_fac

import managers.sd_report_type_crime as sd_report_man_crime
import managers.sd_report_type_general as sd_report_man_general
import managers.sd_report_type_health as sd_report_man_health
import managers.sd_report_type_income as sd_report_man_income

import config_logging
import controllers.sd_report_type_passed_controller as sd_report_controller

# sd_report_man = sd_report_man_crime
sd_report_man = sd_report_man_general
# sd_report_man = sd_report_man_health
# sd_report_man = sd_report_man_income

sd_report_controller.call_controller(sd_report_man)

