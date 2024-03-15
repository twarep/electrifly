from shiny import App, render, ui, Inputs, Outputs, Session, reactive
from htmltools import HTML, css, div
from shiny.types import NavSetArg
from shiny.types import ImgData
from flight_querying import query_flights
from weather_querying import query_weather
import Graphing as Graphing
import shinyswatch
import numpy as np
import pandas as pd
import numpy as np
from os import getenv
from dotenv import load_dotenv
from shinywidgets import output_widget, render_widget
import sqlalchemy as sa
from datetime import datetime, timedelta
import simulation
import shiny.experimental as x
import faicons as fa
from model_querying import Model
from pathlib import Path
import asyncio
from math import ceil, floor

# List of custom aggregate variables
custom_aggregate_variables_dict = {
    "Flight ID": ["flight_id"], 
    "Time (min)": ["time_min"], 
    "Current (Amp)": ["bat_1_current", "bat_2_current"], 
    "Voltage (Volts)": ["bat_1_voltage", "bat_2_voltage"], 
    "State-of-Charge (Percent)": ["bat_1_soc", "bat_2_soc"], 
    "State-of-Health (Percent)": ["bat_1_soh", "bat_2_soh"], 
    "Motor Power (KW)": ["motor_power"], "Ground Speed (Knots)": ["ground_speed"], "Pressure Altitude (Meters)": ["pressure_alt"],
    "Average Cell Temperature (°C)": ["bat_1_avg_cell_temp", "bat_2_avg_cell_temp"], 
    "Minimum Cell Temperature (°C)": ["bat_1_min_cell_temp", "bat_2_min_cell_temp"], 
    "Maximum Cell Temperature (°C)": ["bat_1_max_cell_temp", "bat_2_max_cell_temp"], 
    "Minimum Cell Volt (Volts)": ["bat_1_min_cell_volt", "bat_2_min_cell_volt"], 
    "Maximum Cell Volt (Volts)": ["bat_1_max_cell_volt", "bat_2_max_cell_volt"], 
    "Inverter Cooling Temperature (°C)": ["inverter_cooling_temp_1", "inverter_cooling_temp_1"], 
    "Motor RPM (rpm)": ["motor_rpm"], "Motor Temperature (°C)": ["motor_temp"], 
    "Requested Torque (Nm)": ["requested_torque"], "Indicated Air Speed (Knots)": ["ias"], 
    "Latitude (Degrees)": ["lat"], "Longitude (Degrees)": ["lng"],
    'Stall Warn Active (0/1)': ["stall_warn_active"], 'Inverter Temp (°C)': ["inverter_temp"],
    'Bat 1 Cooling Temp (°C)': ["bat_1_cooling_temp"], 'Remaining Flight Time': ["remaining_flight_time"],
    'Pitch (Degrees)': ["pitch"], 'Roll (Degrees)': ["roll"], 'Heading (Degrees)': ["heading"],
    'Stall Diff Pressure (Pa)': ["stall_diff_pressure"], 'QNG (hPa)': ["qng"], 
    'Outside Air Temperature (°C)': ["oat"], 'ISO Leakage Current': ["iso_leakage_current"]
}
custom_aggregate_variables = list(custom_aggregate_variables_dict.keys())

# List of custom granular variables
custom_granular_variables_dict = {"Flight ID": ["flight_id"], "Time (Min)": ["time_min"],
                        'Bat 1 Current (amp)': ["bat_1_current"], 'Bat 2 Current (amp)': ["bat_2_current"], 
                        'Bat 1 Voltage (volts)': ["bat_1_voltage"], 'Bat 2 Voltage (volts)': ["bat_2_voltage"],
                        'Bat 1 SOC (Percent)': ["bat_1_soc"], 'Bat 2 SOC (Percent)': ["bat_2_soc"], 'Bat 1 SOH (Percent)': ["bat_1_soh"], 'Bat 2 SOH (Percent)': ["bat_2_soh"], 
                        'Bat 1 Min Cell Temp (°C)': ["bat_1_min_cell_temp"], 'Bat 2 Min Cell Temp (°C)': ["bat_2_min_cell_temp"], 
                        'Bat 1 Max Cell Temp (°C)': ["bat_1_max_cell_temp"], 'Bat 2 Max Cell Temp (°C)': ["bat_2_max_cell_temp"], 
                        'Bat 1 Avg Cell Temp (°C)': ["bat_1_avg_cell_temp"], 'Bat 2 Avg Cell Temp (°C)': ["bat_2_avg_cell_temp"], 
                        'Bat 1 Min Cell Volt (volts)': ["bat_1_min_cell_volt"], 'Bat 2 Min Cell Volt (volts)': ["bat_2_min_cell_volt"], 
                        'Bat 1 Max Cell Volt (volts)': ["bat_1_max_cell_volt"], 'Bat 2 Max Cell Volt (volts)': ["bat_2_max_cell_volt"], 
                        'Requested Torque (Nm)': ["requested_torque"], 'Indicated Air Speed (knots)': ["ias"],
                        'Motor RPM (rpm)': ["motor_rpm"], 'Motor Power (KW)': ["motor_power"], 'Motor Temp (°C)': ["motor_temp"], 
                        'Stall Warn Active (0/1)': ["stall_warn_active"], 'Inverter Temp (°C)': ["inverter_temp"], 'Bat 1 Cooling Temp (°C)': ["bat_1_cooling_temp"],
                        'Inverter Cooling Temp 1 (°C)': ["inverter_cooling_temp_1"], 'Inverter Cooling Temp 2 (°C)': ["inverter_cooling_temp_2"], 
                        'Remaining Flight Time': ["remaining_flight_time"], 'Pressure Altitude (m)': ["pressure_alt"], 
                        'Latitude (Degrees)': ["lat"], 'Longitude (Degrees)': ["lng"], 
                        'Ground Speed (knots)': ["ground_speed"], 'Time Stamp (Seconds)': ["time_stamp"],
                        'Pitch (Degrees)': ["pitch"], 'Roll (Degrees)': ["roll"], 'Heading (Degrees)': ["heading"], 
                        'Stall Diff Pressure (Pa)': ["stall_diff_pressure"], 'QNG (hPa)': ["qng"], 
                        'Outside Air Temperature (°C)': ["oat"], 'ISO Leakage Current': ["iso_leakage_current"]
}
custom_granular_variables = list(custom_granular_variables_dict.keys())

# List of custom granular variables
custom_weather_dict = {"Temperature (°F)": ["temperature"], "Dewpoint (°F)": ["dewpoint"], "Relative Humidity (Percent)": ["relative_humidity"],
                        "Wind Direction (Degrees)": ["wind_direction"], "Wind Speed (knots)": ["wind_speed"], "Pressure Altimeter (in)": ["pressure_altimeter"],
                        "Sea Level Pressure (mbar)": ["sea_level_pressure"], "Visibility (mi)": ["visibility"], 
                        "Wind Gust (knots)": ["wind_gust"], "Sky Level 1 (ft)": ["sky_level_1"], "Sky Level 2 (ft)": ["sky_level_2"], "Sky Level 3 (ft)": ["sky_level_3"], "Sky Level 4 (ft)": ["sky_level_4"]
}
custom_weather_variables = list(custom_weather_dict.keys())

# List of variables
charging_variables_columns = {
    "Time (min)": ["time_min"], 
    "State-of-Charge (Percent)": ["bat_1_soc", "bat_2_soc"], 
    "State-of-Health (Percent)": ["bat_1_soh", "bat_2_soh"], 
    "Average Cell Temperature (°C)": ["bat_1_avg_cell_temp", "bat_2_avg_cell_temp"],
    "Minimum Cell Temperature (°C)": ["bat_1_min_cell_temp", "bat_2_min_cell_temp"],
    "Maximum Cell Temperature (°C)": ["bat_1_max_cell_temp", "bat_2_max_cell_temp"],
    "Temperature (°C)": ["temperature"],
}
charging_variables = list(charging_variables_columns.keys())

# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
# Getting the dates to be used in the ML UI:
def get_dates():
    
    # Get dates from datetime
    current_date = datetime.now().date()
    tomorrow_date = current_date + timedelta(days=1)
    day_after_tomorrow_date = current_date + timedelta(days=2)

    # Turn them into strings
    string_current_date = current_date.strftime("%b %d, %Y")
    string_tomorrow_date = tomorrow_date.strftime("%b %d, %Y")
    string_day_after_tomorrow_date = day_after_tomorrow_date.strftime("%b %d, %Y")

    # Create a list and add the dates
    list_of_dates = [string_current_date, string_tomorrow_date, string_day_after_tomorrow_date]

    return list_of_dates

# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
def change_order():
    # initialize flight querying and get list of uniqye activities
    flight_conn = query_flights()
    list_of_activities = flight_conn.get_flight_activities()

    # Set the activity order and add all other activities aside from NA and TBD
    order_activities = ["pre-flight", "takeoff", "climb", "cruise", "descent", "landing"]
    for activity in list_of_activities:
        if activity not in order_activities and activity not in ["NA", "TBD"]:
            order_activities.append(activity)
        
    # Return the ordered activity
    return order_activities


# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
def delete_style(val):
    return "font-weight: bold; text-decoration: underline;"

  
# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
def get_flights(flight_type="Flight test", columns=["id", "flight_date", "flight_time_utc"], table="flights"):
    """
    The function uses the query_flights class to get all the flights ids and dates in a dictionary of key: value --> flight_date: flight_id. 

    Parameters:
        date: Boolean value to specify if you only want to return a list of flight dates from the DB.

    Returns:
        if date is FALSE --> flight_date: dictionary of flight_date: flight_id pairs
    """
    flights = query_flights()

    flight_data = flights.get_flight_id_and_dates(flight_type, columns, table)
    
    return flight_data

# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
def get_charging_data(columns=["id", "flight_date", "flight_time_utc"], table="flights"):
    """
    The function uses the query_flights class to get all the flights ids and dates in a dictionary of key: value --> flight_date: flight_id. 

    Parameters:
        date: Boolean value to specify if you only want to return a list of flight dates from the DB.

    Returns:
        if date is FALSE --> flight_date: dictionary of flight_date: flight_id pairs
    """
    charging_sessions = query_flights()

    charging_data = charging_sessions.get_flight_id_and_dates("Charging", columns, table)
    
    return charging_data

# Function ---------------------------------------------------------------------------------------------------------------------------------------------------------
def get_most_recent_run_time():
    # initialize flight querying and get list of uniqye activities
    flight_conn = query_flights()
    new_date = flight_conn.get_last_scraper_runtime().strftime("%b %d, %Y at %I:%M %p")
    return new_date


# blue theme color
blue = "#3459e6"
grey = "#878787"
red = "#FF0000"
light_grey = "#F0F0F0"


# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
app_ui = ui.page_fluid(
    shinyswatch.theme.zephyr(),
    ui.tags.head(ui.tags.link(rel="icon", type="image/x-icon", href="/favicon.ico?")),
    ui.navset_card_pill(  
        # ===============================================================================================================================================================
        # START: HOMEPAGE
        # ===============================================================================================================================================================
        ui.nav_panel("ElectriFly",
          div(HTML(f"""<h1 style="text-align: center; font-weight: bolder; padding: 2rem 0">
                          <span style="color: {blue}">Empowering</span>
                          <span>Flight,</span>
                          <span style="color: {blue};">Electriflying</span>
                          <span>Tomorrow!</span>
                        </h1>
                    """)
          ),
          ui.div(ui.output_image("velis_img", width="100%", height="100%"), 
            style="text-align: center; padding-bottom: 3rem;",   
          ),
          ui.div(
            ui.row(
              ui.column(4, 
                        div(HTML(f"""
                                  <div style="display: flex; align-items: center; justify-content: center; padding-bottom: 2rem;">&nbsp;&nbsp;&nbsp;
                                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512" style="width: 40px; height: auto; margin-right: 15px;">
                                      <path d="M381 114.9L186.1 41.8c-16.7-6.2-35.2-5.3-51.1 2.7L89.1 67.4C78 73 77.2 88.5 87.6 95.2l146.9 94.5L136 240 77.8 214.1c-8.7-3.9-18.8-3.7-27.3 .6L18.3 230.8c-9.3 4.7-11.8 16.8-5 24.7l73.1 85.3c6.1 7.1 15 11.2 24.3 11.2H248.4c5 0 9.9-1.2 14.3-3.4L535.6 212.2c46.5-23.3 82.5-63.3 100.8-112C645.9 75 627.2 48 600.2 48H542.8c-20.2 0-40.2 4.8-58.2 14L381 114.9zM0 480c0 17.7 14.3 32 32 32H608c17.7 0 32-14.3 32-32s-14.3-32-32-32H32c-17.7 0-32 14.3-32 32z"/>
                                    </svg>
                                    <h2 style="font-weight: bolder;">What is <span style="color: {blue};">ElectriFly?</span></h2>
                                  </div>
                                  <div style="display: flex; align-items: center; justify-content: center; padding-bottom: 1rem;">
                                    <?xml version="1.0" encoding="UTF-8" standalone="no"?> <svg width="183.43576" zoomAndPan="magnify" viewBox="0 0 183.43576 169.21901" height="169.21901" preserveAspectRatio="xMidYMid" version="1.0" id="svg74" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg"> <defs id="defs22"> <clipPath id="f799c83bfd"> <path d="m 110.36328,158.75391 h 154.5 v 87 h -154.5 z m 0,0" clip-rule="nonzero" id="path1" /> </clipPath> <clipPath id="7794839981"> <path d="M 128.75391,199 H 148 v 31.47266 h -19.24609 z m 0,0" clip-rule="nonzero" id="path2" /> </clipPath> <clipPath id="a06dea72d9"> <path d="m 158,195 h 20 v 35.47266 h -20 z m 0,0" clip-rule="nonzero" id="path3" /> </clipPath> <clipPath id="e269844781"> <path d="m 188,184 h 20 v 46.47266 h -20 z m 0,0" clip-rule="nonzero" id="path4" /> </clipPath> <clipPath id="1417e61c86"> <path d="m 218,166 h 19.50391 v 64.47266 H 218 Z m 0,0" clip-rule="nonzero" id="path5" /> </clipPath> <clipPath id="a5fa93ec79"> <path d="m 128.75391,116.47266 h 108.75 V 190 h -108.75 z m 0,0" clip-rule="nonzero" id="path6" /> </clipPath> <clipPath id="d937094b42"> <path d="m 199.18359,109.50781 h 59.92578 V 127 h -59.92578 z m 0,0" clip-rule="nonzero" id="path7" /> </clipPath> <clipPath id="384730fc70"> <path d="m 207.92969,109.50781 h 42.37109 c 2.32031,0 4.54297,0.92188 6.18359,2.5625 1.64063,1.64063 2.5625,3.86328 2.5625,6.1836 0,2.32031 -0.92187,4.54297 -2.5625,6.18359 -1.64062,1.64063 -3.86328,2.5625 -6.18359,2.5625 h -42.37109 c -2.32032,0 -4.54297,-0.92187 -6.1836,-2.5625 -1.64062,-1.64062 -2.5625,-3.86328 -2.5625,-6.18359 0,-2.32032 0.92188,-4.54297 2.5625,-6.1836 1.64063,-1.64062 3.86328,-2.5625 6.1836,-2.5625 z m 0,0" clip-rule="nonzero" id="path8" /> </clipPath> <clipPath id="2151049465"> <path d="M 115.70313,172.35547 H 183 v 20.48828 h -67.29687 z m 0,0" clip-rule="nonzero" id="path9" /> </clipPath> <clipPath id="a9bb854531"> <path d="m 125.94531,172.35547 h 46.76172 c 5.66016,0 10.24609,4.58594 10.24609,10.24609 0,5.65625 -4.58593,10.24219 -10.24609,10.24219 h -46.76172 c -5.65625,0 -10.24218,-4.58594 -10.24218,-10.24219 0,-5.66015 4.58593,-10.24609 10.24218,-10.24609 z m 0,0" clip-rule="nonzero" id="path10" /> </clipPath> <clipPath id="f0d3ff19d1"> <path d="m 149.32812,165.10547 h 59.92579 v 17.49609 h -59.92579 z m 0,0" clip-rule="nonzero" id="path11" /> </clipPath> <clipPath id="c1458e90a1"> <path d="m 158.07422,165.10547 h 42.37109 c 2.32031,0 4.54297,0.92187 6.1836,2.5625 1.64062,1.64062 2.5625,3.86719 2.5625,6.1875 0,2.3164 -0.92188,4.54297 -2.5625,6.18359 -1.64063,1.64063 -3.86329,2.5625 -6.1836,2.5625 h -42.37109 c -2.32031,0 -4.54297,-0.92187 -6.1836,-2.5625 -1.64062,-1.64062 -2.5625,-3.86719 -2.5625,-6.18359 0,-2.32031 0.92188,-4.54688 2.5625,-6.1875 1.64063,-1.64063 3.86329,-2.5625 6.1836,-2.5625 z m 0,0" clip-rule="nonzero" id="path12" /> </clipPath> <clipPath id="b251c9648c"> <path d="m 171.66797,155.85547 h 74.23437 v 12.73047 h -74.23437 z m 0,0" clip-rule="nonzero" id="path13" /> </clipPath> <clipPath id="ea9f4fdd41"> <path d="m 178.03125,155.85547 h 61.47266 c 3.51562,0 6.36328,2.85156 6.36328,6.36719 0,3.51562 -2.84766,6.36328 -6.36328,6.36328 h -61.47266 c -3.51172,0 -6.36328,-2.84766 -6.36328,-6.36328 0,-3.51563 2.85156,-6.36719 6.36328,-6.36719 z m 0,0" clip-rule="nonzero" id="path14" /> </clipPath> <clipPath id="6f07b6a28f"> <path d="m 182.95312,135.36719 h 67.30469 v 20.48828 h -67.30469 z m 0,0" clip-rule="nonzero" id="path15" /> </clipPath> <clipPath id="7e48455ce7"> <path d="m 193.19531,135.36719 h 46.76172 c 5.65625,0 10.24609,4.58984 10.24609,10.24609 0,5.65625 -4.58984,10.24219 -10.24609,10.24219 h -46.76172 c -5.65625,0 -10.24219,-4.58594 -10.24219,-10.24219 0,-5.65625 4.58594,-10.24609 10.24219,-10.24609 z m 0,0" clip-rule="nonzero" id="path16" /> </clipPath> <clipPath id="c41ff71526"> <path d="m 191.79687,118.25391 h 67.3086 v 20.48828 h -67.3086 z m 0,0" clip-rule="nonzero" id="path17" /> </clipPath> <clipPath id="82558e6086"> <path d="m 202.04297,118.25391 h 46.76172 c 5.65625,0 10.24218,4.58593 10.24218,10.24218 0,5.66016 -4.58593,10.2461 -10.24218,10.2461 h -46.76172 c -5.66016,0 -10.2461,-4.58594 -10.2461,-10.2461 0,-5.65625 4.58594,-10.24218 10.2461,-10.24218 z m 0,0" clip-rule="nonzero" id="path18" /> </clipPath> <clipPath id="45f7f2125f"> <path d="m 173,111 h 76 v 71 h -76 z m 0,0" clip-rule="nonzero" id="path19" /> </clipPath> <clipPath id="b9c754249b"> <path d="m 168.19141,165.67187 65.05468,-67.507808 37.80078,36.429688 -65.05078,67.50781 z m 0,0" clip-rule="nonzero" id="path20" /> </clipPath> <clipPath id="eb39837003"> <path d="m 168.19141,165.67187 65.05468,-67.507808 37.80078,36.429688 -65.05078,67.50781 z m 0,0" clip-rule="nonzero" id="path21" /> </clipPath> <clipPath id="a9e2aeb642"> <path d="m 168.19141,165.67187 65.05468,-67.507808 37.80078,36.429688 -65.05078,67.50781 z m 0,0" clip-rule="nonzero" id="path22" /> </clipPath> </defs> <rect x="0" width="183.43576" fill="#ffffff" y="0" height="169.21901" fill-opacity="1" id="rect23" style="stroke-width:0.39152" /> <g clip-path="url(#f799c83bfd)" id="g23" transform="translate(-93.455765,-108.41905)"> <path fill="#000000" d="m 258.28516,177.18359 h -6.51954 v -8.48437 c 0,-5.45313 -4.43359,-9.89063 -9.88671,-9.89063 H 120.23047 c -5.45313,0 -9.89063,4.4375 -9.89063,9.89063 v 66.65625 c 0,5.45312 4.4375,9.89062 9.89063,9.89062 h 121.64844 c 5.45312,0 9.88671,-4.4375 9.88671,-9.89062 v -8.48828 h 6.51954 c 3.51171,0 6.36718,-2.85157 6.36718,-6.35547 v -36.96094 c 0.004,-3.51172 -2.85547,-6.36719 -6.36718,-6.36719 z m 2.41406,43.32422 c 0,1.32422 -1.08203,2.39844 -2.41016,2.39844 h -8.49609 c -1.08985,0 -1.97656,0.88672 -1.97656,1.98047 v 10.46484 c 0,3.27344 -2.66407,5.9336 -5.9336,5.9336 H 120.23047 c -3.26953,0 -5.93359,-2.66016 -5.93359,-5.9336 v -66.65234 c 0,-3.27344 2.66406,-5.9336 5.93359,-5.9336 h 121.64844 c 3.26953,0 5.93359,2.66016 5.93359,5.9336 v 10.46094 c 0,1.08984 0.88672,1.97656 1.97656,1.97656 h 8.4961 c 1.32812,0 2.41015,1.08203 2.41015,2.41015 v 36.96094 z m 0,0" fill-opacity="1" fill-rule="nonzero" id="path23" /> </g> <g clip-path="url(#7794839981)" id="g24" transform="translate(-93.455765,-108.41905)" style="fill:#3459e6;fill-opacity:1"> <path fill="#2f93ff" d="m 128.76172,199.50391 h 19.10156 v 31.17968 h -19.10156 z m 0,0" fill-opacity="1" fill-rule="nonzero" id="path24" style="fill:#3459e6;fill-opacity:1" /> </g> <g clip-path="url(#a06dea72d9)" id="g25" transform="translate(-93.455765,-108.41905)" style="fill:#3459e6;fill-opacity:1"> <path fill="#2f93ff" d="m 158.38281,230.68359 v -35.46875 h 19.26563 v 35.46875 z m 0,0" fill-opacity="1" fill-rule="nonzero" id="path25" style="fill:#3459e6;fill-opacity:1" /> </g> <g clip-path="url(#e269844781)" id="g26" transform="translate(-93.455765,-108.41905)" style="fill:#3459e6;fill-opacity:1"> <path fill="#2f93ff" d="m 188.01172,184.6875 h 19.8789 v 45.99609 h -19.8789 z m 0,0" fill-opacity="1" fill-rule="nonzero" id="path26" style="fill:#3459e6;fill-opacity:1" /> </g> <g clip-path="url(#1417e61c86)" id="g27" transform="translate(-93.455765,-108.41905)" style="fill:#3459e6;fill-opacity:1"> <path fill="#2f93ff" d="M 218.41406,166.36719 H 237.125 v 64.3164 h -18.71094 z m 0,0" fill-opacity="1" fill-rule="nonzero" id="path27" style="fill:#3459e6;fill-opacity:1" /> </g> <g clip-path="url(#a5fa93ec79)" id="g28" transform="translate(-93.455765,-108.41905)"> <path fill="#2f93ff" d="m 128.76172,188.81641 c 0,0 50.67187,-6.84375 85.36719,-52.85157 l -11.30469,-7.40625 34.30859,-12.08593 v 36.17187 l -9.35547,-8.10547 c 0,0 -42.49609,48.01172 -99.01562,44.27735 z m 0,0" fill-opacity="1" fill-rule="nonzero" id="path28" /> </g> <g clip-path="url(#d937094b42)" id="g30" transform="translate(-93.455765,-108.41905)"> <g clip-path="url(#384730fc70)" id="g29"> <path fill="#ffffff" d="m 199.18359,109.50781 h 59.85938 V 127 h -59.85938 z m 0,0" fill-opacity="1" fill-rule="nonzero" id="path29" /> </g> </g> <g clip-path="url(#2151049465)" id="g32" transform="translate(-93.455765,-108.41905)"> <g clip-path="url(#a9bb854531)" id="g31"> <path fill="#ffffff" d="m 115.70313,172.35547 h 67.22656 v 20.48828 h -67.22656 z m 0,0" fill-opacity="1" fill-rule="nonzero" id="path30" /> </g> </g> <g clip-path="url(#f0d3ff19d1)" id="g34" transform="translate(-93.455765,-108.41905)"> <g clip-path="url(#c1458e90a1)" id="g33"> <path fill="#ffffff" d="m 149.32812,165.10547 h 59.85938 v 17.49609 h -59.85938 z m 0,0" fill-opacity="1" fill-rule="nonzero" id="path32" /> </g> </g> <g clip-path="url(#b251c9648c)" id="g36" transform="translate(-93.455765,-108.41905)"> <g clip-path="url(#ea9f4fdd41)" id="g35"> <path fill="#ffffff" d="m 171.66797,155.85547 h 74.1875 v 12.73047 h -74.1875 z m 0,0" fill-opacity="1" fill-rule="nonzero" id="path34" /> </g> </g> <g clip-path="url(#6f07b6a28f)" id="g38" transform="translate(-93.455765,-108.41905)"> <g clip-path="url(#7e48455ce7)" id="g37"> <path fill="#ffffff" d="m 182.95312,135.36719 h 67.22657 v 20.48828 h -67.22657 z m 0,0" fill-opacity="1" fill-rule="nonzero" id="path36" /> </g> </g> <g clip-path="url(#c41ff71526)" id="g40" transform="translate(-93.455765,-108.41905)"> <g clip-path="url(#82558e6086)" id="g39"> <path fill="#ffffff" d="m 191.79687,118.25391 h 67.22657 v 20.48828 h -67.22657 z m 0,0" fill-opacity="1" fill-rule="nonzero" id="path38" /> </g> </g> <g clip-path="url(#45f7f2125f)" id="g44" transform="translate(-93.455765,-108.41905)"> <g clip-path="url(#b9c754249b)" id="g43"> <g clip-path="url(#eb39837003)" id="g42"> <g clip-path="url(#a9e2aeb642)" id="g41"> <path fill="#000000" d="m 240.69141,113.69922 c 2.5039,-1.13281 4.89453,-3.61328 6.91015,-1.67188 4.75781,4.58594 -11.44922,27.08203 -12.16015,27.81641 l 7.90234,20.19922 c 0.65234,1.51953 0.30859,2.42969 -0.3125,3.25 l -1.85547,2.29297 -9.88281,-9.52344 -7.64844,0.60547 c -0.44141,0.46094 -2.55859,3.5664 -7.87109,9.07812 -6.19922,6.4375 -8.15625,7.92188 -8.60157,8.37891 l 2.40625,3.73437 c 0.46094,0.625 -0.77343,2.44922 -1.40234,2.3711 l -7.58594,-0.92188 c -0.61718,0.64063 -2.39453,2.1211 -2.94531,1.58985 -0.73047,-0.70313 -0.73828,-1.24219 -0.56641,-1.78516 l -13.23437,0.72266 c -0.89844,0.0156 -0.21875,-2.51953 1.92578,-3.28516 l 9.76172,-3.71484 -5.75391,-4.65625 1.23438,-1.82422 c 0.4414,-0.64063 2.41797,-1.04297 3.13281,-1.0586 l 9.73438,0.15625 6.41796,-9.77343 -7.65625,0.0742 -28.80078,7.16796 0.31641,-2.70703 c 0,0 -0.0117,-0.72265 1.22656,-2.00781 l 48.55078,-22.53516 8.70313,-13.24609 c 0.35156,-0.54687 1.11328,-3.53515 3.32812,-5.83594 2.39453,-2.48046 2.84766,-2.04296 4.72657,-2.89453" fill-opacity="1" fill-rule="nonzero" id="path40" /> </g> </g> </g> </g> <g fill="#000000" fill-opacity="1" id="g47" transform="translate(-93.455765,-108.41905)"> <g transform="translate(96.799802,272.73552)" id="g46"> <g id="g45"> <path d="m 15.117188,-3.972656 h -7.8125 c -0.46875,0 -0.84375,-0.066406 -1.15625,-0.15625 -0.289063,-0.109375 -0.488282,-0.265625 -0.664063,-0.488282 -0.179687,-0.246093 -0.3125,-0.578124 -0.378906,-1 -0.023438,-0.109374 -0.023438,-0.265624 -0.042969,-0.375 0,0 0.019531,-1.601562 0.042969,-1.601562 h 9.925781 c 0.175781,0 0.621094,-0.085938 0.621094,-0.777344 V -10.125 c 0,-0.6875 -0.445313,-0.753906 -0.621094,-0.753906 l -11.457031,0.02344 C 2.929688,-10.8125 2.375,-10.476562 2.066406,-9.921875 1.953125,-9.746094 1.863281,-9.566406 1.820312,-9.367188 l -0.042968,2.796876 v 0.109374 c 0.019531,1.042969 0.132812,1.933594 0.289062,2.664063 0.199219,0.890625 0.53125,1.621094 0.953125,2.175781 0.445313,0.578125 1.019531,0.976563 1.730469,1.222656 0.6875,0.265626 1.511719,0.3750005 2.488281,0.3750005 h 7.878907 c 0.199218,0 0.644531,-0.0664063 0.644531,-0.7539065 V -3.21875 c 0,-0.6875 -0.445313,-0.753906 -0.644531,-0.753906 z m 0.02344,-14.363282 H 2.375 c -0.175781,0 -0.597656,0.08594 -0.597656,0.796876 v 1.734374 c 0,0.6875 0.421875,0.753907 0.597656,0.753907 l 12.765625,0.01953 c 0.175781,0 0.621094,-0.08594 0.621094,-0.773438 v -1.753906 c 0,-0.691406 -0.445313,-0.777344 -0.621094,-0.777344 z m 0,0" id="path44" /> </g> </g> </g> <g fill="#000000" fill-opacity="1" id="g50" transform="translate(-93.455765,-108.41905)"> <g transform="translate(115.44384,272.73552)" id="g49"> <g id="g48"> <path d="M 14.585938,-3.285156 H 7.371094 c -0.46875,0 -0.84375,-0.042969 -1.15625,-0.15625 C 5.949219,-3.53125 5.726562,-3.683594 5.570312,-3.929688 5.394531,-4.171875 5.261719,-4.507812 5.195312,-4.90625 c -0.089843,-0.445312 -0.113281,-1 -0.113281,-1.664062 v -10.945313 c 0,-0.710937 -0.441406,-0.777344 -0.621093,-0.777344 H 2.417969 c -0.199219,0 -0.640625,0.06641 -0.640625,0.777344 v 10.566406 c 0,1.242188 0.109375,2.308594 0.308594,3.175781 0.199218,0.886719 0.511718,1.621094 0.957031,2.175782 0.441406,0.578125 1.019531,1 1.730469,1.242187 0.664062,0.246094 1.507812,0.3789065 2.484374,0.3789065 h 7.328126 c 0.199218,0 0.621093,-0.0898437 0.621093,-0.7773435 v -1.753906 c 0,-0.6875 -0.421875,-0.777344 -0.621093,-0.777344 z m 0,0" id="path47" /> </g> </g> </g> <g fill="#000000" fill-opacity="1" id="g53" transform="translate(-93.455765,-108.41905)"> <g transform="translate(133.53299,272.73552)" id="g52"> <g id="g51"> <path d="m 15.117188,-3.972656 h -7.8125 c -0.46875,0 -0.84375,-0.066406 -1.15625,-0.15625 -0.289063,-0.109375 -0.488282,-0.265625 -0.664063,-0.488282 -0.179687,-0.246093 -0.3125,-0.578124 -0.378906,-1 -0.023438,-0.109374 -0.023438,-0.265624 -0.042969,-0.375 0,0 0.019531,-1.601562 0.042969,-1.601562 h 9.925781 c 0.175781,0 0.621094,-0.085938 0.621094,-0.777344 V -10.125 c 0,-0.6875 -0.445313,-0.753906 -0.621094,-0.753906 l -11.457031,0.02344 C 2.929688,-10.8125 2.375,-10.476562 2.066406,-9.921875 1.953125,-9.746094 1.863281,-9.566406 1.820312,-9.367188 l -0.042968,2.796876 v 0.109374 c 0.019531,1.042969 0.132812,1.933594 0.289062,2.664063 0.199219,0.890625 0.53125,1.621094 0.953125,2.175781 0.445313,0.578125 1.019531,0.976563 1.730469,1.222656 0.6875,0.265626 1.511719,0.3750005 2.488281,0.3750005 h 7.878907 c 0.199218,0 0.644531,-0.0664063 0.644531,-0.7539065 V -3.21875 c 0,-0.6875 -0.445313,-0.753906 -0.644531,-0.753906 z m 0.02344,-14.363282 H 2.375 c -0.175781,0 -0.597656,0.08594 -0.597656,0.796876 v 1.734374 c 0,0.6875 0.421875,0.753907 0.597656,0.753907 l 12.765625,0.01953 c 0.175781,0 0.621094,-0.08594 0.621094,-0.773438 v -1.753906 c 0,-0.691406 -0.445313,-0.777344 -0.621094,-0.777344 z m 0,0" id="path50" /> </g> </g> </g> <g fill="#000000" fill-opacity="1" id="g56" transform="translate(-93.455765,-108.41905)"> <g transform="translate(152.17703,272.73552)" id="g55"> <g id="g54"> <path d="M 15.339844,-18.292969 H 7.257812 c -0.976562,0 -1.820312,0.132813 -2.507812,0.378907 -0.710938,0.265624 -1.285156,0.6875 -1.707031,1.242187 -0.445313,0.554687 -0.777344,1.289063 -0.976563,2.175781 -0.203125,0.867188 -0.289062,1.929688 -0.289062,3.152344 v 4.394531 c 0,1.242188 0.085937,2.308594 0.289062,3.199219 0.199219,0.863281 0.53125,1.597656 0.976563,2.171875 0.441406,0.558594 1.019531,0.980469 1.707031,1.222656 0.6875,0.246094 1.53125,0.3789065 2.507812,0.3789065 h 8.082032 c 0.179687,0 0.621094,-0.0898437 0.621094,-0.7773435 v -1.753906 c 0,-0.6875 -0.441407,-0.777344 -0.621094,-0.777344 h -7.96875 c -0.46875,0 -0.867188,-0.042969 -1.15625,-0.15625 C 5.925781,-3.53125 5.726562,-3.683594 5.550781,-3.929688 5.371094,-4.152344 5.261719,-4.484375 5.171875,-4.90625 5.105469,-5.351562 5.0625,-5.90625 5.0625,-6.570312 v -5.171876 c 0,-0.667968 0.042969,-1.222656 0.109375,-1.644531 0.089844,-0.421875 0.199219,-0.734375 0.378906,-0.976562 0.175781,-0.246094 0.375,-0.398438 0.664063,-0.488281 0.289062,-0.109376 0.6875,-0.15625 1.15625,-0.15625 h 7.96875 c 0.179687,0 0.621094,-0.08984 0.621094,-0.796876 v -1.710937 c 0,-0.6875 -0.441407,-0.777344 -0.621094,-0.777344 z m 0,0" id="path53" /> </g> </g> </g> <g fill="#000000" fill-opacity="1" id="g59" transform="translate(-93.455765,-108.41905)"> <g transform="translate(171.02082,272.73552)" id="g58"> <g id="g57"> <path d="M 17.117188,-18.292969 H 2.417969 c -0.199219,0 -0.640625,0.06641 -0.640625,0.753907 v 1.734374 c 0,0.730469 0.441406,0.796876 0.640625,0.796876 H 8.125 V -0.753906 C 8.125,-0.0664062 8.570312,0 8.746094,0 h 2.042968 c 0.199219,0 0.621094,-0.0664062 0.621094,-0.753906 v -14.253906 h 5.707032 c 0.199218,0 0.644531,-0.06641 0.644531,-0.796876 v -1.734374 c 0,-0.6875 -0.445313,-0.753907 -0.644531,-0.753907 z m 0,0" id="path56" /> </g> </g> </g> <g fill="#000000" fill-opacity="1" id="g62" transform="translate(-93.455765,-108.41905)"> <g transform="translate(191.66243,272.73552)" id="g61"> <g id="g60"> <path d="m 16.917969,-12.988281 c 0,0.02344 0,0.04687 0,0.06641 0,0.02344 0,0.04687 0,0.06641 z m 0.421875,12.035156 -3.886719,-6.660156 c 1.085937,-0.132813 1.929687,-0.601563 2.488281,-1.355469 0.621094,-0.910156 0.953125,-2.21875 0.976563,-3.953125 -0.02344,-1.730469 -0.355469,-3.039063 -0.976563,-3.949219 -0.667968,-0.957031 -1.777344,-1.421875 -3.289062,-1.421875 H 2.417969 c -0.199219,0 -0.640625,0.06641 -0.640625,0.777344 v 1.753906 c 0,0.6875 0.441406,0.753907 0.640625,0.753907 h 9.660156 c 0.574219,0 0.953125,0.15625 1.175781,0.488281 0.242188,0.332031 0.355469,0.867187 0.355469,1.597656 0,0.734375 -0.113281,1.265625 -0.355469,1.601563 -0.222656,0.332031 -0.601562,0.488281 -1.175781,0.488281 H 2.417969 c -0.199219,0 -0.640625,0.06641 -0.640625,0.753906 v 9.324219 c 0,0.6874998 0.441406,0.7773435 0.640625,0.7773435 h 2.023437 c 0.199219,0 0.621094,-0.0898437 0.621094,-0.7773435 v -6.792969 h 4.683594 l 4.019531,7.125 c 0.08594,0.132813 0.152344,0.246094 0.242187,0.3125 0.113282,0.0859375 0.265626,0.1328125 0.464844,0.1328125 h 2.445313 c 0.265625,0 0.464843,-0.1796875 0.507812,-0.4453125 0.02344,-0.222656 0,-0.398437 -0.08594,-0.53125 z m 0,0" id="path59" /> </g> </g> </g> <g fill="#000000" fill-opacity="1" id="g65" transform="translate(-93.455765,-108.41905)"> <g transform="translate(211.9933,272.73552)" id="g64"> <g id="g63"> <path d="M 4.441406,-18.292969 H 2.398438 c -0.179688,0 -0.621094,0.08984 -0.621094,0.777344 v 16.761719 c 0,0.6874998 0.441406,0.7773435 0.621094,0.7773435 h 2.042968 c 0.175782,0 0.621094,-0.0898437 0.621094,-0.7773435 v -16.761719 c 0,-0.6875 -0.445312,-0.777344 -0.621094,-0.777344 z m 0,0" id="path62" /> </g> </g> </g> <g fill="#000000" fill-opacity="1" id="g68" transform="translate(-93.455765,-108.41905)"> <g transform="translate(219.93921,272.73552)" id="g67"> <g id="g66"> <path d="M 15.140625,-18.292969 H 2.375 c -0.175781,0 -0.597656,0.08984 -0.597656,0.800781 v 1.707032 c 0,0.6875 0.421875,0.777344 0.597656,0.777344 h 12.765625 c 0.175781,0 0.621094,-0.06641 0.621094,-0.753907 v -1.753906 c 0,-0.710937 -0.445313,-0.777344 -0.621094,-0.777344 z m -0.109375,7.4375 -11.457031,0.02344 c -0.644531,0.04297 -1.199219,0.398437 -1.53125,0.929687 -0.089844,0.179688 -0.179688,0.378906 -0.222657,0.578125 l -0.042968,8.570313 c 0,0.6874998 0.441406,0.7773435 0.621094,0.7773435 h 2.042968 c 0.175782,0 0.621094,-0.0898437 0.621094,-0.7773435 0,0 0.019531,-6.816406 0.042969,-6.816406 h 9.925781 c 0.175781,0 0.621094,-0.066407 0.621094,-0.753907 v -1.753906 c 0,-0.6875 -0.445313,-0.777344 -0.621094,-0.777344 z m 0,0" id="path65" /> </g> </g> </g> <g fill="#000000" fill-opacity="1" id="g71" transform="translate(-93.455765,-108.41905)"> <g transform="translate(238.58324,272.73552)" id="g70"> <g id="g69"> <path d="M 14.585938,-3.285156 H 7.371094 c -0.46875,0 -0.84375,-0.042969 -1.15625,-0.15625 C 5.949219,-3.53125 5.726562,-3.683594 5.570312,-3.929688 5.394531,-4.171875 5.261719,-4.507812 5.195312,-4.90625 c -0.089843,-0.445312 -0.113281,-1 -0.113281,-1.664062 v -10.945313 c 0,-0.710937 -0.441406,-0.777344 -0.621093,-0.777344 H 2.417969 c -0.199219,0 -0.640625,0.06641 -0.640625,0.777344 v 10.566406 c 0,1.242188 0.109375,2.308594 0.308594,3.175781 0.199218,0.886719 0.511718,1.621094 0.957031,2.175782 0.441406,0.578125 1.019531,1 1.730469,1.242187 0.664062,0.246094 1.507812,0.3789065 2.484374,0.3789065 h 7.328126 c 0.199218,0 0.621093,-0.0898437 0.621093,-0.7773435 v -1.753906 c 0,-0.6875 -0.421875,-0.777344 -0.621093,-0.777344 z m 0,0" id="path68" /> </g> </g> </g> <g fill="#000000" fill-opacity="1" id="g74" transform="translate(-93.455765,-108.41905)"> <g transform="translate(256.67239,272.73552)" id="g73"> <g id="g72"> <path d="m 18.203125,-18.292969 h -2.464844 c -0.199219,0 -0.464843,0.06641 -0.640625,0.398438 l -4.886718,8.902343 -4.839844,-8.878906 c -0.175782,-0.355468 -0.441406,-0.421875 -0.640625,-0.421875 h -2.53125 c -0.203125,0 -0.355469,0.109375 -0.402344,0.3125 -0.042969,0.152344 -0.019531,0.332031 0.066406,0.488281 l 6.660157,11.875 v 4.863282 C 8.523438,-0.0664062 8.96875,0 9.144531,0 H 11.1875 c 0.179688,0 0.621094,-0.0664062 0.621094,-0.753906 v -4.863282 l 6.726562,-11.875 c 0.08984,-0.15625 0.113282,-0.335937 0.07031,-0.511718 -0.07031,-0.179688 -0.222657,-0.289063 -0.402344,-0.289063 z m 0,0" id="path71" /> </g> </g> </g> </svg>                                   </div>
                                  """))                      
                        ),
              ui.column(7, 
                        div(HTML("""
                                <p>
                                  Electric planes offer a promising alternative to traditional gas-powered aircraft. 
                                  However, e-planes bring on new challenges including limited battery capacity and scarce 
                                  knowledge of their performance in Canadian weather. 
                                </p> 
                                <br>
                                <p>
                                  Our team is using data from the Pipistrel Velis Electro, the world’s first type certified 
                                  electric plane. Our platform enables researchers to analyze flight data and create a battery 
                                  management strategy for the optimal operation of the electric plane. Leveraging machine learning,
                                  ElectriFly optimizes flight schedules based on weather forecasts and improves flight planning by
                                  predicting battery consumption.
                                </p>

                                """))
                        
                        ),
              ui.column(1),
            ),
          ),
          ui.div(
            ui.row(
              ui.column(3,
                div(HTML(f"""<h4 style="font-weight: bolder; color: {grey}; text-align: center;">Our Supporters</h4>"""))
              ),
              ui.column(3, ui.output_image("uw_logo", width="70%", height="70%"), style="display: flex; flex-direction: column; align-items: center; padding: 1rem 0;"),
              ui.column(3, ui.output_image("wisa_logo", width="90%", height="90%"), style="display: flex; flex-direction: column; align-items: center; padding: 1rem 0; margin-bottom: 1rem;"),   
              ui.column(3, ui.output_image("wwfc_logo", width="53%", height="53%"), style="display: flex; flex-direction: column; align-items: center; padding: 1rem 0; margin-bottom: 2rem;"),
              style="align-items: center; padding: 2rem 0;"                       
            ),
          ),
          div(HTML(f"""
                    <div style="display: flex; align-items: center; justify-content: center; padding-bottom: 1rem; padding-top: 1rem;">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512" style="width: 50px; height: auto; margin-right: 15px;">
                        <!--!Font Awesome Free 6.5.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2024 Fonticons, Inc.-->
                        <path d="M308.5 135.3c7.1-6.3 9.9-16.2 6.2-25c-2.3-5.3-4.8-10.5-7.6-15.5L304 89.4c-3-5-6.3-9.9-9.8-14.6c-5.7-7.6-15.7-10.1-24.7-7.1l-28.2 9.3c-10.7-8.8-23-16-36.2-20.9L199 27.1c-1.9-9.3-9.1-16.7-18.5-17.8C173.9 8.4 167.2 8 160.4 8h-.7c-6.8 0-13.5 .4-20.1 1.2c-9.4 1.1-16.6 8.6-18.5 17.8L115 56.1c-13.3 5-25.5 12.1-36.2 20.9L50.5 67.8c-9-3-19-.5-24.7 7.1c-3.5 4.7-6.8 9.6-9.9 14.6l-3 5.3c-2.8 5-5.3 10.2-7.6 15.6c-3.7 8.7-.9 18.6 6.2 25l22.2 19.8C32.6 161.9 32 168.9 32 176s.6 14.1 1.7 20.9L11.5 216.7c-7.1 6.3-9.9 16.2-6.2 25c2.3 5.3 4.8 10.5 7.6 15.6l3 5.2c3 5.1 6.3 9.9 9.9 14.6c5.7 7.6 15.7 10.1 24.7 7.1l28.2-9.3c10.7 8.8 23 16 36.2 20.9l6.1 29.1c1.9 9.3 9.1 16.7 18.5 17.8c6.7 .8 13.5 1.2 20.4 1.2s13.7-.4 20.4-1.2c9.4-1.1 16.6-8.6 18.5-17.8l6.1-29.1c13.3-5 25.5-12.1 36.2-20.9l28.2 9.3c9 3 19 .5 24.7-7.1c3.5-4.7 6.8-9.5 9.8-14.6l3.1-5.4c2.8-5 5.3-10.2 7.6-15.5c3.7-8.7 .9-18.6-6.2-25l-22.2-19.8c1.1-6.8 1.7-13.8 1.7-20.9s-.6-14.1-1.7-20.9l22.2-19.8zM112 176a48 48 0 1 1 96 0 48 48 0 1 1 -96 0zM504.7 500.5c6.3 7.1 16.2 9.9 25 6.2c5.3-2.3 10.5-4.8 15.5-7.6l5.4-3.1c5-3 9.9-6.3 14.6-9.8c7.6-5.7 10.1-15.7 7.1-24.7l-9.3-28.2c8.8-10.7 16-23 20.9-36.2l29.1-6.1c9.3-1.9 16.7-9.1 17.8-18.5c.8-6.7 1.2-13.5 1.2-20.4s-.4-13.7-1.2-20.4c-1.1-9.4-8.6-16.6-17.8-18.5L583.9 307c-5-13.3-12.1-25.5-20.9-36.2l9.3-28.2c3-9 .5-19-7.1-24.7c-4.7-3.5-9.6-6.8-14.6-9.9l-5.3-3c-5-2.8-10.2-5.3-15.6-7.6c-8.7-3.7-18.6-.9-25 6.2l-19.8 22.2c-6.8-1.1-13.8-1.7-20.9-1.7s-14.1 .6-20.9 1.7l-19.8-22.2c-6.3-7.1-16.2-9.9-25-6.2c-5.3 2.3-10.5 4.8-15.6 7.6l-5.2 3c-5.1 3-9.9 6.3-14.6 9.9c-7.6 5.7-10.1 15.7-7.1 24.7l9.3 28.2c-8.8 10.7-16 23-20.9 36.2L315.1 313c-9.3 1.9-16.7 9.1-17.8 18.5c-.8 6.7-1.2 13.5-1.2 20.4s.4 13.7 1.2 20.4c1.1 9.4 8.6 16.6 17.8 18.5l29.1 6.1c5 13.3 12.1 25.5 20.9 36.2l-9.3 28.2c-3 9-.5 19 7.1 24.7c4.7 3.5 9.5 6.8 14.6 9.8l5.4 3.1c5 2.8 10.2 5.3 15.5 7.6c8.7 3.7 18.6 .9 25-6.2l19.8-22.2c6.8 1.1 13.8 1.7 20.9 1.7s14.1-.6 20.9-1.7l19.8 22.2zM464 304a48 48 0 1 1 0 96 48 48 0 1 1 0-96z"/>
                      </svg>
                      <h2 style="font-weight: bolder;">How does it <span style="color: {blue};">work?</span></h2>
                    </div>
                    """)
          ),
          div(HTML(f"""
                    <div style="display: flex; align-items: center; justify-content: center; padding: 0.5rem 0; background-color: {light_grey}; margin: 0 -2rem;">
                      <h2 style="font-weight: bolder; color: {blue};">Researchers</h2>
                    </div>
                    """)
          ),
          ui.div(
            ui.row(
              ui.column(6, 
                        ui.output_image("visualization_img", width="100%", height="100%"), 
                        ui.div(HTML(f"""
                                      <br>
                                      <p style="font-weight: bold">Data Visualizations</p>
                                      <p style="padding: 0 8rem;">Gain comprehensive insights into plane and battery behaviours</p>
                                    """)),
                        style="display: flex; flex-direction: column; align-items: center; text-align: center;"
                        ),
              ui.column(6, 
                        ui.output_image("custom_graph_img", width="100%", height="100%"), 
                        ui.div(HTML(f"""
                                      <br>
                                      <p style="font-weight: bold">Custom Graphs</p>
                                      <p style="padding: 0 8rem;">Develop your own graphs and plot any variable including flight and weather data</p>
                                    """)),
                        style="display: flex; flex-direction: column; align-items: center; text-align: center;"
                        ),
              style="align-items: center; padding: 2rem 0;"                       
            ),
          ),
          ui.div(
            ui.row(
              ui.column(6, 
                        ui.output_image("data_preview_img", width="100%", height="100%"), 
                        ui.div(HTML(f"""
                                      <br>
                                      <p style="font-weight: bold">Data Preview</p>
                                      <p style="padding: 0 8rem;">Preview data at a glance of the most recent flight to ensure all data was uploaded correctly</p>
                                    """)),
                        style="display: flex; flex-direction: column; align-items: center; text-align: center;"
                        ),
              ui.column(6, 
                        ui.output_image("stat_insights_img", width="100%", height="100%"), 
                        ui.div(HTML(f"""
                                      <br>
                                      <p style="font-weight: bold">Statistical Insights</p>
                                      <p style="padding: 0 8rem;">Unlock valuable statistical insights to enhance flight operations efficiency</p>
                                    """)),
                        style="display: flex; flex-direction: column; align-items: center; text-align: center;"
                        ),
              style="align-items: center; padding: 2rem 0;"                       
            ),
          ),
          div(HTML("<br><br>")),
          div(HTML(f"""
                    <div style="display: flex; align-items: center; justify-content: center; padding: 0.5rem 0; background-color: {light_grey}; margin: 0 -2rem;">
                      <h2 style="font-weight: bolder; color: {blue};">Pilots</h2>
                    </div>
                    """)
          ),
          ui.div(
            ui.row(
              ui.column(6, 
                        ui.output_image("scheduling_img", width="100%", height="100%"), 
                        ui.div(HTML(f"""
                                      <br>
                                      <p style="font-weight: bold">Flight Schedule</p>
                                      <p style="padding: 0 8rem;">Determine the optimal flight times based on a simulation model derived from local weather forecasts</p>
                                    """)),
                        style="display: flex; flex-direction: column; align-items: center; text-align: center;"
                        ),
              ui.column(6, 
                        ui.output_image("planning_img", width="100%", height="100%"), 
                        ui.div(HTML(f"""
                                      <br>
                                      <p style="font-weight: bold">Flight Exercise Planning</p>
                                      <p style="padding: 0 8rem;">Empower pilots’ confidence during flight by planning what exercises can be performed in the air</p>
                                    """)),
                        style="display: flex; flex-direction: column; align-items: center; text-align: center;"
                        ),
              style="align-items: center; padding: 2rem 0;"                       
            ),
          ),
          div(HTML(f"""
                    <div style="display: flex; align-items: center; justify-content: center; padding-top: 4rem; padding-bottom: 1rem">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512" style="width: 50px; height: auto; margin-right: 15px;">
                        <!--!Font Awesome Free 6.5.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2024 Fonticons, Inc.-->
                          <path d="M72 88a56 56 0 1 1 112 0A56 56 0 1 1 72 88zM64 245.7C54 256.9 48 271.8 48 288s6 31.1 16 42.3V245.7zm144.4-49.3C178.7 222.7 160 261.2 160 304c0 34.3 12 65.8 32 90.5V416c0 17.7-14.3 32-32 32H96c-17.7 0-32-14.3-32-32V389.2C26.2 371.2 0 332.7 0 288c0-61.9 50.1-112 112-112h32c24 0 46.2 7.5 64.4 20.3zM448 416V394.5c20-24.7 32-56.2 32-90.5c0-42.8-18.7-81.3-48.4-107.7C449.8 183.5 472 176 496 176h32c61.9 0 112 50.1 112 112c0 44.7-26.2 83.2-64 101.2V416c0 17.7-14.3 32-32 32H480c-17.7 0-32-14.3-32-32zm8-328a56 56 0 1 1 112 0A56 56 0 1 1 456 88zM576 245.7v84.7c10-11.3 16-26.1 16-42.3s-6-31.1-16-42.3zM320 32a64 64 0 1 1 0 128 64 64 0 1 1 0-128zM240 304c0 16.2 6 31 16 42.3V261.7c-10 11.3-16 26.1-16 42.3zm144-42.3v84.7c10-11.3 16-26.1 16-42.3s-6-31.1-16-42.3zM448 304c0 44.7-26.2 83.2-64 101.2V448c0 17.7-14.3 32-32 32H288c-17.7 0-32-14.3-32-32V405.2c-37.8-18-64-56.5-64-101.2c0-61.9 50.1-112 112-112h32c61.9 0 112 50.1 112 112z"/>
                      </svg>
                      <h2 style="font-weight: bolder;">Meet the <span style="color: {blue};">team</span></h2>
                    </div>
                    """)
          ),
          ui.div(ui.output_image("team_img", width="100%", height="100%"), 
            style="margin: 0 -2rem;",   
          ),
          ui.div(HTML(f"""<i style="display: flex; align-items: center; justify-content: center; padding-top: 1rem;">Left to Right: Nayeema Nonta, Vikram Bhatt, Meenakshi Andoorveedu, Peter Twarecki, Joanna Yang</i>""")
          ),
          div(HTML("""
                    <p>
                      ElectriFly emerges from the visionary collaboration of five driven Management Engineering Students,
                      whose shared passion for aviation fuels their pursuit of excellence in electric flight. With a profound 
                      belief in the transformative potential of electric aviation within Canadian airspace, this dynamic team 
                      combines their diverse expertise and unwavering dedication to shape the future of flight.
                    </p> 
                    <br>
                    <p>
                      Their journey is marked by meticulous validation, as ElectriFly undergoes rigorous testing through pilot
                      programs and consultation with esteemed subject matter experts. This commitment to thorough validation 
                      ensures that ElectriFly stands at the forefront of innovation, ready to propel electric aviation to new 
                      heights with confidence and precision.
                    </p>
                    """), 
                style="display: flex; flex-direction: column; align-items: center; padding: 3rem 2rem;"
          ),
        ),
        # ===============================================================================================================================================================
        # END: HOMEPAGE
        # ===============================================================================================================================================================
        # ===============================================================================================================================================================
        # START: DATA PREVIEW SCREEN
        # ===============================================================================================================================================================
        ui.nav_panel("Data Preview",
            div(HTML("<h2> Data Preview </h2>")),
            div(HTML("<hr>")),
            ui.card(
                ui.card_header("Welcome to ElectriFly's Data Preview Interface!", style="background-color: #3459e6; color: white; text-align: left;"),
                # div(HTML(f"""<h4 style="font-weight: bolder; color: {blue}; background:{blue}; text-align: center;">Our Supporters</h4>""")),
                ui.p("Easily tailor your data viewing experience to suit your needs. Handpick the columns you want to see and effortlessly remove any you don't need by simply tapping the 'x' button. Dive into the lastest flight and weather data seamlessly!"), min_height="130px"
            ), 
            div(HTML("<hr>")),
            # Column selection panel
            ui.div(
                ui.include_css("bootstrap.css"), ui.h3("Most Recent Flight and Weather Data Records"), 
                style="margin-top:20px;"
            ), 
            ui.p("          "), 
            ui.output_ui("most_recent_run"),
            ui.p("          "), 
            ui.accordion(
                ui.accordion_panel(
                    "Filters",
                    ui.layout_columns(
                        ui.input_selectize("data_granularity", "Select Data Granularity", choices=["Granular", "Aggregate"], selected="Granular"),
                        ui.input_selectize("data_type_selection", "Select Data Type", choices=["Flight test", "Charging", "Ground test"], multiple=False, selected="Flight test"),
                        ui.output_ui("data_type_dates"),
                        ui.input_selectize("total_data_show", "Select Data Preview Limit", choices=[10, 20, 30], multiple=False, selected=10),
                        col_widths=[3, 3, 3, 3]
                    ),
                    ui.output_ui("flight_preview_columns_choice"),
                    ui.p("          "),
                    ui.input_selectize("weather_cols", "Select Weather Data Columns", choices=custom_weather_variables, multiple=True, selected=custom_weather_variables[:5], width="100%"),
                    ui.layout_columns(
                        ui.p("          "),
                        ui.input_action_button("filter_data", "Apply Filters", style="background-color: #3459e6; color: white; border: 1px solid #FFFFFF; cursor: pointer; padding: 17px"),
                        col_widths=(9, 3)
                    )
                )
            ),
            ui.p("          "),   
            ui.div(
                ui.output_data_frame("preview_dataframe_construct"),
                ui.include_css("bootstrap.css"),
                style="margin-top: 2px; max-height: 3000px;"
            ),
            ui.layout_columns(
                div(HTML(f"""<p style="font-weight: bold; font-size: 20px; padding: 10px;">Select the <span style="color: {blue};">Download</span> button to download the data
                        based on the selected <span style="color: {blue};">granularity</span>, <span style="color: {blue};">data type</span>, and <span style="color: {blue};">date</span>.</p>""")),
                ui.download_button("downloadData", "Download", width="100%", style="background-color: #3459e6; color: white; border: 1px solid #FFFFFF; cursor: pointer; padding: 17px"),
                col_widths=(9, 3)
            )
        ),
        # ===============================================================================================================================================================
        # END: DATA PREVIEW SCREEN
        # ===============================================================================================================================================================
        # ===============================================================================================================================================================
        # START: DATA ANALYSIS SCREEN
        # ===============================================================================================================================================================
        ui.nav_menu("Data Analysis",                    
            # ===============================================================================================================================================================
            # START: Recommended Graphs Tab
            # ===============================================================================================================================================================
            ui.nav_panel("Data Visualization", 
                div(HTML("<h2> Data Visualization </h2>")),
                div(HTML("<hr>")),
                ui.card(
                    ui.card_header("Welcome to ElectriFly's Data Visualization Interface!", style="background-color: #3459e6; color: white; text-align: left;"),
                    ui.p("Unlock the power of your data with our intuitive and powerful user interface designed specifically for data analytics. Select the flight dates that you’re interested in and our platform will transform raw data into actionable insights, enabling you to visualize trends and patterns."),
                    min_height = "150px"
                ), 
                div(HTML("<hr>")),
                div(HTML("<h4> Flight Graphs </h4>")),
                ui.layout_columns(
                    ui.input_selectize("singular_flight_date", "Choose Flight Date:", get_flights()),
                    col_widths=(3)
                ),
                ui.p("          "),
                ui.row(
                    ui.column(6,
                        ui.row(
                            ui.column(6,
                            ui.value_box(
                                "Number of circuits",
                                ui.output_text("num_circuits"),
                                showcase=fa.icon_svg("jet-fighter"),
                                min_height="150px"
                            ),),
                            ui.column(6,
                                ui.value_box(
                                "Aircraft Weight (lbs)",
                                ui.output_ui("total_weight"),
                                showcase=fa.icon_svg("weight-hanging"),
                                min_height="150px"
                            ),),

                        div(HTML("<hr>")),
                        ),
                        ui.card(
                            ui.card_header("Weather Data for Selected Flight"),
                            ui.output_table("weather_interactive", align='center'),
                            min_height="450px"
                        ),
                    ),
                    ui.column(6,
                        ui.card(
                            ui.card_header("Flight Map"),
                            ui.output_ui("map_output_variability"),
                            output_widget("lat_long_map"),
                            min_height="665px"
                        )
                    )
                ),  
                div(HTML("<hr>")),
                div(HTML("<h4> Time Graphs </h4>")),
                ui.layout_columns(
                    ui.input_selectize("multi_select_flight_dates", "Choose Flight Date(s):", get_flights(), multiple=True),
                    col_widths=(3)
                ),
                ui.p("          "),
                ui.layout_columns(
                    ui.card(
                        ui.card_header("Multi-Flight SOC vs. Time"),
                        ui.panel_absolute(
                            ui.output_plot(
                                "soc_time_graph",
                                height='90%',
                                width='100%'
                            ), 
                            left="0px",
                            top="10%",
                            width="100%",
                            height='100%',
                        ),
                        min_height="600px"
                    ),
                    ui.card(
                        ui.card_header("Multi-Flight Power Setting vs. Time"),
                        ui.panel_absolute(
                            ui.output_plot(
                                "power_time_graph",
                                height='90%',
                                width='100%'
                            ),
                            left="0px",
                            top="10%",
                            width="100%",
                            height='100%',
                        ),
                        min_height="600px"
                    ),
                    col_widths=(6, 6)
                ),  
            ),
            #  ===============================================================================================================================================================
            # START: CUSTOM GRAPH TAB
            # ===============================================================================================================================================================
            ui.nav_panel("Custom Graph",
                div(HTML("<h2> Custom Graph </h2>")),
                div(HTML("<hr>")),
                ui.card(
                    ui.card_header("Welcome to ElectriFly's Custom Graph Interface!", style="background-color: #3459e6; color: white; text-align: left;"),
                    ui.p("Ready to delve deeper into the data? We have you covered! Our custom graph tool empowers you to visualize and selectively explore the flight data that piques your interest, offering the flexibility to choose your preferred output mode—whether it's a dynamic scatterplot or a basic line plot."), min_height="130px"
                ), 
                div(HTML("<hr>")),
                ui.layout_columns(
                    ui.card(
                        ui.tooltip(
                            ui.input_selectize("select_flights", "Flight Date:", get_flights()), 
                            "Select the date for which you want to view the data."
                        ),
                        ui.tooltip(
                            ui.input_selectize("select_graph", "Graph Type:", ["Line Plot", "Scatter Plot"]), 
                            "Select the type of graph you want to see."
                        )
                    ),
                    ui.card(
                        ui.tooltip(
                            ui.input_selectize("select_x_variable", "Independent (X) Variable:", custom_aggregate_variables, selected=custom_aggregate_variables[1]),
                            "Select the X (independent) variable on the graph."
                        ),
                        ui.tooltip(
                            ui.input_selectize("select_y_variable", "Dependent (Y) Variable:", custom_aggregate_variables, selected=custom_aggregate_variables[4]),
                            "Lastly select the Y (dependent) variable on the graph."
                        )
                    ),
                    ui.card(
                        ui.panel_absolute(
                            ui.output_plot(
                                "custom_graph",
                                width="100%",
                                height='100%'
                            ),
                            left="2%",
                            top="2%",
                            width="95%",
                            height='100%',
                        ),
                        height='600px'
                    ),
                    col_widths=(2, 2, 8)
                )
            ),
            # ===============================================================================================================================================================
            # START: Statistical Insights TAB
            # ===============================================================================================================================================================
            ui.nav_panel("Statistical Insights", 
                div(HTML("<h2> Statistical Insights </h2>")),
                div(HTML("<hr>")),
                ui.card(
                    ui.card_header("Welcome to ElectriFly's Statistical Insights Interface!", style="background-color: #3459e6; color: white; text-align: left;"),
                    ui.p("Discover valuable insights into the heart of the e-plane — the battery. Explore how different aircraft maneuvers affect the battery’s state of charge through detailed statistical visualizations. Additionally, monitor the battery's health over time, enabling you to derive actionable insights and enhance your decision-making processes."), min_height="130px"
                ), 
                div(HTML("<hr>")),
                ui.input_selectize("statistical_time", "Choose Flight Date:", get_flights()),
                ui.p("          "),
                ui.row(
                    ui.column(6,
                        ui.input_selectize("select_activities", 
                            "Choose activities:", 
                            change_order(), 
                            selected=change_order(), 
                            width="500px",
                            multiple=True
                        ),
                        div(HTML("<hr>")),
                        ui.card(
                            ui.output_table("soc_roc_table"), 
                            max_height="450px"
                        ),
                    ),
                    ui.column(6,
                        ui.card(
                            ui.panel_absolute(
                                ui.output_plot(
                                    "power_soc_rate_of_change_scatter_plot",
                                    width="100%",
                                    height='100%'
                                ), 
                                width="95%",
                                height='100%',
                            ),
                            height='600px'
                        ),
                    )
                ),
                div(HTML("<h2> SOH Insights </h2>")),
                div(HTML("<hr>")),
                ui.input_selectize("statistical_multi_time", "Choose Flight Date(s):", get_flights(), multiple=True),
                ui.p("          "),
                ui.row(
                    ui.column(6,
                        ui.card(
                            ui.panel_absolute(
                                ui.output_plot(
                                    "soh_soc_rate_of_change_scatter_plot",
                                    width="100%",
                                    height='100%'
                                ), 
                                width="95%",
                                height='100%',
                            ),
                            height='600px'
                        ),
                    ),

                    ui.column(6,
                        ui.card(
                            ui.panel_absolute(
                                ui.output_plot(
                                    "soh_scatter_plot",
                                    width="100%",
                                    height='100%'
                                ), 
                                width="95%",
                                height='100%',
                            ),
                            height='600px'
                        ), 
                      )
                )
            ),
            #  ===============================================================================================================================================================
            # START: CHARGING GRAPHS TAB
            # ===============================================================================================================================================================
            ui.nav_panel("Charging Graph",
                div(HTML("<h2> Charging Graph </h2>")),
                div(HTML("<hr>")),
                ui.card(
                    ui.card_header("Welcome to ElectriFly's Charging Graph Interface!", style="background-color: #3459e6; color: white; text-align: left;"),
                    ui.p("Our charging graph tool enables you to visualize and selectively explore the charging data for all of the charging sessions."), min_height="130px"
                ), 
                div(HTML("<hr>")),
                ui.layout_columns(
                    ui.card(
                        ui.tooltip(
                            ui.input_selectize("select_charging", "Charging Date and Time:", get_charging_data(), multiple=True), 
                            "Select the date for which you want to view the data."
                        ),
                        ui.tooltip(
                            ui.input_selectize("select_charging_graph", "Graph Type:", ["Line Plot", "Scatter Plot"]), 
                            "Select the type of graph you want to see."
                        )
                    ),
                    ui.card(
                        ui.tooltip(
                            ui.input_selectize("select_x_charging_variable", "Independent (X) Variable:", charging_variables, selected=charging_variables[0]),
                            "Select the X (independent) variable on the graph."
                        ),
                        ui.tooltip(
                            ui.input_selectize("select_y_charging_variable", "Dependent (Y) Variable:", charging_variables, selected=charging_variables[3]),
                            "Lastly select the Y (dependent) variable on the graph."
                        )
                    ),
                    ui.card(
                        ui.panel_absolute(
                            ui.output_plot(
                                "charging_graph",
                                width="100%",
                                height='100%'
                            ),
                            left="2%",
                            top="2%",
                            width="95%",
                            height='100%',
                        ),
                        height='600px'
                    ),
                    col_widths=(2, 2, 8)
                )
            ),
        ),
        # ===============================================================================================================================================================
        # END: DATA ANALYSIS SCREEN
        # ===============================================================================================================================================================
        # ===============================================================================================================================================================
        # START: FLIGHT PLANNING SCREEN
        # ===============================================================================================================================================================
        ui.nav_menu("Flight Planning",
            # ===============================================================================================================================================================
            # START: Flight Scheduling TAB
            # ===============================================================================================================================================================
            ui.nav_panel("Flight Scheduling",
                div(HTML("<h2> Flight Scheduling </h2>")),
                div(HTML("<hr>")),
                ui.card(
                    ui.card_header("Welcome to ElectriFly's Flight Scheduling Interface!", style="background-color: #3459e6; color: white; text-align: left;"),
                    #ui.p
                        div(HTML("""<p>Discover the best flying times for the next 72 hours with our flight scheduling tool. Using Waterloo's forecasted weather data, our tool categorizes each time slot into green, yellow, and red zones, indicating safety levels for flight. Hover over times for detailed safety explanations to inform your flight planning decisions. Happy flying!</p>
                            
                            <p>🟩 = Safe for flight<br>
                            🟨 = Potentially safe for flight<br>
                            🟥 = Not safe for flight</p>
                            """))
                    ,min_height = "250px"
                ),
                ui.row( 
                    ui.column(6,
                        div(HTML("<hr>")),
                        div(HTML("<p><b>Three Day Flight Forecast</b></p>")),
                        div(HTML("<hr>")),
                        ui.output_table("simulation_table")
                    ),
                    ui.column(6,
                        div(HTML("<hr>")),
                        div(HTML("<p><b>Upcoming Flights for Today</b></p>")),
                        div(HTML("<hr>")),
                        ui.output_table("flight_planning_table", width="100%"),
                    ),
                ),
            ),
            # ===============================================================================================================================================================
            # START: Flight Exercise Planning TAB
            # ===============================================================================================================================================================
            ui.nav_panel("Flight Exercise Planning", 
                div(HTML("<h2> Flight Exercise Planning </h2>")),
                div(HTML("<hr>")),
                ui.card(
                    ui.card_header("Welcome to ElectriFly's Flight Exercise Planning Interface!", style="background-color: #3459e6; color: white; text-align: left;"),
                    div(HTML(f"""<p>Prepare your flight exercises with precision by customizing key attributes. Our innovative tool leverages a machine 
                                    learning prediction engine to estimate battery level (SOC) throughout each exercise, as well as the total battery consumption by the end of your 
                                    flight. Empower yourself with this data to make well-informed decisions for your flight planning.
                                </p>
                                <p>The tool enables pilots to choose <span style="color: {blue}; font-weight: bold">two input methods</span>. Changing the method is controlled 
                                    by the switch under the \'Flight Activity Selection\' section to the left. Additionally, the date and time enable the tool to query forecasted weather data.
                                </p>
                                <ol>
                                <li><span style="color: {blue}; font-weight: bold">Method 1:</span> Range attribute selection. Through the specified range, a random value is chosen as the prediction value for the prediction engine</li>
                                <li><span style="color: {blue}; font-weight: bold">Method 2:</span> Single attribute selection. For each attribute, a value is input. Which will be used as the prediction value for the prediction engine</li>
                                </ol>
                    """)),
                    min_height="130px"
                ), 
                div(HTML("<hr>")),  
                ui.p("          "), 
                # Selecting the date
                ui.row(
                    ui.column(3,
                        ui.accordion(
                            ui.accordion_panel(
                                "Flight Date & Time",
                                ui.input_selectize("date_operations", "Choose Flight Date:", get_dates(), multiple=False, selected=get_dates()[0]),
                                ui.p("          "),
                                ui.input_selectize(
                                    "flight_time_select", 
                                    "Choose start time of flight:", 
                                    ["12:00 AM", "12:15 AM", "12:30 AM", "12:45 AM", "01:00 AM", "01:15 AM", "01:30 AM", "01:45 AM", "02:00 AM", 
                                        "02:15 AM", "02:30 AM", "02:45 AM", "03:00 AM", "03:15 AM", "03:30 AM", "03:45 AM", "04:00 AM", "04:15 AM", 
                                        "04:30 AM", "04:45 AM", "05:00 AM", "05:15 AM", "05:30 AM", "05:45 AM", "06:00 AM", "06:15 AM", "06:30 AM", 
                                        "06:45 AM", "07:00 AM", "07:15 AM", "07:30 AM", "07:45 AM", "08:00 AM", "08:15 AM", "08:30 AM", "08:45 AM", 
                                        "09:00 AM", "09:15 AM", "09:30 AM", "09:45 AM", "10:00 AM", "10:15 AM", "10:30 AM", "10:45 AM", "11:00 AM", 
                                        "11:15 AM", "11:30 AM", "11:45 AM", "12:00 PM", "12:15 PM", "12:30 PM", "12:45 PM", "01:00 PM", "01:15 PM", 
                                        "01:30 PM", "01:45 PM", "02:00 PM", "02:15 PM", "02:30 PM", "02:45 PM", "03:00 PM", "03:15 PM", "03:30 PM", 
                                        "03:45 PM", "04:00 PM", "04:15 PM", "04:30 PM", "04:45 PM", "05:00 PM", "05:15 PM", "05:30 PM", "05:45 PM", 
                                        "06:00 PM", "06:15 PM", "06:30 PM", "06:45 PM", "07:00 PM", "07:15 PM", "07:30 PM", "07:45 PM", "08:00 PM", 
                                        "08:15 PM", "08:30 PM", "08:45 PM", "09:00 PM", "09:15 PM", "09:30 PM", "09:45 PM", "10:00 PM", "10:15 PM", 
                                        "10:30 PM", "10:45 PM", "11:00 PM", "11:15 PM", "11:30 PM", "11:45 PM"]
                                )
                            ),
                            ui.accordion_panel(
                                "Flight Activity Selection",
                                ui.input_switch("manual_model_input_switch", label="Single attribute selection", value=False),
                                ui.input_selectize(
                                    "flight_activities", 
                                    "Choose Flight Activity:", 
                                    change_order(), 
                                    multiple=False, 
                                    width=6),
                                ui.p("          "),
                                ui.output_ui("duration_of_activity"),
                                ui.p("          "),
                                ui.output_ui("power_setting_activity"),
                                ui.p("          "),
                                ui.output_ui("altitude_activity"),
                                ui.p("          "),
                                ui.output_ui("ground_speed_activity"),
                                ui.p("          "),
                                ui.output_ui("soh_activity"),
                            ),
                            id="prediction_model",  
                            open="Flight Date & Time", 
                        ),
                    ),
                    ui.column(9,
                        ui.row(
                            ui.column(8, ui.card(ui.output_ui("remaining_soc"), height="60px", style="background-color: #FFFFFF; border: 1px solid #DBDBDB; padding: 0px;")), 
                            ui.column(4,
                                ui.row( 
                                    ui.layout_columns(
                                        ui.tooltip(
                                            ui.input_action_button(
                                                "add_activity", 
                                                "Add activity", 
                                                style="background-color: #3459e6; color: white; border: 1px solid #DBDBDB; cursor: pointer; padding: 17px",
                                            ),
                                            "Add selected activity under the \'Flight Activity Selection\' setting"
                                        ),
                                        ui.tooltip(
                                            ui.input_action_button(
                                                "delete_selected_activity", 
                                                "Delete activity", 
                                                style="background-color: #e7e7e7; color: black; border: 1px solid #DBDBDB; cursor: pointer; padding: 17px",
                                            ),
                                            "Delete any single selected row in the table below."
                                        ),
                                        col_widths=(6, 6)
                                    ), 
                                ) 
                            )
                        ),
                        ui.p("          "),
                        ui.row(
                            ui.card(
                                ui.output_data_frame("model_predict_output"), 
                                height="660px",
                                style="background-color: #FFFFFF; border: 1px solid #DBDBDB;"  
                            )
                        )
                    ),
                    height="700px"
                )            
            )
        ),
        # ===============================================================================================================================================================
        # END: FLIGHT PLANNING SCREEN
        # ===============================================================================================================================================================
        id="tab",  
    )  
)

# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
def server(input: Inputs, output: Outputs, session: Session):
  
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # START: HOMEPAGE 
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------

    @render.image
    def velis_img(): return {"src": "app_images/velis.webp", "width": "65%", "style": "border-radius: 22px;"}

    @render.image
    def uw_logo(): return {"src": "app_images/uw.svg", "width": "100%", "height": "100%"}

    @render.image
    def wisa_logo(): return {"src": "app_images/wisa.svg", "width": "100%", "height": "100%"}

    @render.image
    def wwfc_logo(): return {"src": "app_images/wwfc.png", "width": "100%", "height": "100%"}

    @render.image
    def visualization_img(): return {"src": "app_images/visualization.png", "width": "100%", "height": "100%", "style": "border-radius: 22px; border: 1px solid #D0CFCF; box-shadow: 0 4px 4px rgba(0, 0, 0, 0.25);"}

    @render.image
    def custom_graph_img(): return {"src": "app_images/custom-graph.png", "width": "100%", "height": "100%", "style": "border-radius: 22px; border: 1px solid #D0CFCF; box-shadow: 0 4px 4px rgba(0, 0, 0, 0.25);"}

    @render.image
    def data_preview_img(): return {"src": "app_images/preview.png", "width": "100%", "height": "100%", "style": "border-radius: 22px; border: 1px solid #D0CFCF; box-shadow: 0 4px 4px rgba(0, 0, 0, 0.25);"}

    @render.image
    def stat_insights_img(): return {"src": "app_images/stats.png", "width": "100%", "height": "100%", "style": "border-radius: 22px; border: 1px solid #D0CFCF; box-shadow: 0 4px 4px rgba(0, 0, 0, 0.25);"}

    @render.image
    def scheduling_img(): return {"src": "app_images/scheduling.png", "width": "100%", "height": "100%", "style": "border-radius: 22px; border: 1px solid #D0CFCF; box-shadow: 0 4px 4px rgba(0, 0, 0, 0.25);"}

    @render.image
    def planning_img(): return {"src": "app_images/planning.png", "width": "100%", "height": "100%", "style": "border-radius: 22px; border: 1px solid #D0CFCF; box-shadow: 0 4px 4px rgba(0, 0, 0, 0.25);"}

    @render.image
    def team_img(): return {"src": "app_images/team.png", "width": "100%", "height": "100%"}

    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # END: HOMEPAGE 
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
  

    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # START: DATA ANALYSIS SCREEN 
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.ui
    def data_grid():
        # Placeholder for the actual data grid
        return ui.tags.div("Data grid will be here.")


    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    
    @output
    @render.table
    def weather_interactive(): 
        # Get the flight ID corresponding to the chosen date
        flight_id = input.singular_flight_date()
        weather_df = query_weather().get_weather_by_flight_id(flight_id)
        weather_df = weather_df.style.set_table_styles([
                            {'selector': 'tr', 'props': [('height', '50px')]}, # make row height taller
                            {'selector': 'tr', 'props': [('box-shadow', '1px 1px 4px rgba(0, 0, 0, 0.1)')]},  # Add shadow box effect
                            {'selector': 'td', 'props': [('width', '500px')]}, # Set table width
                            {'selector': 'td', 'props': [('text-align', 'center')]}, # Center align text in cells
                            {'selector': 'th', 'props': [('text-align', 'center')]},  # Center align column names
                        ]).hide(axis="index")

        return weather_df 

      
    # @output
    # @render.table
    # def weather_interactive(): 
    #     # Get the flight ID corresponding to the chosen date
    #     flight_id = input.singular_flight_date()
    #     weather_df = query_weather().get_weather_by_flight_id(flight_id)
        
    #     weather_df_styled = weather_df.style.applymap(format_except_first_col).set_table_styles([
    #                         {'selector': 'tr', 'props': [('height', '50px')]}, # make row height taller
    #                         {'selector': 'tr', 'props': [('box-shadow', '1px 1px 4px rgba(0, 0, 0, 0.1)')]},  # Add shadow box effect
    #                         {'selector': 'td', 'props': [('width', '450px')]}, # Set table width
    #                         {'selector': 'td', 'props': [('text-align', 'center')]}, # Center align text in cells
    #                         {'selector': 'th', 'props': [('text-align', 'center')]},  # Center align column names
    #                     ])
        
    #     def format_except_first_col(val, column):
    #         if column != weather_df.columns[0]:  # Check if the column is not the first column
    #             return '{:.1f}'.format(val)
    #         return val  # If it's the first column, return the value unchanged


    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.plot()
    def custom_graph():

        # Get all the inputs
        flight_id = input.select_flights()
        graph_type = input.select_graph()
        x_var_label = input.select_x_variable()
        y_var_label = input.select_y_variable()

        # Make sure the x_variables are shown
        if x_var_label != "":
            x_variables = custom_aggregate_variables_dict[x_var_label]
        else:
            x_variables = ""

        # Make sure the y_variables are shown
        if y_var_label != "":
            y_variables = custom_aggregate_variables_dict[y_var_label]
        else:
            y_variables = ""

        # Make the graph
        created_custom_graph = Graphing.custom_graph_creation(graph_type, flight_id, x_variables, y_variables, x_var_label, y_var_label)

        # Return the custom graph
        return created_custom_graph         


    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.plot(alt="An interactive plot")
    def soc_time_graph():
        """
        The function uses the input from the 'state' parameter to get data on soc vs time for all the selected dates.

        Returns 
            soc_graph: a matplotlib figure plot with the data plotted already.
        """
        # Get all flight data for interactive plot
        flight_ids = input.multi_select_flight_dates()

        # Graph the SOC
        soc_graph = Graphing.soc_graph(flight_ids)

        # Return the SOC graph
        return soc_graph
        

    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.plot(alt="An interactive plot")
    def power_time_graph():
        """
        The function uses the input from the 'power' parameter to get data on power vs time for all the selected dates.

        Returns 
            motor_power_graph: a matplotlib figure plot with the data plotted already.
        """
        # Get all flight data for interactive plot
        flight_ids = input.multi_select_flight_dates()
        # Graph the Motor Power
        motor_power_graph = Graphing.power_graph(flight_ids)
        # Return the Motor Power graph
        return motor_power_graph
    
    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.plot(alt="An interactive plot")
    def pilotweight_graph():
        """
        The function uses the input from the 'power' parameter to get data on power vs time for all the selected dates.

        Returns 
            motor_power_graph: a matplotlib figure plot with the data plotted already.
        """
        # Get all flight data for interactive plot
        flight_ids = input.multi_select_flight_dates()
        
        # Graph the Motor Power
        pilotweight_graph = Graphing.pilotweight_graph(flight_ids)

        # Return the Motor Power graph
        return pilotweight_graph


    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render_widget
    def lat_long_map():
        """
        Function uses a Python Shiny Widget to showcase a Mapbox Plotly map graph for flights. Uses a responsive text interface to communicate problems in flights.

        Returns:
            figure: A map graph of the flight to showcase on the UI
        """
        # Get the flight id
        flight_id = input.singular_flight_date()
        # Call the graphing function to map the latitudes and longitudes
        figure, latitudes, longitudes = Graphing.create_mapbox_map_per_flight(flight_id)
        if (np.count_nonzero(np.isnan(latitudes)) == len(latitudes)) or (np.count_nonzero(np.isnan(longitudes)) == len(longitudes)):
            @output
            @render.text
            def flight_gps_response_text():
                return "This specific flight does not contain any GPS coordinates. This may be because the pilot may have forgotten to turn on the GPS during flight."
        else:
            @output
            @render.text
            def flight_gps_response_text():
                return "The following graph shows the flight path of the Pipistrel Velis Electro plane for the date chosen."
        return figure


    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.text
    @reactive.event(input.singular_flight_date)
    def map_output_variability():

        # Get the flight id and output based on its outcome
        flight_id = input.singular_flight_date()

        # If there is no flight, return statement to choose flight
        if flight_id == "":
            return div(HTML(f"""Please input a <span style="color: {red};">flight date</span> to view the flight map."""))
        
        # If there is flight, return statement of id
        return div(HTML(f"""Your viewing flight with flight id: <span style="color: {blue};">{str(flight_id)}</span>."""))
    

    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.text
    @reactive.event(input.singular_flight_date)
    def num_circuits():
        """
        Function uses a responsive text interface to show the number of circuits.

        Returns:
            query_result: A numeric value of the number of circuits
        """

        # Get the flight id
        flight_id = input.singular_flight_date()

        # If there is no flight, return statement to choose flight
        if flight_id == "":
            return div(HTML(f"""<span style="color: {red};">No Flight Date</span>"""))
        
        # If there is flight, return the number of circuits.
        query_conn = query_flights()
        query_result = query_conn.get_number_of_circuits(flight_id)
        return div(HTML(f"""<span style="color: {blue};">{query_result}</span>"""))
    
    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.text
    def total_weight():
        """
        Function uses a responsive text interface to show the total weight.

        Returns:
            query_result: A numeric value of the total weight
        """

        # Get the flight id
        flight_id = input.singular_flight_date()
        # If there is no flight, return statement to choose flight
        if flight_id == "":
            return div(HTML(f"""<span style="color: {red};">No Flight Date</span>"""))

        query_conn = query_flights()
        query_result = query_conn.get_flight_weight(flight_id)

        # return the number
        return query_result
    
     # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.plot()
    def charging_graph():

        # Get all the inputs
        flight_ids = input.select_charging()
        graph_type = input.select_charging_graph()
        x_var_label = input.select_x_charging_variable()
        y_var_label = input.select_y_charging_variable()
        x_variables = charging_variables_columns[x_var_label]
        y_variables = charging_variables_columns[y_var_label]

        # Make the graph
        created_custom_graph = Graphing.charging_graph_creation(graph_type, flight_ids, x_variables, y_variables, x_var_label, y_var_label)

        # Return the custom graph
        return created_custom_graph  
    
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # END: DATA ANALYSIS SCREEN 
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # START: INSIGHTS SCREEN 
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.plot(alt="An interactive plot")
    def power_soc_rate_of_change_scatter_plot():
        """
        The function uses the input from the 'power_soc_rate_state' parameter to get data on power, soc rate of change, and activities for all the selected dates.
        Returns 
            power_soc_rate_of_change_scatterplot: a matplotlib figure scatterplot with the data plotted already.
        """
        
        # Get all flight data
        flight_id = input.statistical_time()
        activities_filter = input.select_activities()

        # Graph the power vs. soc rate of change scatter plot, whilte taking into account activities selected
        power_soc_rate_of_change_scatterplot = Graphing.power_soc_rate_scatterplot(flight_id, activities_filter)

        # Return the power vs. soc rate of change scatter plot
        return power_soc_rate_of_change_scatterplot
    

    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.plot(alt="An interactive plot")
    def soh_soc_rate_of_change_scatter_plot():
        """
        The function uses the input from the 'statistical_multi_time' parameter to get data on soh and soc rate of change for all the selected dates.
        Returns 
            soh_soc_rate_of_change_scatterplot: a matplotlib figure scatterplot with the data plotted already.
        """
        # Get all flight data
        flight_ids = input.statistical_multi_time()

        # Graph the soh vs. soc rate of change scatter plot
        soh_soc_rate_of_change_scatterplot = Graphing.soh_soc_rate_scatterplot(flight_ids)

        # Return the soh vs. soc rate of change scatter plot
        return soh_soc_rate_of_change_scatterplot
    

    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.plot(alt="An interactive plot")
    def soh_scatter_plot():
        """
        Returns 
            soh_plot: a matplotlib figure line plot with the data plotted already.
        """

        # Graph the date vs. soh line plot
        soh_plot = Graphing.soh_plot()

        # Return the date vs. soh line plot
        return soh_plot
    

    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.table
    def soc_roc_table(): 
        """
        The function uses the input from the 'soc_roc_state' parameter to get data on soc rate of change stats per activity for the selected date.
        Returns 
            soc_roc_df: a dataframe that will output as a table.
        """
        # Get the flight ID corresponding to the chosen date
        flight_id = input.statistical_time()

        soc_roc_df = query_flights().get_soc_roc_stats_by_id(flight_id)

        return soc_roc_df 
    
