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
from datetime import datetime, timedelta
import simulation
import os

flight_operation_dictionary = {"Activity": [], "Time (minutes)": []}

# Getting initial data
flights = query_flights()

# Get the list of activities from labeled_activities_view
list_of_activities = flights.get_flight_activities()

# Getting the dates to be used in the ML UI:
# Get current date
current_date = datetime.now().date()
string_current_date = current_date.strftime("%Y-%m-%d")

# Get tomorrow's date
tomorrow_date = current_date + timedelta(days=1)
string_tomorrow_date = tomorrow_date.strftime("%Y-%m-%d")

# Get the day after tomorrow's date
day_after_tomorrow_date = current_date + timedelta(days=2)
string_day_after_tomorrow_date = day_after_tomorrow_date.strftime("%Y-%m-%d")

# Create a list and add the dates
list_of_dates = [string_current_date, string_tomorrow_date, string_day_after_tomorrow_date]

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
                        'Heading', 'Stall Diff Pressure', 'QNG', 'Outside Air Temperature', 'ISO Leakage Current', 'Weather ID', 'Weather Date', 'Weather Time UTC', 'Temperature','Dewpoint',
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
    # log_date = datetime.strptime(log_content.strip(), "%b %d, %Y at %I:%M %p")
    # formatted_date = log_date.strftime("%b %d, %Y at %I:%M %p")
    
    return log_content


# Function -------------------------------------------------------------------------------------------------------------------------------------------------------

