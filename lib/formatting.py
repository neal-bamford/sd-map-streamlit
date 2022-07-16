def series_format(items, separator=","):
    """
    Comma separate a list of post codes
    """
    ret_str = ""
    for item in items:
        ret_str += item + separator + " "
        
    ret_str = ret_str[0:len(ret_str)-2] 
    
    replacement = " and "
    reverse_replacement = replacement[::-1]
    
    ret_str = ret_str[::-1].replace(" " + separator, reverse_replacement, 1)[::-1]

    return ret_str