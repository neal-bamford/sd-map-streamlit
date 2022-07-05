from __future__ import print_function
from mailmerge import MailMerge
from datetime import date
import base64
import shutil

template = "../templates/Practical-Business-Python.docx"

document = MailMerge(template)
print(document.get_merge_fields())

s = document.merge(
    status='Gold',
    city='Springfield',
    phone_number='800-555-5555',
    Business='Cool Shoes',
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
            encoded = base64.b64encode(docx.read()).decode()

print(encoded)