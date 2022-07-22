import logging
import logging.config
import json

logging_config_file_name = "./config/logger.cfg"
with open(logging_config_file_name) as logging_config_file:
    logging_config = json.load(logging_config_file)

logging.config.dictConfig(logging_config)
