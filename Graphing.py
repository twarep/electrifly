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
def soc_graph(flight_ids: list):
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
    soc_figure = plt.figure(figsize=(5, 5))

    # Fill ranges
    plt.fill(x_zone, warning_zone, c="yellow", alpha=0.5)
    plt.fill(x_zone, danger_zone, c='r', alpha=0.5)

    # Add text to fill ranges
    plt.text(0.2, 20.5, 'Warning', fontweight='bold')
    plt.text(0.2, 5.5, 'Danger', fontweight='bold', c='white')

    # Plot the graphs
    for i in range(0, len(flight_ids)):

        # Define the date and id
        id = flight_ids[i]

        # Get the soc and time and plot it with a legend label
        soc = flight_data[id]['soc']
        time = flight_data[id]['time_min']
        date = flight_data[id]["date"]
        plt.plot(time, soc, label=date)
    
    # Add labels and legend to plot
    plt.xlim([0, 55])
    plt.ylim([-1, 101])
    plt.xlabel("time (min)")
    plt.ylabel("SOC")
    plt.title("Time vs SOC")
    
    # plt.legend(loc="lower left")
    plt.legend(loc='lower left', fontsize="9", bbox_to_anchor= (0, -0.2), ncol=4,
            borderaxespad=0, frameon=False)

    return soc_figure


# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
def power_graph(flight_ids: list):
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
    power_figure = plt.figure(figsize=(6, 6))

    # Plot the graphs
    for i in range(0, len(flight_ids)):

        # Define the date and id
        id = flight_ids[i]

        # Get the soc and time and plot it with a legend label
        motor_power = flight_data[id]['motor_power']
        time = flight_data[id]['time_min']
        date = flight_data[id]["date"]
        plt.plot(time, motor_power, label=date)
    
    # Add labels and legend to plot
    plt.xlim([0, 55])
    plt.ylim([-1, 70])
    plt.xlabel("time (min)")
    plt.ylabel("Motor power (kilowatts-KW)")
    plt.title("Time vs Motor power")
    
    # plt.legend(loc="lower left")
    plt.legend(loc='lower left', fontsize="9", bbox_to_anchor= (0, -0.2), ncol=4,
            borderaxespad=0, frameon=False)

    return power_figure


# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
def power_soc_rate_scatterplot(flight_id: list, activities_filter: list):
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
    scatter_figure = plt.figure(figsize=(6, 6))
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
        plt.scatter(motor_power[act_mask], soc_rate_of_change[act_mask],
                            s=10, color=activity_color_map[act], label=act)
        
        # Calculate and plot line of best fit for each activity
        a, b = np.polyfit(motor_power[act_mask], soc_rate_of_change[act_mask], 1)
        plt.plot(motor_power[act_mask], a*motor_power[act_mask] + b, 
                        color=activity_color_map[act], linestyle='--', linewidth=2)

    plt.xlabel("Motor Power")
    plt.ylabel("SOC Rate of Change (% change every 0.5 min)")
    plt.title("Motor Power vs. SOC Rate of Change Scatterplot")

    # Create a legend with unique entries
    # Handles are references to the plot elements, and labels are the text descriptions for these elements
    handles, labels = scatter_ax.get_legend_handles_labels()

    # Create a unique list of handle-label pairs
    # This is to ensure that each label (and its corresponding handle) appears only once in the legend
    unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]

    # Create and set the legend for the scatter plot
    # *zip(*unique) unpacks the unique handle-label pairs into separate tuples of handles and labels
    plt.legend(*zip(*unique), loc='upper right', fontsize="7")

    return scatter_figure

# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
def soh_soc_rate_scatterplot(flight_ids: list):
    """
    The function takes in flight ids and dates and creates a single matplotlib figure scatter plot of SOH vs. SOC rate of change.
    A legend of dates is also included. 
    Parameters:
        flight_ids: A list of all flight ids form the DB. Index should corresponds with the flight_dates index.
        flight_dates: A list of all flight dates form the DB. Index should corresponds with the flight_ids index.
    Returns:
        scatter_figure: The matplotlib figure axis with stored scatter plot data and other supports.
    """
    
    # Set Plot
    scatter_figure = plt.figure(figsize=(6, 6))
    scatter_figure.tight_layout()

    # Plot the graphs
    for i in range(0, len(flight_ids)):
        # Make flight db connection
        print("inside for loop")
        flight_db_conn = query_flights()
        flight_data = flight_db_conn.get_flight_soh_soc_rate(flight_ids[i])
        # Define the date and id
        id = flight_ids[i]

        # Get the soh and soc and plot it with a legend label
        soh = flight_data[id]['soh']
        soc_rate_of_change = flight_data[id]['soc_rate_of_change']
        date = flight_data[id]["dates"]
        plt.scatter(soh, soc_rate_of_change, s=5, alpha = 0.3, label=date)

    plt.xlabel("SOH (%)")
    plt.ylabel("SOC Rate of Change (% change every 0.5 min)")
    plt.title("SOH vs. SOC Rate of Change Scatterplot")
    plt.legend(loc='upper right', fontsize="7", ncol=1,
            borderaxespad=0, frameon=True)

    return scatter_figure

# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
def soh_plot():
    """
    The function takes in dates and soh and creates a single matplotlib figure line plot of date vs. SOH.
    Returns:
        line_figure: The matplotlib figure axis with stored line plot data and other supports.
    """
    
    # Set Plot
    line_figure = plt.figure(figsize=(6, 6))
    line_figure.tight_layout()

    # Make flight db connection
    flight_db_conn = query_flights()
    flight_data = flight_db_conn.get_flight_soh()
    soh = flight_data['soh']
    dates = flight_data["dates"]

    # Plot the graph
    plt.plot(dates, soh, marker='o', linestyle='-')
    plt.xlabel("Date (Year-Month)")
    plt.ylabel("SOH (%)")
    plt.title("Average SOH Per Month")

    return line_figure



# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
def custom_graph_creation(graph_type: str, flight_id, x_variable: str, y_variable: str, x_label: str, y_label: str):

    # Make the query connection
    flight_db_conn = query_flights()

    # Get data from x-variables
    query_result = flight_db_conn.get_flight_data_on_id(x_variable, flight_id)

    if len(x_variable) == 2:
        x_ax_data = (query_result[x_variable[0]].to_numpy() + query_result[x_variable[1]].to_numpy()) / 2
    else:
        x_ax_data = query_result[x_variable].to_numpy()

    # Get data from y-variables if they are not the same as the x-variables
    if y_variable != x_variable:
        query_result = flight_db_conn.get_flight_data_on_id(y_variable, flight_id)
    
    if len(y_variable) == 2:
        y_ax_data = (query_result[y_variable[0]].to_numpy() + query_result[y_variable[1]].to_numpy()) / 2
    else:
        y_ax_data = query_result[y_variable].to_numpy()

    # Set Plot
    custom_figure = plt.figure(figsize=(6, 6))
    custom_figure.tight_layout()

    # For each graph type graph different things.
    if graph_type == "Line Plot":
        plt.plot(x_ax_data, y_ax_data)

    elif graph_type == "Scatter Plot":
        plt.scatter(x_ax_data, y_ax_data, s=0.1, alpha = 0.6, c='blue')
    
    # Add labels and legend to plot
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(f"{x_label} vs {y_label}")

    # Return the axis
    return custom_figure

# Function -------------------------------------------------------------------------------------------------------------------------------------------------------
def charging_graph_creation(graph_type: str, flight_id, x_variable: str, y_variable: str, x_label: str, y_label: str):

    # Make the query connection
    flight_db_conn = query_flights()
    # Get data from x-variables
    if x_variable[0] == "temperature":
      query_result_x = flight_db_conn.get_temperature_on_id(flight_id)
    else:
      query_result_x = flight_db_conn.get_flight_data_on_id(x_variable, flight_id)

    # Get data from y-variables if they are not the same as the x-variables
    if y_variable != x_variable:
        if y_variable[0] == "temperature":
            query_result_y = flight_db_conn.get_temperature_on_id(flight_id)
        else:
            query_result_y = flight_db_conn.get_flight_data_on_id(y_variable, flight_id)

    # if one of the columns is temp, then we run the function
    if x_variable[0] == "temperature":
        query_result_x = aggregate_weather_for_charging(query_result_x, query_result_y)
    elif y_variable[0] == "temperature":
        query_result_y = aggregate_weather_for_charging(query_result_y, query_result_x)
        print("query_result_y", query_result_y)
    elif x_variable[0] and y_variable[0] == "temperature":
        query_result_y = aggregate_weather_for_charging(query_result_x, query_result_x)

    if len(x_variable) == 2:
        x_ax_data = (query_result_x[x_variable[0]].to_numpy() + query_result_x[x_variable[1]].to_numpy()) / 2
    else:
        x_ax_data = query_result_x[x_variable].to_numpy()

    
    if len(y_variable) == 2:
        y_ax_data = (query_result_y[y_variable[0]].to_numpy() + query_result_y[y_variable[1]].to_numpy()) / 2
    else:
        y_ax_data = query_result_y[y_variable].to_numpy()

    # Set Plot
    custom_figure = plt.figure(figsize=(6, 6))
    custom_figure.tight_layout()

    # For each graph type graph different things.
    print(x_ax_data)
    print(y_ax_data)
    if graph_type == "Line Plot":
        plt.plot(x_ax_data, y_ax_data)

    elif graph_type == "Scatter Plot":
        plt.scatter(x_ax_data, y_ax_data, s=0.1, alpha = 0.05, c='blue')
    
    # Add labels and legend to plot
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(f"{x_label} vs {y_label}")

    # Return the axis
    return custom_figure

