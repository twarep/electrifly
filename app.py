from shiny import App, render, ui, Inputs, Outputs, Session, reactive
from htmltools import HTML, css, div
from shiny.types import NavSetArg
from typing import List
from flight_querying import query_flights
from weather_querying import query_weather
from htmltools import css
import shinyswatch
import numpy as np
import pandas as pd
import asyncio
from datetime import date
import numpy as np
import matplotlib.pyplot as plt
from os import listdir
from os.path import isfile, join
import shiny.experimental as x
from shiny import App, Inputs, Outputs, Session, render, ui
import psycopg2
import sqlalchemy as sa

mypath = "./test_data/"

#database connection 
def connect_to_db(provider: str):
    provider == "PostgreSQL"
    db_url = "postgresql+psycopg2://user:YU37CrnJMLjG@ep-snowy-pond-543889.us-east-2.aws.neon.tech:5432/electrifly-db"
    engine = sa.create_engine(db_url)
    return engine

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


app_ui = ui.page_navbar(
    # {"style": "color: blue"},
    shinyswatch.theme.zephyr(),

    #UPLOAD SCREEN 
    ui.nav("Upload Data",
            #data refresh button 
            ui.download_button("downloadData", "Flight & Weather Data Refresh", style="background-color: #007bff; color: white;"),
            #expand columns toggle (will be replaced with a multiselect dropdown of columns)
            ui.div(ui.input_switch("expandDataGrid", "Expand Columns", False),
                style="margin-top:40px;"),
            #table header
            ui.div(
                ui.include_css("bootstrap.css"), ui.h4("Most Recent Flight and Weather Data Records"), 
                style="margin-top: 3px;"),  
            #table ouptut
            ui.div(ui.output_data_frame("uploaded_data_df"),
                    ui.include_css("bootstrap.css"),
                    style="margin-top: 2px; max-height: 3000px;",),
           ),

           
    #DATA ANALYSIS SCREEN
    ui.nav("Data Analysis", 
        ui.include_css("bootstrap.css"),
            x.ui.card(
                x.ui.card_header("Welcome to ElectriFly's Data Analytics Interface!"),
                x.ui.card_body("Unlock the power of your data with our intuitive and powerful user interface designed specifically for data analytics. Our platform empowers you to transform raw data into actionable insights, enabling you to make informed decisions and drive your business forward.")
                ),
            #This creates the tabs between the recommended graph screen and the insights
        ui.navset_tab(
            ui.nav("Recommended Graphs", 
              #-----------------------------------------------------------------------------------
              # DIVIDES the page into a row, meaning you can put ui elements side by side
              #-----------------------------------------------------------------------------------
              ui.row( 
                  ui.column(6, # put columns within the rows, the column first param is the width, your total widths add up to 12
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
                            div(HTML("<p>To select multiple dates:</p>")),
                            div(HTML("""<table>
                                          <tr>
                                            <th>Windows</th>
                                          </tr>
                                          <tr>
                                            <td>`ctrl` + click</td>
                                        </table>
                                        <table>
                                          <tr>
                                            <th>Mac</th>
                                          </tr>
                                          <tr>
                                            <td>'cmd' + click</td>
                                          </tr>
                                        </table>""")),
                                width=3
                        ),
                        ui.panel_main(
                            ui.output_plot("interactive")
                        ),
                    )),
                  ui.column(6,
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
                        width=3),
                        ui.panel_main(
                            ui.output_table("weather_interactive")
                        ),
                    position='right'
                    )),
            )),
            ui.nav("Insights", "Statistical Insights in Construction!"),
        ),
            
        ),  

    #ML RECOMMENDATIONS SCREEN
    ui.nav("Recommendations", 
           "In construction! ML predictions on the way!"),

    title="ElectriFly UI",
)


def server(input: Inputs, output: Outputs, session: Session):
  
    #-----------------------------------------------------------------------------------
    #DATA ANALYSIS SCREEN 
    #-----------------------------------------------------------------------------------
    

    @session.download(
        filename=lambda: f"{date.today().isoformat()}-{np.random.randint(100,999)}.csv"
    )
    async def downloadData():
        await asyncio.sleep(0.25)
        yield "one,two,three\n"

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


    #-----------------------------------------------------------------------------------
    #UPLOAD SCREEN 
    #-----------------------------------------------------------------------------------
    
    #arbitrarly downloads this random doc -> functionality needs to change
    @session.download(
        filename=lambda: f"{date.today().isoformat()}-{np.random.randint(100,999)}.csv"
    )
    async def downloadData():
        await asyncio.sleep(0.25)
        yield "one,two,three\n"

    #query for table 
    @reactive.Calc
    def uploaded_data():
        engine = connect_to_db("PostgreSQL")
        query = "SELECT * FROM flight_weather_data_view LIMIT 10;"
        # Execute the query and fetch the data into a DataFrame
        uploaded_data_df = pd.read_sql(query, con=engine)
        return uploaded_data_df
    
    #output table 
    @output
    @render.data_frame
    def uploaded_data_df():
        if input.expandDataGrid():
            return uploaded_data()
        else:
            uploaded_data_df = uploaded_data()
            collapsed_columns = uploaded_data_df.loc[:,["flight_id", "time_min", "bat_1_current",
                                               "bat_2_current","bat_1_voltage", "bat_2_voltage", "bat_1_soc", 
                                               "bat_2_soc","motor_power", "motor_temp"]]
            return collapsed_columns

app = App(app_ui, server, debug=True)