#     #-------------------------------------------------------------------------------------------------------------------------------------------------------------
#     # END: INSIGHTS SCREEN 
#     #-------------------------------------------------------------------------------------------------------------------------------------------------------------

#     #-------------------------------------------------------------------------------------------------------------------------------------------------------------
#     # START: UPLOAD SCREEN 
#     #-------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.data_frame 
    @reactive.event(input.filter_data)
    def preview_dataframe_construct():

        # Get all the input needed
        weather_col_dict = {k: v for k, v in custom_weather_dict.items() if k in input.weather_cols()}
        data_granularity_var = input.data_granularity()
        selection_dict = custom_granular_variables_dict.items() if data_granularity_var == "Granular" else custom_aggregate_variables_dict.items()
        flight_col_dict = {k: v for k, v in selection_dict if k in input.flight_cols()}
        flight_id = input.data_preview_date()
        limit = int(input.total_data_show())

        # If no columns are chosen, then return a dictionary that tells the user to choose a column.
        if len(weather_col_dict) == 0 or len(flight_col_dict) == 0:
            error_dict = {"Please select a weather or flight data column to view. Thank you!": ["-"]}
            error_df = pd.DataFrame(error_dict)
            return render.DataGrid(error_df)

        with ui.Progress(min=1, max=15) as p:
            p.set(message="Calculation in progress", detail="This may take a while...")

            # get the flight query and all other queries
            weather_data = query_weather().get_weather_data(flight_id, weather_col_dict)
            flight_data = query_flights().get_flight_by_column_dict(flight_id, flight_col_dict)

            # Make the holder dictionary 
            weather_concat_dict = {}

            # Get specific data out of the way
            flight_first_col = flight_data.iloc[:, 0].to_numpy()

            # If the length of the weather data is just 1. Fill everything like the weather and return. Else break into chunks and merge.
            if len(weather_data) == 1:

                # Loop over the weather columns
                for weather_col in weather_data.columns:

                    # Check to see if the col is any type of date or time. If there is, change the string to that value.
                    weather_full_data = np.full_like(flight_first_col, weather_data[weather_col][0], dtype=np.double)

                    # Add the numpy list to the dict to make into a dataframe
                    weather_concat_dict[weather_col] = weather_full_data

                # Add the final dict as a dataframe to a concatenated flight data. All data together.
                flight_data = pd.concat([flight_data, pd.DataFrame(weather_concat_dict)], axis=1)

            else:
                
                # split the arrays
                all_arrays = np.array_split(flight_first_col, len(weather_data))

                # Loop over the weather columns
                for weather_col in weather_data.columns:

                    # Make the full list to hold the weather data in bits.
                    weather_full_data = np.full_like(flight_first_col, 0.0, dtype=np.double)

                    # count the indexes
                    idx_counter = 0

                    # loop over the split arrays.
                    for i in range(len(all_arrays)):

                        # Get the split array on the index.
                        split = all_arrays[i]

                        # get the length of the split by the index counter plus the length of the split array.
                        split_len = len(split) + idx_counter

                        # Add the splited weather data based on the index of the array.
                        split_weather_data = np.full_like(split, weather_data[weather_col][i], dtype=np.double)

                        # For the lenth of the split add the data point.
                        weather_full_data[idx_counter:split_len] = split_weather_data

                        # Make the index counter to the length of the split for the next split.
                        idx_counter = split_len
                    
                    # Add the data to the weather dict.
                    weather_concat_dict[weather_col] = weather_full_data

                # Add to the final flight data to put together.
                flight_data = pd.concat([flight_data, pd.DataFrame(weather_concat_dict)], axis=1)

        return render.DataGrid(flight_data.loc[2:limit, :])

    
    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.text
    def most_recent_run():
        most_recent_run_time = get_most_recent_run_time()  # Run the scraper.py script when the app is loaded
        return div(HTML(f"""Data was last refreshed: <span style="color: {blue};">{most_recent_run_time}</span>"""))


    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    # Found yield answer here: https://github.com/posit-dev/py-shiny/issues/476
    @render.download(filename=lambda: f"{str(input.data_type_selection())}-{str(input.data_granularity())}-{str(input.data_preview_date())}.csv")
    async def downloadData():
        
        # Get all the input needed
        weather_col_dict = {k: v for k, v in custom_weather_dict.items() if k in input.weather_cols()}
        data_granularity_var = input.data_granularity()
        selection_dict = custom_granular_variables_dict.items() if data_granularity_var == "Granular" else custom_aggregate_variables_dict.items()
        flight_col_dict = {k: v for k, v in selection_dict if k in input.flight_cols()}
        flight_id = input.data_preview_date()

        # If no columns are chosen, then download a dictionary that says to select the columns
        if len(weather_col_dict) == 0 or len(flight_col_dict) == 0:
            error_dict = {"Please select a weather or flight data column to view. Thank you!": ["Please select a weather or flight data column to view. Thank you!"]}
            error_df = pd.DataFrame(error_dict)
            await asyncio.sleep(0.25)
            yield error_df.to_csv()
            return

        with ui.Progress(min=1, max=15) as p:
            p.set(message="Calculation in progress", detail="This may take a while...")

            # Get the weather and flight data
            weather_data = query_weather().get_weather_data(flight_id, weather_col_dict)
            flight_data = query_flights().get_flight_by_column_dict(flight_id, flight_col_dict)

            # Get specific data out of the way
            flight_first_col = flight_data.iloc[:, 0].to_numpy()

            # Initialize the dict to hold all data
            weather_concat_dict = {}

            # If the length of the weather data is just 1. Fill everything like the weather and return.
            if len(weather_data) == 1:
                
                # Loop over the weather columns
                for weather_col in weather_data.columns:

                    # Check to see if the col is any type of date or time. If there is, change the string to that value.
                    weather_full_data = np.full_like(flight_first_col, weather_data[weather_col][0], dtype=np.double)

                    # Add the numpy list to the dict to make into a dataframe
                    weather_concat_dict[weather_col] = weather_full_data

                # Add the final dict as a dataframe to a concatenated flight data. All data together.
                flight_data = pd.concat([flight_data, pd.DataFrame(weather_concat_dict)], axis=1)

            else:
                # split each value by the length of the number of weather data points
                all_arrays = np.array_split(flight_first_col, len(weather_data))

                # Loop over the weather columns
                for weather_col in weather_data.columns:

                    # Make the full list to hold the weather data in bits.
                    weather_full_data = np.full_like(flight_first_col, 0.0, dtype=np.double)

                    # count the indexes
                    idx_counter = 0

                    # loop over the split arrays.
                    for i in range(len(all_arrays)):

                        # Get the split array on the index.
                        split = all_arrays[i]

                        # get the length of the split by the index counter plus the length of the split array.
                        split_len = len(split) + idx_counter

                        # Add the splited weather data based on the index of the array.
                        split_weather_data = np.full_like(split, weather_data[weather_col][i], dtype=np.double)

                        # For the lenth of the split add the data point.
                        weather_full_data[idx_counter:split_len] = split_weather_data

                        # Make the index counter to the length of the split for the next split.
                        idx_counter = split_len
                    
                    # Add the data to the weather dict.
                    weather_concat_dict[weather_col] = weather_full_data

                # Add to the final flight data to put together.
                flight_data = pd.concat([flight_data, pd.DataFrame(weather_concat_dict)], axis=1)
        
        await asyncio.sleep(0.25)
        yield flight_data.to_csv()

    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.ui
    @reactive.event(input.data_type_selection)
    def data_type_dates():
        data_type = input.data_type_selection()
        return ui.input_selectize("data_preview_date", "Select the Date:", get_flights(flight_type=data_type))
        
    
    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.ui
    @reactive.event(input.data_granularity)
    def flight_preview_columns_choice():
        granularity = input.data_granularity()

        if granularity == "Granular":
            return ui.input_selectize("flight_cols", "Select Flight Data Columns", choices=custom_granular_variables, multiple=True, selected=custom_granular_variables[:5], width="100%")
        else:
            return ui.input_selectize("flight_cols", "Select Flight Data Columns", choices=custom_aggregate_variables, multiple=True, selected=custom_aggregate_variables[:5], width="100%")
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # END: UPLOAD SCREEN 
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    # #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # # START: SIMULATION SCREEN 
    # #-------------------------------------------------------------------------------------------------------------------------------------------------------------

    # For the selection of the flight operations. Global variable to hold the flight operations.
    table_data_show = reactive.Value(-1)
    new_model = Model()
    flight_operation_dictionary = {
        "Activity": [], 
        "Time (mins)": [], 
        "SOH (%)": [],
        "Altitude Gain/Loss (ft)": [],
        "Ground Speed (knots)": [],
        "Motor Power (KW)": [],
        "SOC (%)": [],
    }


    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.table(columns=["Forecast Time", simulation.first_date, simulation.second_date, simulation.third_date])
    def simulation_table(): 
        # Apply conditional formatting
        zones = simulation.zones_table
        explanations = simulation.explanations_table
        styled_data = zones.style.set_tooltips(explanations, props='visibility: hidden; position: absolute; z-index: 1; border: 1px solid #000066;'
                         'background-color: white; color: #000066; font-size: 0.8em;'
                         'transform: translate(0px, -24px); padding: 0.6em; border-radius: 0.5em;').applymap(style_cell).set_table_styles(
                             [{'selector': 'td', 'props': [('width', '450px'), ('border', '5px solid white')]},
                              {'selector': 'td', 'props': [('text-align', 'center')]}, # Center align text in cells
                              {'selector': 'th', 'props': [('text-align', 'center')]},  # Center align column names
                              ]).hide(axis="index")
        return styled_data
    

    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    # Define a function to determine the cell background color
    def style_cell(val):
        if val == 'red':
            return "background-color: #c62828; color: #c62828;"
        elif val == 'yellow':
            return "background-color: #fdd835; color: #fdd835;"
        elif val == 'green':
            return "background-color: #43a047; color: #43a047;"
    

    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    def colour_word(word):
        # make these words red
        if (word =='no' or word == 'flights' or word == 'available'):
            return 'color: red'
        else:
            return 'color: black'
        

    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.table
    def flight_planning_table(): 
        # if the feasible_flights dataframe is empty
        if simulation.feasible_flights.empty:
            # Return a DataFrame with the message
            message_df = pd.DataFrame({"Message": ["There are no flights available to be scheduled today due to weather conditions."]})
            message_df['Message'] = message_df['Message'].apply(lambda x: ' '.join(['<span style="{}">{}</span>'.format(colour_word(word), word) for word in x.split()])) # formats "no flights available" as red

            message_style = message_df.style.hide(axis="index").hide(axis="columns").set_table_styles([
                            {'selector': 'tr', 'props': [('height', '50px')]}, # make row height taller
                            {'selector': 'td', 'props': [('width', '700px')]}, # Set table width
                            {'selector': 'td', 'props': [('text-align', 'left')]}, # left align text in cells
                        ]) 
            return message_style
        else:
            flight_plan = simulation.feasible_flights.style.hide(axis="index").set_table_styles([
                            {'selector': 'tr', 'props': [('height', '50px')]}, # make row height taller
                            {'selector': 'tr', 'props': [('box-shadow', '1px 1px 4px rgba(0, 0, 0, 0.1)')]},  # Add shadow box effect
                            {'selector': 'td', 'props': [('width', '450px')]}, # Set table width
                            {'selector': 'td', 'props': [('text-align', 'center')]}, # Center align text in cells
                            {'selector': 'th', 'props': [('text-align', 'center')]},  # Center align column names
                        ])
            return flight_plan
    

    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.ui
    @reactive.event(input.date_operations)
    def time_selector():
        flight_dates = input.date_operations()

        if flight_dates == "":
            return ui.output_text("Please select a date to fly")
        else:
            return ui.input_selectize("flight_time_select", "Choose start time of flight:", ["12:00 AM", "12:15 AM", "12:30 AM", "12:45 AM", "01:00 AM", "01:15 AM", "01:30 AM", "01:45 AM", "02:00 AM", "02:15 AM", "02:30 AM", "02:45 AM", "03:00 AM", "03:15 AM", "03:30 AM", "03:45 AM", "04:00 AM", "04:15 AM", "04:30 AM", "04:45 AM", "05:00 AM", "05:15 AM", "05:30 AM", "05:45 AM", "06:00 AM", "06:15 AM", "06:30 AM", "06:45 AM", "07:00 AM", "07:15 AM", "07:30 AM", "07:45 AM", "08:00 AM", "08:15 AM", "08:30 AM", "08:45 AM", "09:00 AM", "09:15 AM", "09:30 AM", "09:45 AM", "10:00 AM", "10:15 AM", "10:30 AM", "10:45 AM", "11:00 AM", "11:15 AM", "11:30 AM", "11:45 AM", "12:00 PM", "12:15 PM", "12:30 PM", "12:45 PM", "01:00 PM", "01:15 PM", "01:30 PM", "01:45 PM", "02:00 PM", "02:15 PM", "02:30 PM", "02:45 PM", "03:00 PM", "03:15 PM", "03:30 PM", "03:45 PM", "04:00 PM", "04:15 PM", "04:30 PM", "04:45 PM", "05:00 PM", "05:15 PM", "05:30 PM", "05:45 PM", "06:00 PM", "06:15 PM", "06:30 PM", "06:45 PM", "07:00 PM", "07:15 PM", "07:30 PM", "07:45 PM", "08:00 PM", "08:15 PM", "08:30 PM", "08:45 PM", "09:00 PM", "09:15 PM", "09:30 PM", "09:45 PM", "10:00 PM", "10:15 PM", "10:30 PM", "10:45 PM", "11:00 PM", "11:15 PM", "11:30 PM", "11:45 PM"])


    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.ui
    @reactive.event(input.manual_model_input_switch, input.flight_activities)
    def duration_of_activity():
        flight_activity = input.flight_activities()
        manual_input = input.manual_model_input_switch()

        if manual_input == True:
            return ui.input_numeric("duration_chooser", f"Time (mins) for {flight_activity}:", 1, min=1, max=60)
        else:
            return ui.input_slider("time_delta_slider", "Time (mins)", min=0, max=60, step=0.5, value=[5, 8])
        

    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.ui
    @reactive.event(input.manual_model_input_switch, input.flight_activities)
    def power_setting_activity():
        flight_activity = input.flight_activities()
        manual_input = input.manual_model_input_switch()

        if manual_input == True:
            return ui.input_numeric("power_setting_chooser", f"Motor power (KW) for {flight_activity}:", 1, min=0, max=70)
        else:
            return ui.input_slider("power_setting_slider", "Motor power (KW)", min=0, max=65, step=2, value=[4, 20])


    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.ui
    @reactive.event(input.manual_model_input_switch, input.flight_activities)
    def altitude_activity():
        flight_activity = input.flight_activities()
        manual_input = input.manual_model_input_switch()

        if manual_input == True:
            return ui.input_numeric("altitude_chooser", f"Change in Altitude (ft) for {flight_activity}:", 0, min=-1000, max=1000)
        else:
            return ui.input_slider("altitude_slider", "Change in Altitude (ft)", min=-1000, max=1000, step=10, value=[400, 500])
        
    
    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.ui
    @reactive.event(input.manual_model_input_switch, input.flight_activities)
    def soh_activity():
        flight_activity = input.flight_activities()
        manual_input = input.manual_model_input_switch()

        if manual_input == True:
            return ui.input_numeric("soh_chooser", f"State-of-health (%) for {flight_activity}:", 100, min=0, max=100)
        else:
            return div(HTML(f"""<p style="font-weight: normal; font-size: 18px;">
                            State-of-health (%) from the <span style="color: {blue};">latest flight</span> will be used.</p>"""))
    

    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.ui
    @reactive.event(input.manual_model_input_switch, input.flight_activities)
    def ground_speed_activity():
        flight_activity = input.flight_activities()
        manual_input = input.manual_model_input_switch()

        if manual_input == True:
            return ui.input_numeric("ground_speed_chooser", f"Ground speed (knots) for {flight_activity}:", 1, min=0, max=20)
        else:
            return ui.input_slider("ground_speed_slider", "Ground speed (knots)", min=0, max=100, step=5, value=[45, 50])
        

    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.ui
    @reactive.event(table_data_show)
    def remaining_soc():

        # Get the total soc and return it
        total_soc = sum(flight_operation_dictionary["SOC (%)"]) if len(flight_operation_dictionary["SOC (%)"]) != 0 else 0
        soc = round(float(100 - total_soc), 2)
        if total_soc >= 70:
            return div(HTML(f"""<p style="font-weight: normal; font-size: 16px; border: 1px solid #DBDBDB; padding: 0px;">Total Remaining <span style="color: {red};">SOC: {soc}</span>.
                 You are below <span style="color: {red};">30 % threshold</span>. Adding additional activities <span style="color: {red};">impacts pilot safety</span>.</p>"""))
        else:
            return div(HTML(f"""<p style="font-weight: normal; font-size: 16px; padding: 0px;">Total Remaining <span style="color: {blue};">SOC: {soc}</span>.
                 You are <span style="color: {blue};">free to add</span> more activities in this flight.</p>"""))


    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.data_frame 
    @reactive.event(table_data_show)
    def model_predict_output():

        # Make it a data frame
        flight_operation_output_table = pd.DataFrame(flight_operation_dictionary)

        # Return that data frame
        return render.DataGrid(flight_operation_output_table, row_selection_mode="single")


    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @reactive.effect
    @reactive.event(input.add_activity)
    def _():

        # Get the reactive variable:
        reactive_var = table_data_show.get() + 1

        # Get the inputs from the flight operation and time selection criteria
        operation = input.flight_activities()
        manual_input = input.manual_model_input_switch()
        date = input.date_operations()
        time = input.flight_time_select()

        with ui.Progress(min=1, max=15) as p:
            p.set(message="Calculation in progress", detail="This may take a while...")

            # Change the time to see if the time is incremented every 15 minutes.
            if len(flight_operation_dictionary["Time (mins)"]) > 0:
                
                # Get each segment of the time string
                hour_str = time[0:3]
                period = time[5:8]

                # Change the minutes to every 15 when the time passes that minute
                if len(flight_operation_dictionary["Time (mins)"]) == 1:
                    current_time = flight_operation_dictionary["Time (mins)"][0]
                else:
                    current_time = sum(flight_operation_dictionary["Time (mins)"])
                if current_time > 15:
                    time = hour_str + "15" + period
                elif current_time > 30:
                    time = hour_str + "30" + period
                elif current_time > 45:
                    time = hour_str + "45" + period

            # Get soc based on inputs
            if manual_input: 
                model_time = input.duration_chooser()
                model_power = input.power_setting_chooser()
                model_altitude = input.altitude_chooser()
                model_soh = input.soh_chooser()
                model_speed = input.ground_speed_chooser()
                predicted_soc, act_time, act_power, act_soh, act_alt, act_groundspeed = new_model.get_manual_model_prediction(operation, date, time, model_time, model_altitude, model_speed, model_power, model_soh)
            else:
                tuple_time = input.time_delta_slider()
                tuple_power = input.power_setting_slider()
                tuple_altitude = input.altitude_slider()
                tuple_speed = input.ground_speed_slider()
                predicted_soc, act_time, act_power, act_soh, act_alt, act_groundspeed = new_model.get_model_prediction(operation, date, time, tuple_time, tuple_altitude, tuple_speed, tuple_power)

            # Append all the activities and times in the variable
            flight_operation_dictionary["Activity"].append(operation)
            flight_operation_dictionary["Time (mins)"].append(act_time)
            flight_operation_dictionary["SOH (%)"].append(act_soh)
            flight_operation_dictionary["Altitude Gain/Loss (ft)"].append(act_alt)
            flight_operation_dictionary["Ground Speed (knots)"].append(act_groundspeed)
            flight_operation_dictionary["Motor Power (KW)"].append(act_power)
            flight_operation_dictionary["SOC (%)"].append(predicted_soc)

        # Set the data show to 1
        table_data_show.set(reactive_var)


    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @reactive.effect
    @reactive.event(input.delete_selected_activity)
    def _():

        # Get the specific row from the table
        delete_row_indexes = input.model_predict_output_selected_rows()

        if len(delete_row_indexes) != 0:

            # Get the reactive variable:
            reactive_var = table_data_show.get() - 1

            # remove the specific index
            for row_id in delete_row_indexes:
                del flight_operation_dictionary["Activity"][row_id]
                del flight_operation_dictionary["Time (mins)"][row_id]
                del flight_operation_dictionary["SOH (%)"][row_id]
                del flight_operation_dictionary["Altitude Gain/Loss (ft)"][row_id]
                del flight_operation_dictionary["Ground Speed (knots)"][row_id]
                del flight_operation_dictionary["Motor Power (KW)"][row_id]
                del flight_operation_dictionary["SOC (%)"][row_id]


            # Set the data show to 1
            table_data_show.set(reactive_var)

    # #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # # END: SIMULATION SCREEN 
    # #-------------------------------------------------------------------------------------------------------------------------------------------------------------

# Get the App Ready and Host
www_dir = Path(__file__).parent / "www"
app = App(app_ui, server, static_assets=www_dir, debug=True)
