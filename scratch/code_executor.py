import logging
## Mimics the Word Table Cell
from .cell_example import Cell

log = logging.getLogger(__name__)


from typing import Callable

def my_exec(str_command):
  str_command = add_lambda(str_command)
  exec(str_command, globals(), locals())
  
def iif(condition, function_true: Callable[[], None], function_false: Callable[[], None]) -> None:
  log.debug(f"{condition}")
  function_true() if condition else function_false()

def some_function(p_str):
  print(f"Hello {p_str}")
  
def include_image(image_location, image_alignment='left', image_width=6):
  if "table_cell" not in locals:
    log.error("Can not reference table_cell")
  else:
    table_cell = locals["table_cell"]
    table_cell.set_image_content(image_location, image_alignment, image_width)
    
    log.info(f"{table_cell.get_content()}")
  
def include_text(text, text_alignment='left'):
  if "table_cell" not in locals:
    log.error("Can not reference table_cell")
  else:
    table_cell = locals["table_cell"]
    table_cell.set_text_content(text, text_alignment)
    
    log.info(f"{table_cell.get_content()}")

if 1==2:  
  run_command = True
  cell = Cell.__new__(Cell)
  # cell.__init__()
  
  image_location = "/some/image/location/and_image_name.png"
  some_text      = "Some interesting data analytics text..."
  
  locals = {}
  
  locals["run_command"] = run_command
  locals["cell"] = cell
  locals["include_image"] = include_image
  locals["some_text"] = some_text
  
  table_cell_text = """{{
  
  if run_command:
    # include_image(image_location)
    # include_image(image_location, 'centre', 8)
    include_text(some_text, 'justified')
  }}"""
  
  
  if table_cell_text.startswith("{{"):
    # Add the table cell to the globals
    locals["table_cell"] = cell ##Might need a UUID to segment session
  
    # Take the value found that we think is a command and strip out the command part
    table_cell_text = table_cell_text.replace("{{", "").replace("}}", "")
    
    # Call the code and catch the response
    response = exec(table_cell_text, globals() ,{"run_command":run_command})
    
    if response != None:
      log.error(response)
  
  else:
    log.warn("Not a Command")
  
def add_lambda(function_call_str) -> str:
  ret_val = function_call_str.replace("some_function", "lambda:some_function")
  ret_val = ret_val.replace("iif", "lambda:iif")
  if(ret_val.startswith("lambda:")):
    ret_val = ret_val.replace("lambda:", "", 1)
    log.debug(ret_val)
    
  
  return ret_val

log.info(locals)  
my_exec("iif(1==1, some_function('true'), iif(1==2, some_function('true 2'), iif(1==1, some_function('true 3'), some_function('false 3'))))")
# iif(1==2, lambda:some_function('true'), lambda:iif(1==2, lambda:some_function('true 2'), lambda:some_function('false 2')))
  