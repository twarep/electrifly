from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
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
    current_date = datetime.now()
        # Format the date as a string in the format YYYY-MM-DD
    # formatted_date = current_date.strftime('%Y-%m-%d')
    return current_date


def get_forecast_by_current_date():
    """
    
    """
    # Make database connection
    engine = connect()

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

    engine.dispose()

    return weather_flight_df