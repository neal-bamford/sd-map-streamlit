# INTELIGENT REPORT GENERATION

This repository is forms part of the dissertation for an MSc in Data Analytics at London Metropolitan University. At its core it generates reports based on templates created using MS Word and will combine the template with items within a shared dictionary called `report_contex`. Currently it can add text, images and tables. It is also possible to run Python code directly from the template, though this feature is currently experimental.

The code has been developed in the form of the controller to manager service pattern, incorporating daos when data is to be retrieved from the database. If accessing the SDMap database you will need to have your ip address included in the accepted list, it is suggested you use a static ip address, perhaps via a suitable VPN provider. The code is a standard set of Python modules which are either called directly, via a Jupyter notebook (which allows visualisations to be, you know visualised) or via a local instance of Streamlit, which is how this project is deployed for mass consumption.

# Running the Code Quickly

## Jupyter

## Streamlit

## Python

# Report Generation

To create a report based on a template you need the following

* A Word template file. An example of which can be seen 