from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd
import os


class query_weather:
   
    def __connect(self):
        """
        
        """
        # Load .env files
        load_dotenv()

        # Connect to Database
        engine_string = "postgresql+psycopg2" + os.getenv('DATABASE_URL')[8:]
        
        engine = create_engine(engine_string)

        return engine
    

    def get_weather_by_flight_id(self, flight_id):
        """Gets the weather data based on the inputted ID.

        Parameters: flight_id --> The id corresponding to the flight. Must be an integer number above 4 characters.

        Returns: weather_flight_df --> A dataframe with the weather data. Or a statement saying. 
        """

        # Check if the flight_id exists and then run the code
        if flight_id == "":
            error_dict = {"Please input a flight date to view the flight map.": ["-"]}
            error_df = pd.DataFrame(error_dict)
            return error_df

        # Make database connection
        engine = self.__connect()

        query = f"""SELECT weather.weather_time_utc AS "Time (UTC)", 
                          weather.temperature AS "Temperature (°F)", 
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
    

    def get_weather_data(self, flight_id: int, columns_dict: dict):

        # Make database connection
        engine = self.__connect()

        # Get the columns in order and make the query
        str_column = str("".join([f"weather.{value[0]} AS \"{key}\", " for key, value in list(columns_dict.items())])[:-2])
        query = f"""SELECT {str_column} 
                    FROM flight_weather 
                    JOIN weather 
                        ON flight_weather.weather_id = weather.id 
                    WHERE flight_weather.flight_id = {flight_id};"""
        
        # Select the data based on the query
        weather_flight_df = pd.read_sql_query(query, engine)

        engine.dispose()

        return weather_flight_df
        
