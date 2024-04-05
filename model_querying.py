import pandas as pd
import psycopg2
import random
import numpy as np
import os
import pickle
import joblib
from flight_querying import query_flights
from dotenv import load_dotenv
from sqlalchemy import create_engine

class Model():

    # Initialize the class by getting the model
    def __init__(self):

        # Get the trained model
        model_filename = 'ML_model_outputs/prescription_xgboost_model.joblib'
        self.model = joblib.load(model_filename)

        # Get the activity label model too
        label_model_filename = 'ML_model_outputs/label_xgboost_model.joblib'
        self.label_model = joblib.load(label_model_filename)

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


    # Function -----------------------------------------------------------------------------
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
    def get_attribute_max_min(self, attribute: str, operation: str):
        
        # Get the connection
        connection = self.__connection()

        # create a cursor object to interact with the database
        cursor = connection.cursor()

        # Get the attribute columns
        cursor.execute(f"SELECT {attribute} FROM model WHERE activity = \'{operation}\';")

        # Get all the data and columns names and make a pandas dataframe.
        data = cursor.fetchall()
        attribute_array = pd.DataFrame(data, columns=[attribute]).to_numpy()

        # close the cursor and the connection
        cursor.close()
        self.__disconnect(connection)

        return round(attribute_array.max(), 2), round(attribute_array.min(), 2)


    # Function ------------------------------------------------------------------------------------
    # Get prediction based off manual input of all datatypes
    def get_manual_model_prediction(self, maneuver, forecast_date, forecast_time, time_delta, altitude, ground_speed, motor_power, soh):

        # Get the activities
        with open("ML_model_outputs/columns.pkl", "rb") as file:
            model_cols = pickle.load(file)
        all_activities = [col for col in model_cols if "activity" in col]

        # Get the weather data for this flight
        # NOTE: the forecasted visibility is in meters, while the weather data visibility is in miles
        # NOTE: 1 mile (nautical) = 1852 meters
        temperature, visibility, windspeed = self.fights.get_forecast_weather_by_date(forecast_date, forecast_time)
        visibility_mile = round(visibility/1852, 2)

        # get and fill attributes
        attributes_dict = {
            "time_delta": [time_delta],
            "soh": [soh],
            "average_altitude": [altitude],
            "ground_speed": [ground_speed],
            "average_power": [motor_power]
        }

        # add weather
        attributes_dict["temperature"] = [temperature]
        attributes_dict["visibility"] = [visibility_mile]
        attributes_dict["wind_speed"] = [windspeed]

        # make the addition of the activity
        for operation in all_activities:
            if "NA" not in operation or "TBD" not in operation:
                if maneuver in operation:
                    attributes_dict[operation] = [True]
                else:
                    attributes_dict[operation] = [False]

        # Make the pandas df for 
        pred_df = pd.DataFrame(attributes_dict)

        # Make prediction if prediction is below 0 change it to zero
        prediction = self.model.predict(pred_df)
        if prediction < 0:
            prediction = 0

        return prediction, attributes_dict["time_delta"][0], attributes_dict["average_power"][0], attributes_dict["soh"][0], attributes_dict["average_altitude"][0], attributes_dict["ground_speed"][0]


    # Function ------------------------------------------------------------------------------------
    # Gets prediction based on sliders
    def get_model_prediction(self, maneuver, forecast_date, forecast_time, time_tuple, altitude_tuple, ground_speed_tuple, motor_power_tuple):

        # Get the activities
        with open("ML_model_outputs/columns.pkl", "rb") as file:
            model_cols = pickle.load(file)
        all_activities = [col for col in model_cols if "activity" in col]

        # Get the weather data for this flight
        # NOTE: the forecasted visibility is in meters, while the weather data visibility is in miles
        # NOTE: 1 mile (nautical) = 1852 meters
        temperature, visibility, windspeed = self.fights.get_forecast_weather_by_date(forecast_date, forecast_time)
        visibility_mile = round(visibility/1852, 2)

        # get the attribute values
        attributes_dict = {}
        max_soh, min_soh = self.get_attribute_max_min("soh", maneuver)
        attributes_dict["time_delta"] = round(np.random.uniform(time_tuple[0], time_tuple[1]), 2)
        attributes_dict["soh"] = min_soh
        attributes_dict["average_altitude"] = np.random.randint(altitude_tuple[0], altitude_tuple[1])
        attributes_dict["ground_speed"] = np.random.randint(ground_speed_tuple[0], ground_speed_tuple[1])
        attributes_dict["average_power"] = np.random.randint(motor_power_tuple[0], motor_power_tuple[1])

        # add weather
        attributes_dict["temperature"] = [temperature]
        attributes_dict["visibility"] = [visibility_mile]
        attributes_dict["wind_speed"] = [windspeed]

        # make the addition of the activity
        for operation in all_activities:
            if "NA" not in operation or "TBD" not in operation:
                if maneuver in operation:
                    attributes_dict[operation] = [True]
                else:
                    attributes_dict[operation] = [False]

        # Make the pandas df for 
        pred_df = pd.DataFrame(attributes_dict)

        # Make prediction if prediction is below 0 change it to zero
        prediction = self.model.predict(pred_df)
        if prediction < 0:
            prediction = 0

        return prediction, attributes_dict["time_delta"], attributes_dict["average_power"], attributes_dict["soh"], attributes_dict["average_altitude"], attributes_dict["ground_speed"]