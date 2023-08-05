from shiny import App, render, ui, Inputs, Outputs, Session, reactive
from htmltools import HTML, css, div
from shiny.types import NavSetArg
from typing import List
from flight_querying import query_flights
from weather_querying import query_weather
import Graphing as Graphing
from htmltools import css
import shinyswatch
import numpy as np
import pandas as pd
import asyncio
import matplotlib.pyplot as plt
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
    engine = sa.create_engine(db_url, connect_args={"options": "-c timezone=US/Eastern"})
    return engine


def uploaded_data():
     engine = connect_to_db("PostgreSQL")
     query = "SELECT * FROM flight_weather_data_view2 LIMIT 10;"
    # Execute the query and fetch the data into a DataFrame
     uploaded_data_df = pd.read_sql(query, con=engine)
    #uploaded_data_df['flight_date'] = pd.to_datetime(uploaded_data_df['flight_date'])
     uploaded_data_df['flight_date'] = pd.to_datetime(uploaded_data_df['flight_date'], format="%Y-%m-%d %H:%M:%S")
    # Convert the 'flight_date' column back to a string
     uploaded_data_df['flight_date'] = uploaded_data_df['flight_date'].dt.strftime("%Y-%m-%d")
     return uploaded_data_df



def uploaded_cols(): 
    uploaded_data_df = uploaded_data()
    all_uploaded_cols = uploaded_data_df.iloc[:, 1:]
    return all_uploaded_cols


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

            #column selection panel
            ui.div(
            # Dropdown with checkboxes
            ui.input_select("selected_cols", "Select Columns to Preview",choices= list(uploaded_cols().columns), multiple=True),
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
                                get_flights(True),
                                selected=get_flights(True)[0],
                                multiple=True,
                            ),
                            div(HTML("<p>To select multiple dates:</p>")),
                            div(HTML("""<table>
                                          <tr>
                                            <th><b>Windows</b>:</th>
                                          </tr>
                                          <tr>
                                            <td>`ctrl` + click</td>
                                        </table>
                                        <table>
                                          <tr>
                                            <th><b>Mac</b>:</th>
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

    title="ElectriFly",
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
        soc_graph = Graphing.graph_soc_graph(list(input.state()))



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

    @output
    @render.data_frame
    def uploaded_data_df():
        uploaded_data_df = uploaded_data()
        selected_columns = input.selected_cols()
        if not selected_columns:
            # Return the entire DataFrame as default when no columns are selected
            default_columns = uploaded_data_df.loc[:,["flight_id","flight_date", "weather_time_utc", "time_min","bat_1_soc", 
                                               "bat_2_soc","motor_power", "motor_temp"]]
            return default_columns
        else:
            # Filter the DataFrame based on the selected columns
            filtered_df = uploaded_data_df.loc[:, selected_columns]
            return filtered_df
        
app = App(app_ui, server, debug=True)
