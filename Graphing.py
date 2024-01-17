from flight_querying import query_flights
from weather_querying import query_weather
import plotly.graph_objects as go
from dotenv import load_dotenv
import numpy as np
import os
import pandas as pd
import plotly.express as px
import plotly.io as pio
import matplotlib.pyplot as plt


# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
def create_mapbox_map_per_flight(flight_id: int):
    """ 
    Function takes a flight id and uses the Mapbox mapping feature from plotly and a MAPBOX_PUBLIC_TOKEN to create a map of the fligt's 
    latitude and longitude coordinates.

    Parameter:
        flight_id: A integer number corresponding with the flight map you want.

    Returns:
        fig: A plotly figure object with Scattermapbox functionality
        latitude: A numpy array of Double data type latitudes for the flight.
        longitude: A numpy array of Double data type longitudes for the flight.
    """

    # Load .env file
    load_dotenv()

    # Get mapbox token to run the code.
    mapbox_access_token = os.getenv('MAPBOX_PUBLIC_TOKEN')

    # Specify Waterloo Wellington Flight Center coordinates and specify the columns to query
    wwfc_lat = 43.45567935107457
    wwfc_lon = -80.3881582036048
    query_columns = ['lat', 'lng']

    # Get Flight data for specific flight.
    query_conn = query_flights()
    query_result = query_conn.get_flight_data_on_id(query_columns, flight_id)
    query_result.replace(0, np.nan, inplace=True)

    # Fine tune lat and long on the dataframe
    latitude = query_result["lat"].to_numpy()
    longitude = query_result["lng"].to_numpy() * (-1)

    # Graphing
    fig = go.Figure(go.Scattermapbox(
        lat=latitude,
        lon=longitude,
        mode="lines",
        marker=go.scattermapbox.Marker(
            size=5
        ),
        text=['WWFC'],
    ))

    # Update the figure layout
    fig.update_layout(
        hovermode='closest',
        margin=dict(l=5, r=5, t=5, b=5),
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=wwfc_lat,
                lon=wwfc_lon
            ),
            pitch=0,
            zoom=12,
        )
    )

    return fig, latitude, longitude


# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
def soc_graph(flight_ids: list, flight_dates: list):
    """
    The function takes in flight ids and dates and creates a single matplotlib figure line graph of soc vs. time with warning and danger zones. 

    Parameters:
        flight_ids: A list of all flight ids form the DB. Index should corresponds with the flight_dates index.
        flight_dates: A list of all flight dates form the DB. Index should corresponds with the flight_ids index.

    Returns:
        soc_ax: The matplotlib figure axis with stored soc vs. time graph data and other supports.
    """

    # Make flight db connection
    flight_db_conn = query_flights()
    flight_data = flight_db_conn.get_flight_soc_and_time(flight_ids)

    # Set warning zone, and danger zone ranges
    x_zone = [0, 0, 60, 60]
    warning_zone = [15.01, 30, 30, 15.01]
    danger_zone = [0, 15, 15, 0]

    # Set Plot
    soc_figure = plt.figure()
    soc_ax = soc_figure.add_subplot(1, 1, 1)
    soc_figure.tight_layout()

    # Fill ranges
    soc_ax.fill(x_zone, warning_zone, c="yellow", alpha=0.5)
    soc_ax.fill(x_zone, danger_zone, c='r', alpha=0.5)

    # Add text to fill ranges
    soc_ax.text(0.2, 20.5, 'Warning', fontweight='bold')
    soc_ax.text(0.2, 5.5, 'Danger', fontweight='bold', c='white')

    # Plot the graphs
    for i in range(0, len(flight_ids)):

        # Define the date and id
        id = flight_ids[i]
        date = flight_dates[i]

        # Get the soc and time and plot it with a legend label
        soc = flight_data[id]['soc']
        time = flight_data[id]['time_min']
        soc_ax.plot(time, soc, label=date)
    
    # Add labels and legend to plot
    soc_ax.set_xlim([0, 55])
    soc_ax.set_ylim([-1, 101])
    soc_ax.set_xlabel("time (min)")
    soc_ax.set_ylabel("SOC")
    soc_ax.set_title("Time vs SOC")
    
    # plt.legend(loc="lower left")
    soc_ax.legend(loc='upper left', fontsize="7", bbox_to_anchor= (1.01, 1.01), ncol=1,
            borderaxespad=0, frameon=False)

    return soc_ax


# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
def power_graph(flight_ids: list, flight_dates: list):
    """
    The function takes in flight ids and dates and creates a single matplotlib figure scatter graph of motor_power vs. time. 

    Parameters:
        flight_ids: A list of all flight ids form the DB. Index should corresponds with the flight_dates index.
        flight_dates: A list of all flight dates form the DB. Index should corresponds with the flight_ids index.

    Returns:
        power_ax: The matplotlib figure axis with stored motor_power vs. time graph data and other supports.
    """

    # Make flight db connection
    flight_db_conn = query_flights()
    flight_data = flight_db_conn.get_flight_motor_power_and_time(flight_ids)

    # Set Plot
    power_figure = plt.figure()
    power_ax = power_figure.add_subplot(1, 1, 1)
    power_figure.tight_layout()

    # Plot the graphs
    for i in range(0, len(flight_ids)):

        # Define the date and id
        id = flight_ids[i]
        date = flight_dates[i]

        # Get the soc and time and plot it with a legend label
        motor_power = flight_data[id]['motor_power']
        time = flight_data[id]['time_min']
        power_ax.scatter(time, motor_power, s=10, label=date)
    
    # Add labels and legend to plot
    power_ax.set_xlim([0, 55])
    power_ax.set_ylim([-1, 70])
    power_ax.set_xlabel("time (min)")
    power_ax.set_ylabel("Motor power (kilowatts-KW)")
    power_ax.set_title("Time vs Motor power")
    
    # plt.legend(loc="lower left")
    power_ax.legend(loc='upper left', fontsize="7", bbox_to_anchor= (1.01, 1.01), ncol=1,
            borderaxespad=0, frameon=False)

    return power_ax


# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
def power_soc_rate_scatterplot(flight_id: list, flight_dates: list, activities_filter: list):
    """
    The function takes in flight ids and dates and creates a single matplotlib figure scatter plot of motor_power vs. SOC rate of change.
    A legend of activities is also included. 
    Parameters:
        flight_ids: A list of all flight ids form the DB. Index should corresponds with the flight_dates index.
        flight_dates: A list of all flight dates form the DB. Index should corresponds with the flight_ids index.
        activities_filter: A list of all flight activities the user would like to filter by.
    Returns:
        scatter_ax: The matplotlib figure axis with stored scatter plot data and other supports.
    """

    # Make flight db connection
    flight_db_conn = query_flights()
    flight_data = flight_db_conn.get_flight_power_soc_rate(flight_id, activities_filter)

    # Set Plot
    scatter_figure = plt.figure()
    scatter_ax = scatter_figure.add_subplot(1, 1, 1)
    scatter_figure.tight_layout()

    # Get the motor power and soc rate
    motor_power = flight_data[flight_id]['motor_power']
    soc_rate_of_change = flight_data[flight_id]['soc_rate_of_change']

    # Get activities
    activity = flight_data[flight_id]['activity']

    # Determine unique activities and assign colors or markers
    unique_activities = np.unique(activity)

    # gets colours from the jet colour map
    colors = plt.cm.jet(np.linspace(0, 1, len(unique_activities))) 

    # assigns each unique activity to a colour
    activity_color_map = dict(zip(unique_activities, colors)) 
    
    # Iterate over each unique activity type
    for act in unique_activities:
        
        # Create a boolean mask where the condition (activity == act) is True
        # This mask is used to select only the data points corresponding to the current activity
        act_mask = activity == act

        # Plot the scatter points for the current activity
        # motor_power[act_mask] and soc_rate_of_change[act_mask] select the data points that correspond to the current activity
        scatter_ax.scatter(motor_power[act_mask], soc_rate_of_change[act_mask],
                            s=10, color=activity_color_map[act], label=act)
        
        # Calculate and plot line of best fit for each activity
        a, b = np.polyfit(motor_power[act_mask], soc_rate_of_change[act_mask], 1)
        scatter_ax.plot(motor_power[act_mask], a*motor_power[act_mask] + b, 
                        color=activity_color_map[act], linestyle='--', linewidth=2)

    scatter_ax.set_xlabel("Motor Power")
    scatter_ax.set_ylabel("SOC Rate of Change")
    scatter_ax.set_title("Motor Power vs. SOC Rate of Change Scatterplot")

    # Create a legend with unique entries
    # Handles are references to the plot elements, and labels are the text descriptions for these elements
    handles, labels = scatter_ax.get_legend_handles_labels()

    # Create a unique list of handle-label pairs
    # This is to ensure that each label (and its corresponding handle) appears only once in the legend
    unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]

    # Create and set the legend for the scatter plot
    # *zip(*unique) unpacks the unique handle-label pairs into separate tuples of handles and labels
    scatter_ax.legend(*zip(*unique), loc='upper left', fontsize="7", bbox_to_anchor=(1.01, 1.01))

    return scatter_ax


# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
def custom_graph_creation(graph_type: str, flight_id, x_data_label: str, y_data_label: str):

    # Make the query connection
    flight_db_conn = query_flights()
    query_result = flight_db_conn.get_flight_data_on_id([x_data_label, y_data_label], flight_id)
    x_ax_data = query_result[x_data_label].to_numpy()
    y_ax_data = query_result[y_data_label].to_numpy()

    # Set Plot
    custom_figure = plt.figure()
    custom_ax = custom_figure.add_subplot(1, 1, 1)
    custom_figure.tight_layout()

    # For each graph type graph different things.
    if graph_type == "Line Plot":
        custom_ax.plot(x_ax_data, y_ax_data)

    elif graph_type == "Scatter Plot":
        custom_ax.scatter(x_ax_data, y_ax_data, s=5, c='blue')
    
    # Add labels and legend to plot
    custom_ax.set_xlabel(x_data_label)
    custom_ax.set_ylabel(y_data_label)
    custom_ax.set_title(f"{x_data_label} vs {y_data_label}")

    # Return the axis
    return custom_ax
