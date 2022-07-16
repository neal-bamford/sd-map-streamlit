import os 

def remove_temp_file(file_name, override=None):
    """
    Removes a file if override is defined, will use its true/false value
    """
    remove_file = True;
    
   
    if override != None:
        print(override)
        remove_file = override
    
    if remove_file:
        os.remove(file_name)
    