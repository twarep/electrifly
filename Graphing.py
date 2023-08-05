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


def graph_soc_graph(flight_ids: list, flight_dates: list):

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