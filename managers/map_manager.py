import folium
import numpy as np
import pandas as pd
import os
import time
from selenium import webdriver
from lib import file_tools as ft

def generate_map(file, **kwargs):
    """
    Uses Selenium, chromium_driver and chrome executables on host to take the folium generated
    html file, render it then take a snapshot of the page, save it as a .png then return its 
    location to the caller.
    """
    
    post_code_search = kwargs["post_code_search"]
    ward_name = kwargs["ward_name"]
    post_code_search_longitude = kwargs["post_code_search_longitude"]
    post_code_search_latitude  = kwargs["post_code_search_latitude"]
    pc_longitudes = kwargs["pc_longitudes"]
    pc_latitudes = kwargs["pc_latitudes"]
    properties = kwargs["properties"]

    remove_temp_files =  properties["reports_generation"]["clean_temp_files"]
    chrome_binary_location = properties["chrome"]["binary_location"]
    browser_pause_s = properties["selenium"]["browser_pause_s"]
    
    ## Calculated
    pc_longitudes_max = pc_longitudes.max()
    pc_longitudes_min = pc_longitudes.min()
    
    pc_latitudes_max = pc_latitudes.max()
    pc_latitudes_min = pc_latitudes.min()
    
    pc_longitudes_mid = (pc_longitudes_max + pc_longitudes_min)/2
    pc_latitudes_mid  = (pc_latitudes_max + pc_latitudes_min)/2
    
    combined = np.column_stack((pc_latitudes, pc_longitudes))

    ## Create the map and add borough overlay = centre on centre of map 
    m = folium.Map(location=[pc_latitudes_mid, pc_longitudes_mid], zoom_start=12)
        
    m.fit_bounds([[pc_latitudes_min, pc_longitudes_min], [pc_latitudes_max, pc_longitudes_max]])
        
    m.get_root().html.add_child(folium.Element("""
    <style>
    .mapText {
        white-space: nowrap;
        color:blue;
        font-weight: bold;
        font-size:large
    }
    </style>"""))
        
    ## Add Ward Name Name                     
    folium.Marker([pc_latitudes_mid, pc_longitudes_mid],
                        icon=folium.DivIcon(html="" + ward_name + "",
                        class_name="mapText")).add_to(m)
                                                           
    folium.Rectangle(combined, color="green", 
                        weight=2,
                        fill=True,
                        fill_color="pink",
                        fill_opacity=0.2).add_to(m)
    
    ## Search Post_Code
    tooltip = post_code_search
    folium.Marker([post_code_search_latitude, post_code_search_longitude], 
                        icon=folium.DivIcon(html="" + post_code_search + "",
                        class_name="mapText")).add_to(m)
    
    ## Save the HTML file
    html_file = file + ".html"
    m.save(html_file)
        
    ## Load it
    from selenium.webdriver.chrome.options import Options as ChromiumOptions
    from selenium.webdriver.chrome.service import Service as ChromeService
    
    chrome_options = ChromiumOptions()
    chrome_options.headless = True
    
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("-no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    chrome_service = ChromeService(executable_path = chrome_binary_location)
    browser = webdriver.Chrome(service=chrome_service,
                               options = chrome_options
                               ) 
    
    html_file_abs =  "file:///" + os.path.abspath(html_file)
    
    print("Browser is loading {}".format(html_file))
    browser.get(html_file_abs)

    time.sleep(browser_pause_s)
    
    ## Save the map graphic
    location_png_file = file + ".png"
    browser.save_screenshot(location_png_file)
    browser.quit()   
    
    ft.remove_temp_file(html_file, remove_temp_files)
    
    return location_png_file
