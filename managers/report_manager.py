from docx import Document
import mailmerge as mm
import docx
from docx.shared import Inches
from fpdf import FPDF
from lib import file_tools as ft

def generate_report(session_id, template_name, location_png_file, report_merge_data, remove_temp_files=True):

    ## Start creating the report for the template
    # template_name = "sd_general_report_processor_template.docx"
    stage_01_template = "./reports/templates/{}".format(template_name);
    
    ## Take original templage and add all images
    # Pre-process to add images
    image_document = Document(stage_01_template)
    
    # Reference the tables. This is where we will add our images
    image_tables = image_document.tables
    paragraph = image_tables[0].rows[0].cells[0].add_paragraph()
    paragraph_run = paragraph.add_run()
    paragraph.alignment = 1
    
    # r.add_picture("../docx_generation/images/plot-example.jpg",width=Inches(4.0), height=Inches(.7))
    paragraph_run.add_picture(location_png_file, width=Inches(6.0))
    
    
    
    #
    # ## Save the template and reference it for the merge to happen in the next part
    stage_02_template = "./reports/generation/documents/{}_stage_02_template_{}".format(session_id, template_name)
    image_document.save(stage_02_template)
    
    
    # Merge text
    merge_document = mm.MailMerge(stage_02_template)
    merge_document.merge(**report_merge_data)
    
    ## Save the template
    stage_03_docx = "./reports/generation/documents/{}_{}".format(session_id, template_name)
    merge_document.write(stage_03_docx)
    
    ## Remove the intermediate template    
    merge_document.close()
    
    ## These may move to a list then be called at the end as a cleanup process    
    ft.remove_temp_file(location_png_file, remove_temp_files)
    ft.remove_temp_file(stage_02_template, remove_temp_files)
    
    return stage_03_docx