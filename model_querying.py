import pandas as pd
import psycopg2
import random
import numpy as np
import os
import joblib
from flight_querying import query_flights
from dotenv import load_dotenv
from sqlalchemy import create_engine

class Model():

    # Initialize the class by getting the model
    def __init__(self):

        # Get the trained model
        model_filename = 'ML_model_outputs/prescription_randomforest_model.joblib'
        self.model = joblib.load(model_filename)

        # Initializae the engine string and make sure that the model table is in the db
        self.__engine_string = "postgresql+psycopg2" + os.getenv('DATABASE_URL')[8:]
        self.fights = query_flights()
        self.database_model_data()


    # Hidden Function -----------------------------------------------------------------------------
    # Creates and returns a connection to the database
    def __connection(self):
        
        # Load .env file
        load_dotenv()

        # Get the connection string from the environment variable
        connection_string = os.getenv('DATABASE_URL')

        # Connect to the PostgreSQL database
        conn = psycopg2.connect(connection_string)

        # Return the connection
        return conn


    # Hidden Function -----------------------------------------------------------------------------
    # Disconnect the given connection from the database
    def __disconnect(self, conn):
        conn.close()
    

    # Hidden Function -----------------------------------------------------------------------------
    # this function checks if the given table exists
    def table_exists(self, table):

        # Get the connection
        connection = self.__connection()
    
        # create a cursor object to interact with the database
        cursor = connection.cursor()
        
        # check if the given table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1
                FROM pg_catalog.pg_tables
                WHERE tablename = %s
            );
        """, (table,))
        
        # fetch the result
        exists = cursor.fetchone()[0]
        
        # close the cursor and the connection
        cursor.close()
        self.__disconnect(connection)
        
        return exists
    

    # Function ------------------------------------------------------------------------------------
    # Check if specific table exists if not, make it and add saved data in `ML_model_outputs/all_data.csv`
    def database_model_data(self):
        
        # If the model table does not exist
        if not self.table_exists("model"):
            print("Model doesn't exist")

            # Get data from the csv file
            all_data = pd.read_csv("ML_model_outputs/all_data.csv").drop(columns=["unique_data_identifier"])

            # push the data to the forecast table
            engine = create_engine(self.__engine_string)

            # add new table to db
            all_data.to_sql("model", engine, if_exists="fail", index=False)


    # Function ------------------------------------------------------------------------------------
    # Get the specific columns from the model table and 
    def model_attributes(self, activity, column_names: list):

        # Get the connection
        connection = self.__connection()

        # create a cursor object to interact with the database
        cursor = connection.cursor()

        # Get the attribute columns
        str_column = "".join([f"{column}, " for column in column_names])[:-2]
        cursor.execute(f"SELECT {str_column} FROM model WHERE activity = \'{activity}\' and time_delta > 0.1;")

        # Get all the data and columns names and make a pandas dataframe.
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=column_names)

        # Loop through all columns and get the a random value
        attribute_values = {}
        rand_index = random.randint(0, len(df) -1)
        for column in column_names:
            attribute_values[column] = df[column].to_numpy()[rand_index]

        # close the cursor and the connection
        cursor.close()
        self.__disconnect(connection)

        # return those attributes
        return attribute_values


    # Function ------------------------------------------------------------------------------------
    # Check if specific table exists if not, make it and add saved data in `ML_model_outputs/all_data.csv`
    def get_model_prediction(self, maneuver, forecast_date, forecast_time):

        # Get the connection and 
        all_activities = self.fights.get_unique_activity()

        # Get the weather data for this flight
        # NOTE: the forecasted visibility is in meters, while the weather data visibility is in miles
        # NOTE: 1 mile (nautical) = 1852 meters
        temperature, visibility, windspeed = self.fights.get_forecast_weather_by_date(forecast_date, forecast_time)
        visibility_mile = round(visibility/1852, 2)

        # get the attribute values
        attributes = ["time_delta", "soh", "average_altitude", "ground_speed", "average_power"]
        attributes_dict = self.model_attributes(maneuver, attributes)

        # add weather
        attributes_dict["temperature"] = [temperature]
        attributes_dict["visibility"] = [visibility_mile]
        attributes_dict["wind_speed"] = [windspeed]

        # Prefix the activities with is_
        for operation in all_activities:
            if operation not in ("NA", "TBD"):
                operation_column = "activity_is_" + operation
                
                if maneuver in operation_column:
                    attributes_dict[operation_column] = [True]
                else:
                    attributes_dict[operation_column] = [False]

        # Make the pandas df for 
        pred_df = pd.DataFrame(attributes_dict)

        prediction = self.model.predict(pred_df)

        return prediction, attributes["time_delta"], attributes["average_power"]