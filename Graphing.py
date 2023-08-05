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


def create_mapbox_map_per_flight(flight_id: int):

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
    lattitude = query_result["lat"].to_numpy()
    longitude = query_result["lng"].to_numpy() * (-1)

    # Graphing
    fig = go.Figure(go.Scattermapbox(
        lat=lattitude,
        lon=longitude,
        mode="lines",
        marker=go.scattermapbox.Marker(
            size=5
        ),
        text=['WWFC'],
    ))

    fig.update_layout(
        hovermode='closest',
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

    return fig


def graph_soc_graph(flight_ids: list):

    # Make flight db connection
    flight_db_conn = query_flights()
    flight_data = flight_db_conn.get_flight_soc_and_time(flight_ids)

    # Set warning zone, and danger zone ranges
    x_zone = [0, 0, 60, 60]
    warning_zone = [15.01, 30, 30, 15.01]
    danger_zone = [0, 15, 15, 0]

    # Set Plot
    soc_figure = plt.subplots(figsize=(10, 10))

    # Fill ranges
    soc_figure.fill(x_zone, warning_zone, c="yellow", alpha=0.5)
    soc_figure.fill(x_zone, danger_zone, c='r', alpha=0.5)

    # Plot the graphs
    for date in input.state():

        # Loop for all the flight ids
        if date in flight_data.keys():

            # Get the soc and time and plot it with a legend label
            soc = flight_data[date]['soc']
            time = flight_data[date]['time']
            plt.plot(time, soc, label=date)
    
    # Add labels and legend to plot
    soc_figure.xlim([0, 55])
    soc_figure.ylim([-1, 101])
    soc_figure.xlabel("time (min)")
    soc_figure.ylabel("SOC")
    soc_figure.title("Time vs SOC")
    
    # plt.legend(loc="lower left")
    soc_figure.legend(loc='upper right', bbox_to_anchor=(1.15, 1.02),
        ncol=3, fancybox=True, shadow=True)

    return soc_figure