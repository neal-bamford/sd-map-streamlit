# Introduction
This is brief description of the major components of this code base and how you might get something running to demonstrate how those major components produce a general report.

The code base is a Streamlit repository, but parts of it can be used in isolation and through an iPythjon notebook such as Jupter Lab's. It *must* however there are a number of limitations.

## Limitations

* The code must be run locally if using Jupyter Lab - the reason for this is that it reads and writes a number of artifacts from the repository and has not been tested within a hosted environment for this aspect.

* It can be run within a local instance of Streamlit, and should be if developing the online Streamlit version. see https://docs.streamlit.io/library/get-started/installation#install-streamlit-on-windows to do this. If you do want to do this the use the Python file SD_Map_Dev.py when starting Streamlit.
** Currently as of submission of this project, there is an issue with the hosted version of this Streamlit repository, due to a mismatch of Chromedriver versions and Chromium in the hosted environment. This will be investigated and resolved. For now I suggest you run the report generation through a local Jupyter lab instance

* You must have your local ip address in the list of allowed ip addresses against the SD Map Azure database, otherwise it won't connect.

* You will need to add the password credentials of the the user *sdmapuser* in the file .streamlit/secrets.toml password = "<<password>>"

* The file .streamlit/secrets.toml points to the chromedriver used to render the map image from the Folium html (it uses Javascript, long story). Currently it points at the repository instance of this see [chrome] ... binary_location = "./drivers/105/chromedriver.exe" and should work on a Windows environment. This is what's not working in the deployed environment currently.

* You will need to have a number of Python libraries installed. This list can be seen in the file ._requirements.txt


## Creating a document

If you have a local instance of Streamlit Running then follow the tests in the documentation provided separately. Otherwise use the Jupyter Notebook interface contained in ``SD_Map_01_Genearl_Report.ipynb``

### Setup your search
Change the values in the *Search Criteria* cell, or run with the provided ones. Exceute the cell's code.

city      = "London"

borough   = "Islington"
ward_name = "Holloway"
post_code = ""

year_from = 2013
year_to   = 2022


### Run it
Execute the code in under the *REPORT GENERATION* Cell.

### Observe the output
All being well, you should see a lot of output generated, some visualisations and (just above these) something like

[DEBUG] managers.sd_report_type_general: returning generated_report:./reports/generation/documents//REPORT_TYPE_01_GENERAL_sd_general_report_template_01.new.style.docx

That's where your report has been generated.



