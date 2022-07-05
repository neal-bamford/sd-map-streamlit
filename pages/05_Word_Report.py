from __future__ import print_function
import streamlit as st
import base64
import shutil
from fpdf import FPDF
from mailmerge import MailMerge
from datetime import date

st.markdown("# Word Report Page")
st.sidebar.markdown("# Word Report Page")

report_text = st.text_input("Report Text")


export_as_word = st.button("Export Report")

def create_download_link(val, filename):
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.docx">Download file</a>'

if export_as_word:

    template = "./templates/Practical-Business-Python.docx"
    
    document = MailMerge(template)
    print(document.get_merge_fields())
    
    s = document.merge(
        status=report_text,
        city='Springfield',
        phone_number='800-555-5555',
        Business=report_text,
        zip='55555',
        purchases='$500,00000000',
        shipping_limit='$5',
        state='MO',
        address='1234 Main Street',
        date='{:%d-%b-%Y}'.format(date.today()),
        discount='5%',
        recipient='Mr. Jones')
    
    
    document.write('test-output.docx')
    
    for file in ["test-output.docx"]:
            with open(file, "rb") as docx:
                encoded = docx.read()
    
    html = create_download_link(encoded , "test")

    st.markdown(html, unsafe_allow_html=True)