app_ui = ui.page_fillable(
    # {"style": "color: blue"},
    shinyswatch.theme.zephyr(),
    ui.navset_card_pill(  
        # ===============================================================================================================================================================
        # START: UPLOAD SCREEN
        # ===============================================================================================================================================================
        ui.nav_panel("ElectriFly", "Homepage content"),
        ui.nav_panel("Data Preview",
            # Column selection panel
            ui.div(
                # Dropdown with checkboxes
                ui.input_selectize("selected_cols", "Choose Columns to Preview", choices=list(uploaded_cols().columns), multiple=True),
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
        # ===============================================================================================================================================================
        # End: UPLOAD SCREEN
        # ===============================================================================================================================================================
        ),
        ui.nav_menu("Data Analysis",
                                        
            # ===============================================================================================================================================================
            # START: Recommended Graphs Tab
            # ===============================================================================================================================================================
            ui.nav_panel("Data Visualization", 
                div(HTML("<h2> Data Visualization </h2>")),
                div(HTML("<hr>")),
                ui.card(
                    ui.card_header("Welcome to ElectriFly's Data Analytics Interface!"),
                    ui.p("Unlock the power of your data with our intuitive and powerful user interface designed specifically for data analytics. Our platform empowers you to transform raw data into actionable insights, enabling you to make informed decisions and drive your business forward.")
                    ,min_height = "150px"
                ),  
                div(HTML("<hr>")),
                div(HTML("<h4> Single Date Graphs </h4>")),
                ui.row(
                    ui.column(6, ui.input_selectize("singular_flight_date", "Choose Flight Date:", get_flights())),
                    ui.column(6, ui.output_text("num_circuits"))
                ),
                ui.row(
                    # Put columns within the rows, the column first param is the width, your total widths add up to 12
                    ui.column(6, div(HTML("<p><b>Weather Data for Selected Flight</b></p>")), div(HTML("<hr>")), ui.panel_main(ui.output_table("weather_interactive"))),
                    ui.column(6, div(HTML("<p><b>Flight Map</b></p>")), div(HTML("<hr>")), output_widget("lat_long_map")),
                ),
                div(HTML("<hr>")),
                div(HTML("<hr>")),
                div(HTML("<h4> Multiple Date Graphs </h4>")),
                ui.row(
                    ui.column(12, ui.input_selectize("multi_select_flight_dates", "Choose Flight Date(s):", get_flights(), multiple=True))
                ),
                ui.row(
                    ui.column(6, div(HTML("<p><b>SOC vs Time Across Multiple Flights</b></p>")), div(HTML("<hr>")), ui.output_plot("soc_time_graph")),
                    ui.column(6, div(HTML("<p><b>Power Setting vs Time Across Multiple Flights</b></p>")), div(HTML("<hr>")), ui.output_plot("power_time_graph"))
                ),
                div(HTML("<hr>"))
            ),
            #  ===============================================================================================================================================================
            # START: CUSTOM GRAPH TAB
            # ===============================================================================================================================================================
            ui.nav_panel("Custom Graph",
                div(HTML("<h2> Custom Graph </h2>")),
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
            ui.nav_panel("Statistical Insights", 
                div(HTML("<h2> Statistical Insights </h2>")),
                div(HTML("<hr>")),
                ui.input_selectize("statistical_time", "Choose Flight Date:", get_flights(["fw_flight_id", "flight_date"], "labeled_activities_view")),
                ui.row( 
                    # put columns within the rows, the column first param is the width, your total widths add up to 12
                    ui.column(6, 
                        div(HTML("<hr>")),
                        div(HTML("<p><b>Motor Power vs SOC Rate of Change</b></p>")),
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
                        div(HTML("<p><b>Plane Operations vs SOC Rate of Change Statistics </b></p>")),
                        div(HTML("<hr>")),
                        ui.panel_main(ui.output_table("soc_roc_table"))
                    ),  
                ),
            ),
        ),
        ui.nav_menu("Flight Planning",
            # ===============================================================================================================================================================
            # START: Flight Scheduling TAB
            # ===============================================================================================================================================================
            ui.nav_panel("Flight Scheduling",
            div(HTML("<h2> Flight Scheduling </h2>")),
            div(HTML("<hr>")),
            ui.card(
                ui.card_header("Welcome to ElectriFly's Simulation Interface!"),
                #ui.p
                    div(HTML("""<p>The Three Day Flight Forecast determines the safety of flights for each 15 minute block of time for today, and the next two days after.
                        <br>Upcoming Flights for Today provides times today when flights can safely be scheduled.</p>
                        
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
                        ui.card(
                            ui.output_table("simulation_table")
                        ),
                    ),
                    ui.column(6,
                        div(HTML("<hr>")),
                        div(HTML("<p><b>Upcoming Flights for Today</b></p>")),
                        div(HTML("<hr>")),
                        ui.card(
                            ui.output_table("flight_planning_table")
                        ),
                    ),
                ),
            ),
            
            # ===============================================================================================================================================================
            # START: Flight Exercise Planning TAB
            # ===============================================================================================================================================================
            ui.nav_panel("Flight Exercise Planning", 
            div(HTML("<h2> Flight Exercise Planning </h2>")),
                # Selecting the date
                ui.row(
                    ui.column(6,
                        div(HTML("<hr>")),
                        ui.input_selectize("date_operations", "Choose Flight Date:", list_of_dates, multiple=False, width=6, selected=None),
                        div(HTML("<hr>"))
                    ),
                    ui.column(6,
                        div(HTML("<hr>")),
                        ui.output_ui("time_selector"),
                        div(HTML("<hr>"))
                    )
                ),
                ui.layout_columns(
                    ui.card(
                        div(HTML("<hr>")),
                        ui.input_selectize("flight_operations", "Choose Flight Operation:", list_of_activities, multiple=False, width=6, selected=None),
                        div(HTML("<hr>")),
                        ui.output_ui("duration_of_activity"),
                        div(HTML("<hr>")),
                        ui.input_action_button("select_activity", "Add activity"),
                        height="100%"
                    ),
                    ui.card(
                        ui.output_data_frame("activity_selection_output"),
                        height="100%"
                    ),
                    ui.card(
                        ui.input_action_button("reset_activity", "Reset All Activities"),
                        height="100%"
                    ),
                    col_widths=(3, 6, 3)
                )              
            )
        ),
        id="tab",  
    )  
)

# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
def server(input: Inputs, output: Outputs, session: Session):
  
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
    
    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.text
    def most_recent_run():
        most_recent_run_time = get_most_recent_run_time()  # Run the scraper.py script when the app is loaded
        return f"Data was last refreshed at: {most_recent_run_time}"  
    
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # END: UPLOAD SCREEN 
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # START: SIMULATION SCREEN 
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------

    # For the selection of the flight operations.
    table_data_show = reactive.Value(-1)

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
                             [{'selector': 'td', 'props': 'border: 5px solid white;'}])
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
    
    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.ui
    @reactive.event(input.date_operations)
    def time_selector():
        flight_dates = input.date_operations()

        if flight_dates == "":
            return ui.output_text("Please select a date to fly")
        else:
            return ui.input_selectize("testing", "Choose start time of flight:", ["12:00 AM", "12:15 AM", "12:30 AM", "12:45 AM", "01:00 AM", "01:15 AM", "01:30 AM", "01:45 AM", "02:00 AM", "02:15 AM", "02:30 AM", "02:45 AM", "03:00 AM", "03:15 AM", "03:30 AM", "03:45 AM", "04:00 AM", "04:15 AM", "04:30 AM", "04:45 AM", "05:00 AM", "05:15 AM", "05:30 AM", "05:45 AM", "06:00 AM", "06:15 AM", "06:30 AM", "06:45 AM", "07:00 AM", "07:15 AM", "07:30 AM", "07:45 AM", "08:00 AM", "08:15 AM", "08:30 AM", "08:45 AM", "09:00 AM", "09:15 AM", "09:30 AM", "09:45 AM", "10:00 AM", "10:15 AM", "10:30 AM", "10:45 AM", "11:00 AM", "11:15 AM", "11:30 AM", "11:45 AM", "12:00 PM", "12:15 PM", "12:30 PM", "12:45 PM", "01:00 PM", "01:15 PM", "01:30 PM", "01:45 PM", "02:00 PM", "02:15 PM", "02:30 PM", "02:45 PM", "03:00 PM", "03:15 PM", "03:30 PM", "03:45 PM", "04:00 PM", "04:15 PM", "04:30 PM", "04:45 PM", "05:00 PM", "05:15 PM", "05:30 PM", "05:45 PM", "06:00 PM", "06:15 PM", "06:30 PM", "06:45 PM", "07:00 PM", "07:15 PM", "07:30 PM", "07:45 PM", "08:00 PM", "08:15 PM", "08:30 PM", "08:45 PM", "09:00 PM", "09:15 PM", "09:30 PM", "09:45 PM", "10:00 PM", "10:15 PM", "10:30 PM", "10:45 PM", "11:00 PM", "11:15 PM", "11:30 PM", "11:45 PM"])

    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.ui
    @reactive.event(input.flight_operations)
    def duration_of_activity():
        flight_activity = input.flight_operations()

        if flight_activity == "":
            return ui.output_text("Please select a flight activity")
        else:
            return ui.input_numeric("duration_chooser", f"Choose number of minutes for {flight_activity}:", 1, min=1, max=60)

    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @output
    @render.data_frame 
    @reactive.event(table_data_show)
    def activity_selection_output():

        # Get the global flight holder variable
        global flight_operation_dictionary

        # Make it a data frame
        flight_operation_output_table = pd.DataFrame(flight_operation_dictionary)

        # Return that data frame
        return flight_operation_output_table
    
    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @reactive.effect
    @reactive.event(input.reset_activity)
    def _():
        
        # Get the global flight holder variable
        global flight_operation_dictionary

        # Get the reactive variable:
        reactive_var = table_data_show.get() - 1

        # Clear all of the activities and times in the variable
        flight_operation_dictionary["Activity"].clear()
        flight_operation_dictionary["Time (minutes)"].clear()

        # Set the data show to 0
        table_data_show.set(reactive_var)

        

    # Function -------------------------------------------------------------------------------------------------------------------------------------------
    @reactive.effect
    @reactive.event(input.select_activity)
    def _():

        # Get the global flight holder variable
        global flight_operation_dictionary

        # Get the reactive variable:
        reactive_var = table_data_show.get() + 1

        # Get the inputs from the flight operation and time selection criteria
        operation = input.flight_operations()
        operation_duration = input.duration_chooser()

        # Append all the activities and times in the variable
        flight_operation_dictionary["Activity"].append(operation)
        flight_operation_dictionary["Time (minutes)"].append(operation_duration)

        # Set the data show to 1
        table_data_show.set(reactive_var)


    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # END: SIMULATION SCREEN 
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------

# Get the App Ready and Host
app = App(app_ui, server, debug=True)
