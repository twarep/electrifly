import pandas as pd
from shiny import App, render, ui
import shiny

# Rendered through following code example:
# https://shiny.posit.co/py/api/ui.output_table.html#shiny.ui.output_table

weather_data_df = pd.DataFrame(
                {"Id": [1, 2, 3, 4, 5, 6], 
                 "Time": ["7/11/2023 5:00:00 PM", "7/11/2023 6:00:00 PM", "7/11/2023 7:00:00 PM", "7/11/2023 7:31:00 PM", "7/11/2023  7:55:00 PM", "7/11/2023  7:56:00 PM"], 
                 "Air Temperature": [80.6, 82.4, 80.6, 78.8, 78.8, 78.8], 
                 "Wind Direction (degrees from true north)": [230, 240, 220, 230, 230, 220], 
                 "Wind Speed (Knots)": [14, 13, 14, 13, 7, 7], 
                 "Visibility (miles)": [9, 9, 9, 9, 9, 9], 
                 "Wind Gust (Knots)": [21, 20, 19, 18, 18, 15]})

plane_data_df = pd.DataFrame(
                {"Id": [2345, 2346, 2347, 2348], 
                 "Battery 1 SOC": [100, 87, 61, 43], 
                 "Battery 2 SOC": [100, 88, 61, 43], 
                 "Battery 1 Average Temperature (°C)": [19, 21, 24, 25], 
                 "Battery 2 Average Temperature (°C)": [19, 20, 24, 25],
                 "Indicated Airspeed (Knots)": [0, 59.71556, 71.93128, 83.11363], 
                 "Requested Torque": [0, 857, 758, 385]})


app_ui = ui.page_fluid(
    ui.h3("Python Shiny Tables Example"),
    ui.div("Weather Data Records:"),
    ui.output_table("weather_data_result"),
    ui.div("Flight Data Record:"),
    ui.output_table("plane_data_result"),
)


def server(input, output, session):
    @output
    @render.table
    def weather_data_result():
        return weather_data_df
    
    @output
    @render.table
    def plane_data_result():
        return plane_data_df

    
app = App(app_ui, server)