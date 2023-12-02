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
                          weather.visibility AS "Visibility (m)"
                    FROM flight_weather 
                    JOIN weather
                        ON flight_weather.weather_id = weather.id
                    WHERE flight_weather.flight_id = {flight_id}"""
        
        # Select the data based on the query
        weather_flight_df = pd.read_sql_query(query, engine)

        engine.dispose()

        return weather_flight_df
        
        
    def get_temperature_summary_by_flight_id(self, flight_id):
        """
        
        """
        # Make database connection
        engine = self.connect()

        query = f"""SELECT min(weather.temperature) AS "Min Temperature (°C)", 
                     max(weather.temperature) AS "Max Temperature (°C)", 
                     avg(weather.temperature) AS "Average Temperature (°C)",
                     stddev_samp(weather.temperature) AS "Standard Deviation Temperature (°C)",
                     var_samp(weather.temperature) AS "Variance Temperature (°C)",
                    FROM flight_weather 
                    JOIN weather
                        ON flight_weather.weather_id = weather.id
                    WHERE flight_weather.flight_id = {flight_id} and weather.temperature is not null"""
        
        # Select the data based on the query
        weather_flight_df = pd.read_sql_query(query, engine)

        engine.dispose()

        return weather_flight_df


    def get_soc_summary_by_flight_id(self, flight_id):
        """
        
        """
        # Make database connection
        engine = self.connect()

        query = f"""SELECT min((flights.bat_1_soc + flights.bat_2_soc) / 2) AS "Min SOC", 
                     max((flights.bat_1_soc + flights.bat_2_soc) / 2) AS "Max SOC", 
                     avg((flights.bat_1_soc + flights.bat_2_soc) / 2) AS "Average SOC",
                     stddev_samp((flights.bat_1_soc + flights.bat_2_soc) / 2) AS "Standard Deviation SOC",
                     var_samp((flights.bat_1_soc + flights.bat_2_soc) / 2) AS "Variance SOC",
                    FROM flightsdata_{flight_id}
                    WHERE flights.flight_id = {flight_id} and flights.bat_1_soc is not null"""
        
        # Select the data based on the query
        soc_flight_df = pd.read_sql_query(query, engine)

        engine.dispose()

        return soc_flight_df