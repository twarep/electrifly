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
from shinywidgets import output_widget, render_widget
import sqlalchemy as sa

# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
#database connection 
def connect_to_db(provider: str):
    provider == "PostgreSQL"
    #db_url = "postgresql+psycopg2" + os.getenv('DATABASE_URL')[8:]
    db_url = "postgresql+psycopg2://user:velis@129.97.25.100:5432/velis"
    engine = sa.create_engine(db_url, connect_args={"options": "-c timezone=US/Eastern"})
    return engine


# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
def uploaded_data():
     engine = connect_to_db("PostgreSQL")
     query = "SELECT * FROM flight_weather_data_view LIMIT 10;"
    # Execute the query and fetch the data into a DataFrame
     uploaded_data_df = pd.read_sql(query, con=engine)
     uploaded_data_df['flight_date'] = pd.to_datetime(uploaded_data_df['flight_date'], format="%Y-%m-%d %H:%M:%S")
    # Convert the 'flight_date' column back to a string
     uploaded_data_df['flight_date'] = uploaded_data_df['flight_date'].dt.strftime("%Y-%m-%d")
     engine.dispose()
     return uploaded_data_df


# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
def uploaded_cols(): 
    uploaded_data_df = uploaded_data()
    all_uploaded_cols = uploaded_data_df.iloc[:, 1:]
    return all_uploaded_cols


# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
def get_flights(date: bool):
    """
    The function uses the query_flights class to get all the flights ids and dates in a dictionary of key: value --> flight_date: flight_id. 
    It returns data depending if the the input parameter specifies only flight_date to be returned.

    Parameters:
        date: Boolean value to specify if you only want to return a list of flight dates from the DB.

    Returns:
        if date is TRUE --> list(flight_data.keys()): List of flight dates in form mm/dd/yyyy
        if date is FALSE --> flight_date: dictionary of flight_date: flight_id pairs
    """
    flights = query_flights()

    flight_data = flights.get_flight_id_and_dates()

    if date:
        return list(flight_data.keys())
    
    return flight_data


# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
app_ui = ui.page_navbar(
    # {"style": "color: blue"},
    shinyswatch.theme.zephyr(),

    # UPLOAD SCREEN        ################################################################################################################################
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
    # DATA ANALYSIS SCREEN ################################################################################################################################
    ui.nav("Data Analysis", 
        ui.include_css("bootstrap.css"),
            x.ui.card(
                x.ui.card_header("Welcome to ElectriFly's Data Analytics Interface!"),
                x.ui.card_body("""Unlock the power of your data with our intuitive and powerful user interface designed specifically for data analytics. 
                               Our platform empowers you to transform raw data into actionable insights, enabling you to make informed decisions and drive your business forward.""")
                ),
            #This creates the tabs between the recommended graph screen and the insights
        ui.navset_tab(
            # RECOMMENDED GRAPHS TAB ################################################################################################################################
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
                                "soc",
                                "Choose flight date(s):",
                                get_flights(True),
                                selected=get_flights(True)[0],
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
                            ui.output_plot("soc_time_graph")
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
                ),

                ui.row( 
                    ui.column(6, # put columns within the rows, the column first param is the width, your total widths add up to 12
                        div(HTML("<hr>")),
                        div(HTML("<p><b>Power Setting vs. Time Across Multiple Flights</b></p>")),
                        div(HTML("<hr>")),
                        ui.layout_sidebar(
                            ui.panel_sidebar(
                                ui.input_select(
                                    "power",
                                    "Choose flight date(s):",
                                    get_flights(True),
                                    selected=get_flights(True)[0],
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
                                ui.output_plot("power_time_graph")
                            ),
                        )
                    ),
                    # This is the start of the code for the flight circuit map #################################################################
                    ui.column(6,
                        div(HTML("<hr>")),
                        div(HTML("<p><b>Flight Circuit Map</b></p>")),
                        div(HTML("<hr>")),
                        ui.output_text("flight_gps_response_text"),
                        ui.layout_sidebar(
                            ui.panel_sidebar(
                                ui.input_select(
                                    "map_state",
                                    "Choose flight date(s):",
                                    get_flights(True),
                                ),
                                width=3
                            ),
                            ui.panel_main(
                                output_widget("lat_long_map")
                            ),
                            position='right'
                        ),
                    # This is the end of the code for the flight circuit map #################################################################
                    ),
                )
            ),
                
            ui.nav("Insights", "Statistical Insights in Construction!"),
        ),
            
        ),  

    #ML RECOMMENDATIONS SCREEN
    ui.nav("Recommendations", 
           "In construction! ML predictions on the way!"),

    title="ElectriFly",
)


# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
def server(input: Inputs, output: Outputs, session: Session):
  
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # START: DATA ANALYSIS SCREEN 
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.table
    def weather_interactive(): 
        # Get the flight ID corresponding to the chosen date
        flight_date = input.weather_state()
        flight_id = get_flights(False)[flight_date]
        weather_df = query_weather().get_weather_by_flight_id(flight_id)
        return weather_df 


    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.plot(alt="An interactive plot")
    def soc_time_graph():
        """
        The function uses the input from the 'state' parameter to get data on soc vs. time for all the selected dates.

        Returns 
            soc_graph: a matplotlib figure plot with the data plotted already.
        """
        # Get all flight data for interactive plot
        flight_data = get_flights(False)
        flight_dates = input.soc()
        flight_ids = []

        # Add flight ids to list
        for flight_date in flight_dates:
            flight_ids.append(flight_data[flight_date])

        # Graph the SOC
        soc_graph = Graphing.soc_graph(flight_ids, flight_dates)

        # Return the SOC graph
        return soc_graph
        
    
    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.plot(alt="An interactive plot")
    def power_time_graph():
        """
        The function uses the input from the 'power' parameter to get data on power vs. time for all the selected dates.

        Returns 
            motor_power_graph: a matplotlib figure plot with the data plotted already.
        """
        # Get all flight data for interactive plot
        flight_data = get_flights(False)
        flight_dates = input.power()
        flight_ids = []

        # Add flight ids to list
        for flight_date in flight_dates:
            flight_ids.append(flight_data[flight_date])
        
        # Graph the Motor Power
        motor_power_graph = Graphing.power_graph(flight_ids, flight_dates)

        # Return the Motor Power graph
        return motor_power_graph


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
        flight_date = input.map_state()
        flight_id = get_flights(False)[flight_date]
        
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

    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # END: DATA ANALYSIS SCREEN 
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # START: UPLOAD SCREEN 
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    # Arbitrarly downloads this random doc -> functionality needs to change
    @session.download(
        filename=lambda: f"{date.today().isoformat()}-{np.random.randint(100,999)}.csv"
    )
    async def downloadData():
        await asyncio.sleep(0.25)
        yield "one,two,three\n"

    # Function -------------------------------------------------------------------------------------------------------------------------------------------
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
        
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # END: UPLOAD SCREEN 
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------

# Get the App Ready and Host
app = App(app_ui, server, debug=True)
