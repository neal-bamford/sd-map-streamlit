import json
import uuid

def replace_place_holders(str, place_holder_str, replacement_str, ):
    """
    Replaces a place_holder surrounded by "{place_holder_str}" in str 
    with replacement_str 
    """
    place_holder_str = "{" + place_holder_str + "}"
    str = str.replace(place_holder_str, replacement_str)
    return str

def json_template_processor(template_file_str, session_id, template_option, merge_field_vals):
    _version_ = 1.0
    
    ## Get the json file
    with open(template_file_str) as template_file:
        json_processor = json.load(template_file)
    
    ## Reference values in the json file
    domain = json_processor["domain"]
    description = json_processor["description"]
    version = json_processor["version"]
    
    #
    ## CHECK VERSIONS ARE COMPATIBLE
    #
    if _version_ != version:
        raise Exception("Method json_template_processor with version {} can not process json file {} with version {}".format(_version_, template_file_str, version))
    
    #
    ##
    ### STAGE 01 - Take the template and add the images
    ##
    #
    print("-- stage 01 - add images --")

    st01 = json_processor["stage_01"]
    st01_description = st01["description"]
    st01_input_folder = st01["input_folder"]
    st01_input_template = st01["input_template"]
    st01_output_folder = st01["output_folder"]
    st01_output_template = st01["output_template"]
    
    ## Make any token substitutions
    st01_output_template = replace_place_holders(st01_output_template, "session_id", session_id)
    
    ## This is what we will do
    print("-- stage description --")
    print(st01_description)
    print("\n")
    
    print("I am about to take the docx template file {}/{} and create the second stage docx template file {}/{}".format( \
          st01_input_folder,   \
          st01_input_template, \
          st01_output_folder,  \
          st01_output_template))
    
    #
    ## Choose the template option to use. Stage 01 dictates the option for both stages
    #
    
    ## List of options for stage 01
    st01_template_options = st01["template_options"]
    st01_template_options_len = len(st01_template_options)
    
    ## Set the template chosen from the list to None initially
    ## It will then either become 0 or the value passed in as 
    ## parameter template_option
    st01_template_option_to_use = None
    
    ## If we don't have the template option set in tempalte_option then default to 0
    try:
        for st01_template_option in st01_template_options:
            ## This will set the 
            if st01_template_option_to_use == None or st01_template_option["option_number"] == template_option:
                st01_template_option_to_use = st01_template_option
    except:
        print("An error occurred trying to set the option to use in stage 1")
    
    print("The stage one option to use is {}".format(st01_template_option_to_use["option_number"]))   
    #
    ## PROCESS STAGE 01 TEMPLATE OPTION
    #
    ## Reference the images and their location
    st01_template_images = st01_template_option_to_use["option_images"]
    
    ## Loop through the image options, consists of a table_cell number and image
    try:
        table_cell_to_remove = []
        for st01_template_images in st01_template_images:
            table_cell = st01_template_images["table_cell"]
            
            image_location = st01_template_images["image_location"]
            image_location = replace_place_holders(image_location, "session_id", session_id)

            ## ADD IMAGES            
            if image_location != "": 
                print("Within the template {}/{} inserting into table-cell {} image {}".format(st01_input_folder, \
                                                                                               st01_input_template,\
                                                                                               table_cell, \
                                                                                               image_location))
            ## We may want to delete the table cells than are empty so keep a track of them for re-processing
            else:
                table_cell_to_remove.append(table_cell)
            
        ## REMOVE TABLE CELLS NO LONGER NEEDED
        if len(table_cell_to_remove) > 0:
            print("We will now remove the following table cell{} {} before going to the second stage.".format("s" if len(table_cell_to_remove) >1 else "", \
                                                                                                          table_cell_to_remove))
    except Exception as e: 
        print("An error occurred trying to include images into table cells" + str(e))

    #
    ##
    ### STAGE 02 - take the new changed template and do merge
    ##
    #
    print("-- stage 02 - merge --")
    
    st02 = json_processor["stage_02"]
    st02_description = st02["description"]
    st02_output_folder = st02["output_folder"]
    st02_output_document = st02["output_document"]
    st02_output_document_web_name = st02["output_document_web_name"]
    
    ## Make any token substitutions
    st02_output_document = replace_place_holders(st02_output_document, "session_id", session_id)


    ## This is what we will do
    print("-- stage description --")
    print(st02_description)
    print("\n")
    
    print("I am about to take the stage 01 docx template file {}/{} and merge with data to create the docx file {}/{}".format( \
          st01_output_folder,  \
          st01_output_template, \
          st02_output_folder, \
          st02_output_document))
    
    st02_template_options = st02["template_options"]
    st02_template_options_len = len(st02_template_options) 
    #
    ## CHECK TEMPLATE OPTION LENGTHS ARE EQUAL
    #
    if st01_template_options_len != st02_template_options_len:
        raise Exception("Stage 1 template option length {} is != to stage 2 template option length".format(st01_template_option_len, \
                                                                                                           st02_template_option_len))

    st02_template_option_to_use = None
    
    ## If we don't have the template option set in tempalte_option then default to 0
    try:
        for st02_template_option in st02_template_options:
            ## This will set the 
            if st02_template_option_to_use == None or st02_template_option["option_number"] == template_option:
                st02_template_option_to_use = st02_template_option
    except:
        print("An error occurred trying to set the option to use in stage 2")

    #
    ## PROCESS STAGE 02 TEMPLATE OPTION
    #
    print("The stage two option to use is {}".format(st02_template_option_to_use["option_number"]))   
    
    ## Reference the images and their location
    st02_template_fields = st02_template_option_to_use["option_fields"]
    
    ## Loop through the field options, merge with placeholders in the docx template
    try:
        for st02_template_field in st02_template_fields:
            merge_field = st02_template_field["merge_field"]
            include_merge_field = st02_template_field["include_merge_field"]
            
            ## Check if the merge field exists in the passed in values. Raise an exception if not
            if merge_field not in merge_field_vals:
                raise Exception("Field {} is not present in merge field values".format(merge_field))
                
            ## Reference the value for use
            merge_field_value = merge_field_vals[merge_field]

            ## MERGE FIELDS           
            if include_merge_field: 
                print("Within the template {}/{} merging field {} with value {}".format(st01_output_folder, \
                                                                                        st01_output_template, \
                                                                                        merge_field, \
                                                                                        merge_field_value))
            ## We may want to delete the table cells than are empty so keep a track of them for re-processing
            else:
                print("Field {} with value {} will not be merged with template".format(merge_field, merge_field_value))
            
    except Exception as e: 
        print("An error occurred trying to include images into table cells" + str(e))    
    
    return st02_output_document_web_name, "DOCUMENT_CONTENTS" 

## Generate a session id
session_id = str(uuid.uuid1())
## Choose the template option for stage 1
template_option = 4

## THese are the fields merge values
merge_field_vals = {"A": "<<field_value_for_A>>", "B": "<<field_value_for_B>>", "C": "<<field_value_for_C>>", "D": "<<field_value_for_D>>"}
    
web_report_name, web_report = json_template_processor("../docx_generation/processors/example_json_processor.json", session_id, template_option, merge_field_vals)    
    


