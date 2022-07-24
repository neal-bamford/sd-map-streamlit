import logging
import pyodbc 

log = logging.getLogger(__name__)

def get_db_conn(database_props):
    try:                      
        db_conn = pyodbc.connect(driver   = database_props["driver"]
                               , server   = "{},{}\{}".format(database_props["host"], database_props["port"], database_props["instance"])
                               , database = database_props["database"]
                               , uid      = database_props["username"]
                               , pwd      = database_props["password"])

        log.info(f"DATABASE CONNECTIVITY") 
    except Exception as e:
        log.error(f"NO DATABASE CONNECTIVITY") 
        log.error(e)
        raise Exception("NO DATABASE CONNECTIVITY")
        
    return db_conn