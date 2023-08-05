from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import os


class query_flights:

    # Database Connection Function ---------------------------------------------------------------------------------------------------------
    def connect(self):
        """
        The function initiates a connection with the PostgreSQL database using the DATABASE_URL.
        """
        # Load .env file
        load_dotenv()

        # Connect to Database
        engine_string = "postgresql+psycopg2" + os.getenv('DATABASE_URL')[8:]
        
        engine = create_engine(engine_string)

        return engine
    

    # Get Flights Function -----------------------------------------------------------------------------------------------------------------
    def get_flights(self, columns: list):
        """
        The function runs the following query: SELECT id, flight_date FROM flights. This gets all the flight id's and dates of the flight.
        """

        # Make query
        if len(columns) == 0:
            query = "SELECT * FROM flights"
        else:
            str_column = "".join([f"{column}, " for column in columns])[:-2]
            query = f"SELECT {str_column} FROM flights"

        # Make database connection
        engine = self.connect()

        # Select the data based on the query
        flights = pd.read_sql_query(query, engine)

        # Dispose of the connection, so we don't overuse it.
        engine.dispose()

        return flights
    

    # Get Flight by Id Function ------------------------------------------------------------------------------------------------------------
    def get_flight_by_id(self, id: int):
        """
        The function runs the following query: SELECT id, flight_date FROM flights. This gets all the flight id's and dates of the flight.
        """

        # Make query
        query = f"SELECT * FROM flights WHERE id == {str(id)}"

        # Make database connection
        engine = self.connect()

        # Select the data based on the query
        flights = pd.read_sql_query(query, engine)

        # Dispose of the connection, so we don't overuse it.
        engine.dispose()

        return flights
    

    # Get Flight Data Function ------------------------------------------------------------------------------------------------------------
    def get_flight_data_on_id(self, columns: list, id: int):

        # Make database connection
        engine = self.connect()

        # Unravel list of columns to be a string to input
        str_column = "".join([f"{column}, " for column in columns])[:-2]

        # Make query
        query = f"SELECT {str_column} FROM flightdata_{str(id)}"

        # Select the data based on the query
        flight_data = pd.read_sql_query(query, engine)

        # Dispose of the connection, so we don't overuse it.
        engine.dispose()

        return flight_data


    # Get Flight Id and Dates Function ---------------------------------------------------------------------------------------------------
    def get_flight_id_and_dates(self):
        """
        Function gets all flight ids and dates and returns a dictionary of flight_date: flight_id
        """

        # Initialize the dictionary
        flight_dict = {}

        # Get all the flights
        flights_df = self.get_flights(["id", "flight_date"])

        # Change to Numpy
        ids = flights_df["id"].to_numpy()
        flight_dates = flights_df["flight_date"].to_numpy()

        # Loop over all the flight dates to input into dictionary
        for i in range(len(flight_dates)):
            
            # Create a string object to show the date in mm/dd/year format. Create Key: Value relation.
            date = flight_dates[i].strftime("%m/%d/%Y")
            flight_dict[date] = ids[i]

        return flight_dict
    

    # Get Flight Id, SOC, and Time (in minutes) Function --------------------------------------------------------------------------------
    def get_flight_soc_and_time(self, flight_ids: list):
        """
        Function that uses the flight ids to get their respective soc and time columns. Then, returns a dictionary of 
        flight_id: {soc: [], time: []}
        """

        # Initialize the dictionary
        flight_dict = {}

        # Get soc, and time data for the specific flight
        for id in flight_ids:

            # Get the flight data
            flights_df = self.get_flight_data_on_id(["flight_id", "time_min", "bat_1_soc", "bat_2_soc"], id)

            # Change to Numpy
            times = flights_df["time_min"].to_numpy()
            soc = (flights_df["bat_1_soc"].to_numpy() + flights_df["bat_2_soc"].to_numpy()) / 2

            flight_dict[id] = {"soc": soc, "time_min": times}

        return flight_dict




