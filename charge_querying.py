from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta

class Charge:

    # Database Connection Function ---------------------------------------------------------------------------------------------------------
    def __connect(self):
        """
        The function initiates a connection with the PostgreSQL database using the DATABASE_URL.
        """
        # Load .env file
        load_dotenv()

        # Connect to Database
        engine_string = "postgresql+psycopg2" + os.getenv('DATABASE_URL')[8:]
        
        engine = create_engine(engine_string)

        return engine
    

    # Get charges Function -----------------------------------------------------------------------------------------------------------------
    def get_charge_data(self, columns: list, table):
        """
        The function runs the following query: SELECT {columns} FROM {table} WHERE flight_type = \'Charging\'.
        """

        # Make query
        if len(columns) == 0:
            query = f"SELECT * FROM {table} WHERE flight_type = \'Charging\' ORDER BY flight_date DESC;"
        else:
            str_column = "".join([f"{column}, " for column in columns])[:-2]
            query = f"SELECT {str_column} FROM {table} WHERE flight_type = \'Charging\' ORDER BY flight_date DESC;"

        # Make database connection
        engine = self.__connect()

        # Select the data based on the query
        charge_data = pd.read_sql_query(query, engine)

        # Dispose of the connection, so we don't overuse it.
        engine.dispose()

        return charge_data


    # Get Flight by Id Function ------------------------------------------------------------------------------------------------------------
    def get_charge_data_by_id(self, id: int):
        """
        The function runs the following query: SELECT id, flight_date FROM charges. This gets all the flight id's and dates of the flight.
        """

        # Make query
        query = f"SELECT * FROM charges WHERE id = {str(id)}"

        # Make database connection
        engine = self.__connect()

        # Select the data based on the query
        charge_data = pd.read_sql_query(query, engine)

        # Dispose of the connection, so we don't overuse it.
        engine.dispose()

        return charge_data

    # Get Flight Data Function ------------------------------------------------------------------------------------------------------------
    def get_charge_data_on_id(self, columns: list, id: int):

        # Make database connection
        engine = self.__connect()

        # Unravel list of columns to be a string to input
        str_column = "".join([f"{column}, " for column in columns])[:-2]

        # Make query
        query = f"SELECT {str_column} FROM flightdata_{str(id)}"

        # Select the data based on the query
        charge_data = pd.read_sql_query(query, engine)

        # Dispose of the connection, so we don't overuse it.
        engine.dispose()

        return charge_data

    
    # Get Charge Data Id and Dates Function ---------------------------------------------------------------------------------------------------
    def get_charge_data_id_and_dates(self, columns, table):
        """
        Function gets all flight ids and dates and returns a dictionary of flight_id : flight_date 
        """

        # Initialize the dictionary
        charge_data_dict = {}

        # Get all the charges
        charge_data_df = self.get_charge_data(columns, table)

        # Change to Numpy
        ids = charge_data_df[columns[0]].to_numpy()
        flight_dates = charge_data_df[columns[1]].to_numpy()

        if len(columns) > 2:
            flight_times = charge_data_df[columns[2]].to_numpy()
            datetimes = [datetime.combine(flight_dates[i], flight_times[i]) - relativedelta(hours=5) for i in range(len(flight_dates))]

        # Loop over all the flight dates to input into dictionary
        for i in range(len(flight_dates)):
            
            # Create a string object to show the date in mm/dd/year format. Create Key: Value relation.
            if len(columns) > 2:
                date = datetimes[i].strftime("%b %d, %Y at %I:%M %p")
            else:
                date = flight_dates[i].strftime("%B %d, %Y")

            id = str(ids[i])
            charge_data_dict[id] = date

        return charge_data_dict
