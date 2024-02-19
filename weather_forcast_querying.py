from datetime import date
from dotenv import load_dotenv
from sqlalchemy import create_engine
from forecast import get_forcast_from_today
from storage import db_connect, table_exists, execute
import pandas as pd
import os

# Database Connection Function ---------------------------------------------------------------------------------------------------------
def connect():
    """
    The function initiates a connection with the PostgreSQL database using the DATABASE_URL.
    """
    # Load .env file
    load_dotenv()

    # Connect to Database
    engine_string = "postgresql+psycopg2" + os.getenv('DATABASE_URL')[8:]
    
    engine = create_engine(engine_string)

    return engine


def get_current_date():
    current_date = date.today()
    # Format the date as a string in the format YYYY-MM-DD
    # formatted_date = current_date.strftime('%Y-%m-%d')
    return current_date


def get_forecast_by_current_date():
    """
    Get the forecast for the current day and the next three days. If the forecast isn't made, then make it and return the query.
    """

    # Make database connection
    engine = connect()

    # Check to see if the forecast table exists in the DB
    # If it does, first see if the forecast is required by checking if the current date is the first date saved in the DB
    # If it is, then don't drop the table and return. If it isn't, the drop the table and calculate the forecast
    conn = db_connect()
    if table_exists("forecast", conn):
        # get the first date from the forecast
        query_string = "SELECT DISTINCT(forecast_date) FROM forecast ORDER BY forecast_date LIMIT 1;"
        forecast_date = pd.read_sql_query(query_string, engine).to_dict("dict")["forecast_date"][0]
        today_date = get_current_date()
        # Check if they are the same
        if forecast_date == today_date:
            print("dates are the same, not going to drop the forecast table")
        else:
            # drop the table
            execute("DROP TABLE forecast;")
            # Get newest forcast from api call on the forecast.py
            get_forcast_from_today()
    else:
        # If the table doesn't exist, then get newest forcast from api call on the forecast.py
        get_forcast_from_today()

    # Make the query and take into dataframe
    query = f"""SELECT forecast_date AS "Forecast Date",
                        forecast_time_et AS "Forecast Time",
                        temperature_2m AS "Temperature (°C)",
                        weathercode AS "Weathercode",
                        windgusts_10m AS "Wind Gusts",
                        lightning_potential AS "Lightning Potential",
                        winddirection_10m AS "Wind Direction 10m (Degrees)", 
                        visibility AS "Visibility",
                        sunrise_time AS "Sunrise",
                        sunset_time AS "Sunset"
                FROM forecast
            """
    weather_flight_df = pd.read_sql_query(query, engine)

    # Dispose of the engine and close its connection and then return the dataframe
    engine.dispose()
    return weather_flight_df