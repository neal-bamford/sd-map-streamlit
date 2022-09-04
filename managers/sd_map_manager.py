import logging

import folium
import numpy as np
import pandas as pd
import os
import time
from selenium import webdriver
from lib import file_tools as ft

log = logging.getLogger(__name__)

def generate_map(file, **kwargs):
    """
    Uses Selenium, chromium_driver and Chrome executables on host to take the folium generated
    html file, render it then take a snapshot of the page, save it as a .png then return its 
    location to the caller.
    """
    properties = kwargs["properties"]
    map_args   = kwargs["map_args"]

    remove_temp_files =  properties["reports_generation"]["clean_temp_files"]
    chrome_binary_location = properties["chrome"]["binary_location"]
    browser_pause_s = properties["selenium"]["browser_pause_s"]
    
    ## We'll retrieve borough data but not use it for now        
    borough_d        = map_args["borough"]
    borough_long_lat = borough_d["lat_long"]
    borough_min_lat  = borough_long_lat[:, 0].min() 
    borough_max_lat  = borough_long_lat[:, 0].max() 
    borough_min_long = borough_long_lat[:, 1].min()
    borough_max_long = borough_long_lat[:, 1].max()
    
    borough_mid_lat  = (borough_min_lat + borough_max_lat)/2
    borough_mid_long = (borough_min_long + borough_max_long)/2
    borough_name = borough_d["label"]

    ## Create the map and add borough overlay = centre on centre of map 
    m = folium.Map(location=[borough_mid_lat, borough_mid_long], zoom_start=12)
    m.fit_bounds([[borough_min_lat, borough_min_long], [borough_max_lat, borough_max_long]])

    ###
    ### Ward level seems best 
    ###
    ward_name_d   = map_args["ward_name"]
    ward_long_lat = ward_name_d["lat_long"]
    ward_min_lat  = ward_long_lat[:, 0].min() 
    ward_max_lat  = ward_long_lat[:, 0].max() 
    ward_min_long = ward_long_lat[:, 1].min()
    ward_max_long = ward_long_lat[:, 1].max()
    ward_name     = ward_name_d["label"]
    
    ward_mid_lat  = (ward_min_lat + ward_max_lat)/2
    ward_mid_long = (ward_min_long + ward_max_long)/2
    
    ### Post Code
    post_code_level = False
    if "post_code" in map_args:
        post_code_level    = True
        post_code_d        = map_args["post_code"]
        post_code_long_lat = post_code_d["lat_long"]

        post_code_lat      = post_code_long_lat[:, 0]
        post_code_long     = post_code_long_lat[:, 1]

        post_code          = post_code_d["label"]
    
    ward_mid_lat  = (ward_min_lat + ward_max_lat)/2
    ward_mid_long = (ward_min_long + ward_max_long)/2
    
    map_bounds = [[ward_min_lat, ward_min_long], [ward_max_lat, ward_max_long]]
    # map_bounds = [[borough_min_lat, borough_min_long], [borough_max_lat, borough_max_long]]
    
    rectangle_bounds = [[ward_min_lat, ward_min_long], [ward_max_lat, ward_max_long]]
    # rectangle_bounds = [[borough_min_lat, borough_min_long], [borough_max_lat, borough_max_long]]

    ## Create the map and add borough overlay = centre on centre of map 
    map = folium.Map(location=[(borough_min_lat + borough_max_lat)/2, (borough_min_long + borough_max_long)/2], zoom_start=12)
    map.fit_bounds(map_bounds)

    folium.Rectangle(rectangle_bounds,
                     color = "pink", 
                     weight = 2,
                     fill = True,
                     fill_color = "pink",
                     fill_opacity=0.2).add_to(map)

    ## Add a style for the text on the map
    map.get_root().html.add_child(folium.Element("""
    <style>
    .mapText {
        white-space: nowrap;
        color:blue;
        font-weight: bold;
        font-size:large
    }
    </style>"""))
        
    #
    # Add the ward name                     
    #
    folium.Marker([ward_max_lat, ward_mid_long]
                 ,icon=folium.DivIcon(html = f"{ward_name}"
                 ,class_name = "mapText")).add_to(map)
                                                           
    #
    # Add post code
    #
    if post_code_level:
        folium.Marker([post_code_lat, post_code_long]
                    , icon=folium.DivIcon(html = f"{post_code}"
                    , class_name = "mapText")).add_to(map)
    
    ## Save the HTML file
    html_file = file + ".html"
    map.save(html_file)
        
    ## Load it
    from selenium.webdriver.chrome.options import Options as ChromiumOptions
    from selenium.webdriver.chrome.service import Service as ChromeService
    location_png_file = ""
    print("Before chrome_options")
    chrome_options = ChromiumOptions()
    # chrome_options.headless = True
      
    print("Before add_argument")
    chrome_options.add_argument("--headless")
    # chrome_options.add_argument("-no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    
    import chromedriver_binary as cdb
    print("Before add_chromedriver_to_path")
    cdb.add_chromedriver_to_path()
    
    # chrome_service = ChromeService(executable_path = chrome_binary_location)
    chrome_service = ChromeService()
    print("Before ChromeService()")
    chrome_service = ChromeService()
      # browser = webdriver.Chrome(service=chrome_service,
      #                            options = chrome_options
      #                            ) 
    print(">>>>>>>>>>>>>>>>>>>>>>>")
    print("before browser")
    browser = webdriver.Chrome(service=chrome_service, options = chrome_options, service_args=['--verbose', 'log-path=./chromedriver.log']) 
    print("after browser")
    print(">>>>>>>>>>>>>>>>>>>>>>>")
    if 1 == 2:    
      
      html_file_abs =  "file:///" + os.path.abspath(html_file)
      
      log.debug("Browser is loading {}".format(html_file))
      browser.get(html_file_abs)
    
      time.sleep(browser_pause_s)
      
      ## Save the map graphic
      location_png_file = file + ".png"
      browser.save_screenshot(location_png_file)
      browser.quit()   
      
      ft.remove_temp_file(html_file, remove_temp_files)
      
      return location_png_file