def aggregate_weather_for_charging(weather_data, flight_data):
        
        # # Get all the input needed
        # weather_col_dict = {k: v for k, v in custom_weather_dict.items() if k in input.weather_cols()}
        # data_granularity_var = input.data_granularity()
        # selection_dict = custom_granular_variables_dict.items() if data_granularity_var == "Granular" else custom_aggregate_variables_dict.items()
        # flight_col_dict = {k: v for k, v in selection_dict if k in input.flight_cols()}
        # flight_id = input.data_preview_date()

        # # If no columns are chosen, then download a dictionary that says to select the columns
        # if len(weather_col_dict) == 0 or len(flight_col_dict) == 0:
        #     error_dict = {"Please select a weather or flight data column to view. Thank you!": ["Please select a weather or flight data column to view. Thank you!"]}
        #     error_df = pd.DataFrame(error_dict)
        #     # await asyncio.sleep(0.25)
        #     yield error_df.to_csv()
        #     return

        # with ui.Progress(min=1, max=15) as p:
        #     p.set(message="Calculation in progress", detail="This may take a while...")

        #     # Get the weather and flight data
        #     weather_data = query_weather().get_weather_data(flight_id, weather_col_dict)
        #     flight_data = query_flights().get_flight_by_column_dict(flight_id, flight_col_dict)

        # Get specific data out of the way
        # flight_first_col = flight_data.iloc[:, 0].to_numpy()
        # print("flight_first_col:", flight_first_col)
        # # Initialize the dict to hold all data
        # weather_concat_dict = {}

        # print(len(weather_data))
        # # If the length of the weather data is just 1. Fill everything like the weather and return.
        # if len(weather_data) == 1:
        #     # Loop over the weather columns
        #     for weather_col in weather_data.columns:
        #         print("weather_col", weather_col)
        #         # Check to see if the col is any type of date or time. If there is, change the string to that value.
        #         weather_full_data = np.full_like(flight_first_col, weather_data[weather_col][0], dtype=np.double)
        #         print("weather_full_data", weather_full_data)
        #         # Add the numpy list to the dict to make into a dataframe
        #         weather_concat_dict[weather_col] = weather_full_data

        #     # Add the final dict as a dataframe to a concatenated flight data. All data together.
        #     flight_data = pd.concat([flight_data, pd.DataFrame(weather_concat_dict)], axis=1)
        #     print("flight_data", flight_data)

        # else:
        #     # split each value by the length of the number of weather data points
        #     all_arrays = np.array_split(flight_first_col, len(weather_data))
        #     print("all_arrays", all_arrays)
        #     # Loop over the weather columns
        #     for weather_col in weather_data.columns:
        #         print("weather_col", weather_col)
        #         # Make the full list to hold the weather data in bits.
        #         weather_full_data = np.full_like(flight_first_col, 0.0, dtype=np.double)
        #         print("weather_full_data", weather_full_data)
        #         # count the indexes
        #         idx_counter = 0

        #         # loop over the split arrays.
        #         for i in range(len(all_arrays)):

        #             # Get the split array on the index.
        #             split = all_arrays[i]

        #             # get the length of the split by the index counter plus the length of the split array.
        #             split_len = len(split) + idx_counter

        #             # Add the splited weather data based on the index of the array.
        #             split_weather_data = np.full_like(split, weather_data[weather_col][i], dtype=np.double)

        #             # For the lenth of the split add the data point.
        #             weather_full_data[idx_counter:split_len] = split_weather_data

        #             # Make the index counter to the length of the split for the next split.
        #             idx_counter = split_len
                
        #         # Add the data to the weather dict.
        #         weather_concat_dict[weather_col] = weather_full_data
        #         print("weather_concat_dict", weather_concat_dict)

        #     # Add to the final flight data to put together.
        #     print(flight_data, "flight_data")
        #     flight_data = pd.concat([flight_data, pd.DataFrame(weather_concat_dict)], axis=1)
    # Sample dataframes (df1 and df2)

    print(weather_data)
    # Extract unique values from the column in the temperature dataframe
    unique_values = weather_data['temperature'].unique()

    # Calculate the number of times each unique value should be repeated
    num_repeats = len(flight_data) // len(unique_values)
    remainder = len(flight_data) % len(unique_values)

    # Create a list of repeated values
    repeated_values = []
    for value in unique_values:
        repeated_values.extend([value] * num_repeats)

    # Append remainder of values to evenly distribute
    repeated_values.extend(unique_values[:remainder])

    # Assign the repeated values to a new column in the first dataframe
    flight_data['temperature'] = repeated_values[:len(flight_data)]

    print(flight_data.head())
    return flight_data
