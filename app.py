from shiny import App, render, ui, Inputs, Outputs, Session, reactive
from htmltools import HTML, div
from shiny.types import NavSetArg
from typing import List
from flight_querying import query_flights
from weather_querying import query_weather
from htmltools import css
import shinyswatch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import asyncio
from datetime import date
import numpy as np
from os import listdir
from os.path import isfile, join
import shiny.experimental as x
mypath = "./test_data/"

# Initialize the flight data dates as name keys
data_file_names = [f for f in listdir(mypath) if isfile(join(mypath, f))]
data_file_changed_names = [name[14:name.index('.')].replace('.csv', '').replace('-', ' ').capitalize() for name in data_file_names]
data = {}

# Get all data from files and store in data dictionary
for file in data_file_names:
    data_df = pd.read_csv(join(mypath, file))
    soc = (data_df[' bat 1 soc'].to_numpy() + data_df[' bat 2 soc'].to_numpy()) / 2
    time_minutes = data_df[' time(min)'].to_numpy()
    data[file[14:file.index('.')].replace('.csv', '').replace('-', ' ').capitalize()] = {'soc': soc, 'time': time_minutes}


# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
def get_flights(date: bool):

    flights = query_flights()

    flight_data = flights.get_flight_id_and_dates()

    if date:
        return list(flight_data.keys())
    
    return flight_data


# Table data
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

app_ui = ui.page_navbar(
    shinyswatch.theme.zephyr(),
    ui.nav("Upload Data",
            ui.download_button("downloadData", "Flight & Weather Data Refresh", style="background-color: #007bff; color: white;"),
            div(HTML("<hr>")),
            ui.h3("Python Shiny Tables Example"),
            div(HTML("<hr>")),
            div("Weather Data Records:"),
            ui.output_table("weather_data_result"),
            div(HTML("<hr>")),
            div("Flight Data Record:"),
            ui.output_table("plane_data_result"),
            div(HTML("<hr>")),
        ),
    ui.nav("Data Analysis", 
            ui.include_css("bootstrap.css"),
            x.ui.card(
                x.ui.card_header("Welcome to ElectriFly's Data Analytics Interface!"),
                x.ui.card_body("Unlock the power of your data with our intuitive and powerful user interface designed specifically for data analytics. Our platform empowers you to transform raw data into actionable insights, enabling you to make informed decisions and drive your business forward.")
                ),
            div(HTML("<hr>")),
            div(HTML("<p><b>SOC vs. Time Across Multiple Flights</b></p>")),
            div(HTML("<hr>")),
            ui.layout_sidebar(
                ui.panel_sidebar(
                    ui.input_select(
                        "state",
                        "Choose flight date(s):",
                        data_file_changed_names,
                        selected=data_file_changed_names[0],
                        multiple=True,
                    ),
                    div(HTML("<p>To select multiple dates on <b>Windows</b>: </p>")),
                    div("1. Press `ctrl` + select the dates"),
                    div(HTML("<hr>")),
                    div(HTML("<p>To select multiple dates on <b>Mac</b>: </p>")),
                    div("1. Press `cmd` + select the dates"),
                    width = 3
                ),
                ui.panel_main(
                    ui.output_plot("interactive")
                ),
            ),
            div(HTML("<hr>")),
            div(HTML("<p><b>Weather Data for Selected Flights</b></p>")),
            div(HTML("<hr>")),
            ui.layout_sidebar(
                ui.panel_sidebar(
                    ui.input_select(
                        "weather_state",
                        "Choose flight date(s):",
                        get_flights(True),
                        selected=get_flights(True)[0],
                    ),
                ),
                ui.panel_main(
                    ui.output_table("weather_interactive")
                ),
                position='right'
            ),
        ),  
    ui.nav("Recommendations", 
           "In Construction! ML Predictions on the way!"),
    title="Electrifly UI",
)

#arbitrarly downloads this random doc -> functionality needs to change
def server(input: Inputs, output: Outputs, session: Session):

    @session.download(
        filename=lambda: f"{date.today().isoformat()}-{np.random.randint(100,999)}.csv"
    )
    async def downloadData():
        await asyncio.sleep(0.25)
        yield "one,two,three\n"

    @output
    @render.table
    def weather_data_result():
        return weather_data_df
    
    @output
    @render.table
    def plane_data_result():
        return plane_data_df

    @output
    @render.table
    def weather_interactive(): 
        # Get the flight ID corresponding to the chosen date
        flight_date = input.weather_state()
        flight_id = get_flights(False)[flight_date]
        weather_df = query_weather().get_weather_by_flight_id(flight_id)
        return weather_df 

    @output
    @render.plot(alt="An interactive plot")
    def interactive():
        # SOC ranges
        x1 = 0
        x2 = 60
        y1 = 15.01
        y2 = 30
        r1 = 0
        r2 = 15
        # Fill ranges
        plt.fill([x1, x1, x2, x2], [y1, y2, y2, y1], c="yellow", alpha=0.5)
        plt.fill([x1, x1, x2, x2], [r1, r2, r2, r1], c='r', alpha=0.5)
        # Add text to fill ranges
        plt.text(0.2, 20.5, 'Warning', fontsize='large', fontweight='bold')
        plt.text(0.2, 5.5, 'Danger', fontsize='large', fontweight='bold', c='white')
        # Plot the graphs
        for date in input.state():
            if date in data.keys():
                soc = data[date]['soc']
                time = data[date]['time']
                plt.plot(time, soc, label=date)
        # Add labels and legend to plot
        plt.xlim([0, 55])
        plt.ylim([-1, 101])
        plt.xlabel("time (min)")
        plt.ylabel("SOC")
        plt.title("Time vs SOC")
        # plt.legend(loc="lower left")
        plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1.02),
          ncol=3, fancybox=True, shadow=True)



app = App(app_ui, server, debug=True)
