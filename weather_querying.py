from dotenv import load_dotenv
from sqlalchemy import create_engine
from flight_querying import query_flights
import pandas as pd
import numpy as np
import psycopg2
import json
import os


class query_weather:
   
    def connect(self):
        """
        
        """
        # Load .env files
        load_dotenv()

        # Connect to Database
        engine_string = "postgresql+psycopg2" + os.getenv('DATABASE_URL')[8:]
        
        engine = create_engine(engine_string)

        return engine
    

    def get_weather_by_flight_id(self, flight_id):
        """
        
        """
        # Make database connection
        engine = self.connect()

        query = f"""SELECT weather.weather_time_utc AS "Time (UTC)", 
                          weather.temperature AS "Temperature (°C)", 
                          weather.wind_speed AS "Wind Speed (knots)", 
                          weather.wind_direction AS "Wind Direction (Degrees)", 
                          weather.visibility AS "Visibility (Mi)"
                    FROM flight_weather 
                    JOIN weather
                        ON flight_weather.weather_id = weather.id
                    WHERE flight_weather.flight_id = {flight_id}"""
        
        # Select the data based on the query
        weather_flight_df = pd.read_sql_query(query, engine)

        engine.dispose()

        return weather_flight_df
        
        



