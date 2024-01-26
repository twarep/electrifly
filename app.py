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
from datetime import date
import numpy as np
from os import listdir, getenv
from os.path import isfile, join
from dotenv import load_dotenv
import shiny.experimental as x
from shinywidgets import output_widget, render_widget
import sqlalchemy as sa
import simulation
import os

# Getting initial data
flights = query_flights()

# Get the list of activities from labeled_activities_view
list_of_activities = flights.get_flight_activities()

# List of variables
custom_variables_columns = {
    "Time (min)": ["time_min"], 
    "Current": ["bat_1_current", "bat_2_current"], 
    "Voltage": ["bat_1_voltage", "bat_2_voltage"], 
    "State-of-Charge": ["bat_1_soc", "bat_2_soc"], 
    "State-of-Health": ["bat_1_soh", "bat_2_soh"], 
    "Average Cell Temperature": ["bat_1_avg_cell_temp", "bat_2_avg_cell_temp"],
    "Minimum Cell Temperature": ["bat_1_min_cell_temp", "bat_2_min_cell_temp"],
    "Maximum Cell Temperature": ["bat_1_max_cell_temp", "bat_2_max_cell_temp"],
    "Minimum Cell Volt": ["bat_1_min_cell_volt", "bat_2_min_cell_volt"],
    "Maximum Cell Volt": ["bat_1_max_cell_volt", "bat_2_max_cell_volt"],
    "Inverter Cooling Temperature": ["inverter_cooling_temp_1", "inverter_cooling_temp_1"],
    "Motor RPM": ["motor_rpm"],
    "Motor Power": ["motor_power"],
    "Motor Temperature": ["motor_temp"],
    "Requested Torque": ["requested_torque"],
    "Indicated Air Speed": ["ias"],
    "Pressure Altitude": ["pressure_alt"],
}
custom_variables = list(custom_variables_columns.keys())


# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
#database connection 
def connect_to_db(provider: str):
    load_dotenv()
    provider == "PostgreSQL"
    db_url = "postgresql+psycopg2" + os.getenv('DATABASE_URL')[8:]
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
    # Rename columns to be human readable
    readable_columns = ['Fw Flight ID','Flight Date','Flight ID','Time (Min)','Bat 1 Current','Bat 1 Voltage','Bat 2 Current','Bat 2 Voltage','Bat 1 SOC','Bat 2 SOC',
                        'Bat 1 SOH', 'Bat 2 SOH', 'Bat 1 Min Cell Temp', 'Bat 2 Min Cell Temp', 'Bat 1 Max Cell Temp', 'Bat 2 Max Cell Temp', 'Bat 1 Avg Cell Temp', 'Bat 2 Avg Cell Temp', 'Bat 1 Min Cell Volt', 'Bat 2 Min Cell Volt',
                        'Bat 1 Max Cell Volt', 'Bat 2 Max Cell Volt', 'Requested Torque', 'Motor RPM', 'Motor Power', 'Motor Temp', 'Indicated Air Speed', 'Stall Warn Active', 'Inverter Temp', 'Bat 1 Cooling Temp',
                        'Inverter Cooling Temp 1', 'Inverter Cooling Temp 2', 'Remaining Flight Time', 'Pressure Altitude', 'Latitude', 'Longitude', 'Ground Speed', 'Pitch', 'Roll', 'Time Stamp',
                        'Heading', 'Stall Diff Pressure', 'QNG', 'Outside Air Temperature', 'ISO Leakage Current', 'ID', 'Weather Date', 'Weather Time UTC', 'Temperature','Dewpoint',
                        'Relative Humidity','Wind Direction', 'Wind Speed', 'Pressure Altimeter','Sea Level Pressure', 'Visibility', 'Wind Gust', 'Sky Coverage 1', 'Sky Coverage 2', 'Sky Coverage 3', 
                        'Sky Coverage 4', 'Sky Level 1', 'Sky Level 2','Sky Level 3','Sky Level 4','Weather Codes', 'Metar']
    uploaded_data_df.columns = readable_columns # TEST IF THIS WORKS
    engine.dispose()
    return uploaded_data_df


# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
def uploaded_cols(): 
    uploaded_data_df = uploaded_data()
    all_uploaded_cols = uploaded_data_df.iloc[:, 1:]
    return all_uploaded_cols


# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
def get_flights(columns=["id", "flight_date", "flight_time_utc"], table="flights"):
    """
    The function uses the query_flights class to get all the flights ids and dates in a dictionary of key: value --> flight_date: flight_id. 

    Parameters:
        date: Boolean value to specify if you only want to return a list of flight dates from the DB.

    Returns:
        if date is FALSE --> flight_date: dictionary of flight_date: flight_id pairs
    """
    flights = query_flights()

    flight_data = flights.get_flight_id_and_dates(columns, table)
    
    return flight_data


# Function ---------------------------------------------------------------------------------------------------------------------------------------------------------
def get_most_recent_run_time():
    log_file = 'scraper_run_log.txt'
    with open(log_file, 'r') as file:
        log_content = file.read()

    return log_content


# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
app_ui = ui.page_navbar(
    # {"style": "color: blue"},
    shinyswatch.theme.zephyr(),
    # ===============================================================================================================================================================
    # START: UPLOAD SCREEN
    # ===============================================================================================================================================================
    ui.nav("Upload Data",
        # Column selection panel
        ui.div(
            # Dropdown with checkboxes
            ui.input_selectize("selected_cols", "Select Columns to Preview", choices=list(uploaded_cols().columns), multiple=True),
            style="margin-top:40px;"
        ),  
        # Table header
        ui.div(
            ui.include_css("bootstrap.css"), ui.h4("Most Recent Flight and Weather Data Records"), 
            style="margin-top: 3px;"
        ), 
        # Table ouptut
        ui.div(
            ui.output_data_frame("uploaded_data_df"),
            ui.include_css("bootstrap.css"),
            style="margin-top: 2px; max-height: 3000px;"
        ),
        # Display the most recent run time
        ui.div(
            ui.div(ui.output_text("most_recent_run")),
            style="margin-top: 10px;"
        ),
    ),
    # ===============================================================================================================================================================
    # End: UPLOAD SCREEN
    # ===============================================================================================================================================================
    # ===============================================================================================================================================================
    # START: DATA ANALYSIS SCREEN 
    # ===============================================================================================================================================================
    ui.nav("Data Analysis", 
        ui.include_css("bootstrap.css"),
        x.ui.card(
            x.ui.card_header("Welcome to ElectriFly's Data Analytics Interface!"),
            x.ui.card_body("""Unlock the power of your data with our intuitive and powerful user interface designed specifically for data analytics. 
                            Our platform empowers you to transform raw data into actionable insights, enabling you to make informed decisions and drive your business forward.""")
        ),
        # This creates the tabs between the recommended graph screen and the insights
        ui.navset_tab(
            # ===============================================================================================================================================================
            # START: Recommended Graphs Tab
            # ===============================================================================================================================================================
            ui.nav("Recommended Graphs", 
                div(HTML("<hr>")),
                div(HTML("<h3> Single Date Graphs </h3>")),
                ui.row(
                    ui.column(6, ui.input_selectize("singular_flight_date", "Choose Flight Date:", get_flights())),
                    ui.column(6, ui.output_text("num_circuits"))
                ),
                ui.row(
                    # Put columns within the rows, the column first param is the width, your total widths add up to 12
                    ui.column(6, div(HTML("<p><b>Weather Data for Selected Flights</b></p>")), div(HTML("<hr>")), ui.panel_main(ui.output_table("weather_interactive"))),
                    ui.column(6, div(HTML("<p><b>Flight Map</b></p>")), div(HTML("<hr>")), output_widget("lat_long_map")),
                ),
                div(HTML("<hr>")),
                div(HTML("<hr>")),
                div(HTML("<h3> Multiple Date Graphs </h3>")),
                ui.row(
                    ui.column(12, ui.input_selectize("multi_select_flight_dates", "Choose Flight Date(s):", get_flights(), multiple=True))
                ),
                ui.row(
                    ui.column(6, div(HTML("<p><b>SOC vs. Time Across Multiple Flights</b></p>")), div(HTML("<hr>")), ui.output_plot("soc_time_graph")),
                    ui.column(6, div(HTML("<p><b>Power Setting vs. Time Across Multiple Flights</b></p>")), div(HTML("<hr>")), ui.output_plot("power_time_graph"))
                ),
                div(HTML("<hr>"))
            ),
            # ===============================================================================================================================================================
            # START: CUSTOM GRAPH TAB
            # ===============================================================================================================================================================
            ui.nav("Custom Graph",
                div(HTML("<hr>")),
                div(HTML("""<p>The <b>Custom Graphs</b> feature is a one-of-a-kind feature empowering 
                         you with the ability to visualize flight data the way you want. Here is a simple way to use the custom graph:</p>""")),
                div(
                    HTML("""<ol> 
                        <li> Select the date for which you want to view the data, and </li>
                        <li> Select the type of graph you want to see, then </li>
                        <li> Select the X (independent) variable on the graph, </li>
                        <li> Lastly select the Y (dependent) variable on the graph. </li>
                        </ol>"""
                    )
                ),
                div(HTML("<hr>")),
                ui.row(
                    ui.column(3, ui.input_selectize("select_flights", "Flight Date:", get_flights())),
                    ui.column(3, ui.input_selectize("select_graph", "Graph Type:", ["Line Plot", "Scatter Plot"])),
                    ui.column(3, ui.input_selectize("select_x_variable", "Independent (X) Variable:", custom_variables, selected=custom_variables[0])),
                    ui.column(3, ui.input_selectize("select_y_variable", "Dependent (Y) Variable:", custom_variables, selected=custom_variables[3])),
                ),
                ui.output_plot("custom_graph")
            ),
            # ===============================================================================================================================================================
            # START: Statistical Insights TAB
            # ===============================================================================================================================================================
            ui.nav("Statistical Insights", 
                div(HTML("<hr>")),
                ui.input_selectize("statistical_time", "Choose Flight Date:", get_flights(["fw_flight_id", "flight_date"], "labeled_activities_view")),
                ui.row( 
                    # put columns within the rows, the column first param is the width, your total widths add up to 12
                    ui.column(6, 
                        div(HTML("<hr>")),
                        div(HTML("<p><b>Motor Power vs. SOC Rate of Change</b></p>")),
                        div(HTML("<hr>")),
                        ui.layout_sidebar(
                            ui.panel_sidebar(
                                ui.input_selectize("select_activities", "Choose activities:", list_of_activities, selected=list_of_activities, multiple=True),
                                width=3
                            ),
                            ui.panel_main(ui.output_plot("power_soc_rate_of_change_scatter_plot")),
                            position='right'
                        )
                    ),
                    ui.column(6,
                        div(HTML("<hr>")),
                        div(HTML("<p><b>Plane Operations vs. SOC Rate of Change Statistics </b></p>")),
                        div(HTML("<hr>")),
                        ui.panel_main(ui.output_table("soc_roc_table"))
                    ),  
                ),
            ),
            # ===============================================================================================================================================================
            # END: Statistical Insights TAB
            # ===============================================================================================================================================================
        ),    
    ),  
    # ===============================================================================================================================================================
    # END: DATA ANALYSIS SCREEN 
    # ===============================================================================================================================================================
    # ===============================================================================================================================================================
    # START: ML RECOMMENDATIONS SCREEN
    # ===============================================================================================================================================================
    ui.nav("Simulation", 
        ui.nav("Forecasting",
            ui.row( 
                ui.column(6,
                    div(HTML("<hr>")),
                    div(HTML("<p><b>Number of Feasible Flights</b></p>")),
                    div(HTML("<hr>")),
                    ui.panel_main(ui.output_table("simulation_table", style="width: 70%; height: 300px;")),
                ),
                ui.column(6,
                    div(HTML("<hr>")),
                    div(HTML("<p><b>Upcoming Flights for Today</b></p>")),
                    div(HTML("<hr>")),
                    ui.panel_main(ui.output_table("flight_planning_table", style="width: 70%; height: 300px;")),
                ),
            )
        ),
        ui.nav("Fligh Operations Modeling", 
            ui.input_selectize("flight_operations", "Choose Flight Date:", ["Take-off", "Stall", "Cruise"], multiple=True), 
            ui.output_text("showing_ml")
        ) 
    ),
    # ===============================================================================================================================================================
    # END: ML RECOMMENDATIONS SCREEN
    # ===============================================================================================================================================================
    title="ElectriFly",
)


# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
def server(input: Inputs, output: Outputs, session: Session):
  
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # START: DATA ANALYSIS SCREEN 
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------

    @render.text 
    def showing_ml():
        data = input.flight_operations()
        return f"Flight Operations chosen: {data}" 

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
        return weather_df 

    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.plot()
    def custom_graph():

        # Get all the inputs
        flight_id = input.select_flights()
        graph_type = input.select_graph()
        x_var_label = input.select_x_variable()
        y_var_label = input.select_y_variable()
        x_variables = custom_variables_columns[x_var_label]
        y_variables = custom_variables_columns[y_var_label]

        # Make the graph
        created_custom_graph = Graphing.custom_graph_creation(graph_type, flight_id, x_variables, y_variables, x_var_label, y_var_label)

        # Return the custom graph
        return created_custom_graph         

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
        The function uses the input from the 'power' parameter to get data on power vs. time for all the selected dates.

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
    def num_circuits():
        """
        Function uses a responsive text interface to show the number of circuits.

        Returns:
            query_result: A numeric value of the number of circuits
        """

        # Get the flight id
        flight_id = input.singular_flight_date()

        query_conn = query_flights()
        query_result = query_conn.get_number_of_circuits(flight_id)

        # Send number of flights with entire string --> The number of circuits for the chosen flight is: {query_result}
        return f"The number of circuits for the chosen flight is: {query_result}"
    
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
    
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # END: INSIGHTS SCREEN 
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
            default_columns = uploaded_data_df.loc[:,["Flight ID","Flight Date", "Weather Time UTC", "Time (Min)","Bat 1 SOC", 
                                               "Bat 2 SOC","Motor Power", "Motor Temp"]]
            return default_columns
        else:
            # Filter the DataFrame based on the selected columns
            filtered_df = uploaded_data_df.loc[:, selected_columns]
            return filtered_df
    @output
    @render.text
    def most_recent_run():
        most_recent_run_time = get_most_recent_run_time()  # Run the scraper.py script when the app is loaded
        return f"Last data retrieval: {most_recent_run_time}"  
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # END: UPLOAD SCREEN 
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # START: SIMULATION SCREEN 
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.table
    def simulation_table(): 
        # Apply conditional formatting
        #cell_style = lambda val: f"background-color: {'red' if val == 'red' else 'green'};"
        styled_data = simulation.result_table_colours.style.applymap(style_cell)
        # new = styled_data.set_table_styles()
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
    @output
    @render.table
    def flight_planning_table(): 
        # Apply conditional formatting
        #cell_style = lambda val: f"background-color: {'red' if val == 'red' else 'green'};"
        flight_plan = simulation.feasible_flights
        # new = styled_data.set_table_styles()
        return flight_plan
    
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # END: SIMULATION SCREEN 
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------

# Get the App Ready and Host
app = App(app_ui, server, debug=True)
