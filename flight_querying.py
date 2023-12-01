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
    
    # Get Flights From 'labeled_activities_view' Function -----------------------------------------------------------------------------------------------------------------
    def get_flights_act_view(self, columns: list):
        """
        The function runs the following query: SELECT flight_id, flight_date FROM labeled_activities_view. This gets all the flight id's and dates of the flight.
        """

        # Make query
        if len(columns) == 0:
            query = "SELECT * FROM labeled_activities_view"
        else:
            str_column = "".join([f"{column}, " for column in columns])[:-2]
            query = f"SELECT {str_column} FROM labeled_activities_view"

        # Make database connection
        engine = self.connect()

        # Select the data based on the query
        print(query)
        flights = pd.read_sql_query(query, engine)
        print("finished reading query")

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
    
    # Get Flight Data for every half minute Function ------------------------------------------------------------------------------------------------------------
    def get_flight_data_every_half_min_on_id(self, columns: list, id: int):

        # Make database connection
        engine = self.connect()

        # # Unravel list of columns to be a string to input
        # str_column = "".join([f"{column}, " for column in columns])[:-2]

        # Make query
        query = f"""
                SELECT
                    fw_flight_id,
                    activity,
                    time_min,
                    bat_1_soc,
                    bat_2_soc,
                    motor_power
                FROM
                    labeled_activities_view
                WHERE
                    fw_flight_id = {str(id)};
                """

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
    
    # Get Flight Id and Dates Function ---------------------------------------------------------------------------------------------------
    def get_flight_id_and_dates_act_view(self):
        """
        Function gets all flight ids and dates from labeled_activities_view and returns a dictionary of flight_date: flight_id
        """

        # Initialize the dictionary
        flight_dict = {}

        # Get all the flights
        flights_df = self.get_flights_act_view(["fw_flight_id", "flight_date"])

        # Change to Numpy
        ids = flights_df["fw_flight_id"].to_numpy()
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

    
    # Get Flight Id, Motor power, and Time (in minutes) Function -------------------------------------------------------------------------
    def get_flight_motor_power_and_time(self, flight_ids: list):
        """
        Function that uses the flight ids to get their respective motor power and time columns. Then, returns a dictionary of 
        flight_id: {motor_power: [], time: []}
        """

        # Initialize the dictionary
        flight_dict = {}

        # Get soc, and time data for the specific flight
        for id in flight_ids:

            # Get the flight data
            flights_df = self.get_flight_data_on_id(["flight_id", "time_min", "motor_power"], id)

            # Change to Numpy
            times = flights_df["time_min"].to_numpy()
            motor_power = flights_df["motor_power"].to_numpy()

            flight_dict[id] = {"motor_power": motor_power, "time_min": times}

        return flight_dict
    
    # Get Flight Id, Motor power, and SOC rate Function -------------------------------------------------------------------------
    def get_flight_power_soc_rate(self, flight_ids: list):
        """
        Function that uses the flight ids to get their respective time, motor power, soc, soc rate of change, and activity columns. 
        Then, returns a dictionary of 
        fw_flight_id: {time: [], motor_power: [], soc: [], soc_rate_of_change: [], activity: []}
        """

        # Initialize the dictionary
        flight_dict = {}

        # Get time, power, soc, and soc rate data for the specific flight(s)
        for id in flight_ids:

            # Get the flight data
            flights_df = self.get_flight_data_every_half_min_on_id(["fw_flight_id", "time_min", "motor_power", "bat_1_soc", "bat_2_soc", "activity"], id)

            # Change to Numpy
            times = flights_df["time_min"].to_numpy()
            motor_power = flights_df["motor_power"].to_numpy()
            activity = flights_df["activity"].to_numpy()
            soc = (flights_df["bat_1_soc"].to_numpy() + flights_df["bat_2_soc"].to_numpy()) / 2 # get soc avg

            # Calculate SOC rate of change
            # The rate of change for the last entry will be set to 0 since there is no next entry to compare with
            soc_rate_of_change = (soc[1:] - soc[:-1]) / (times[1:] - times[:-1])
            # Append a 0 to soc_rate_of_change to keep the array sizes consistent
            soc_rate_of_change = np.append(soc_rate_of_change, 0) 

            flight_dict[id] = {"time_min": times, "motor_power": motor_power, "soc": soc, "soc_rate_of_change": soc_rate_of_change, "activity": activity}

        return flight_dict


    def get_number_of_circuits(self, flight_id):
        """
        Function that uses a flight id to get the number of circuits. Then, returns the number of circuits.
        """
        # Make database connection
        engine = self.connect()

        # query for the number of circuits (explanation below), note that cycle = circuit

        # Common Table Expression (CTE) named "AltitudeData": This CTE rounds the "pressure_alt" values to integers using the ROUND function and calculates the previous and next rounded altitudes using the LAG and LEAD.
        # Main query selects the sum of "is_start_of_cycle" from a subquery named "StartOfCycleData." This subquery is where the actual cycle detection logic is implemented
        #  "StartOfCycleData" subquery:
            # Selects the altitude values and the "time_min" column from the "AltitudeData" CTE.
            # Calculates a new column named "is_start_of_cycle" using CASE. is_start_of_cycle = 1 when the following conditions are met:
                # The rounded altitude (which is current altitude) is greater than 500.
                # The previous altitude (prev_altitude) is less than or equal to 500, or it is null (indicating the start of the dataset).
                # The next altitude (next_altitude) is greater than or equal to 500, or it is null (indicating the end of the dataset).
                # When these conditions are met, it signifies the start of a cycle, and "is_start_of_cycle" is set to 1; otherwise, it is set to 0.
            # In the main query, it sums up the "is_start_of_cycle" values, which basically counts the number of cycles.
        query = f"""WITH AltitudeData AS (
                    SELECT
                        time_min,
                        ROUND(pressure_alt) AS altitude,
                        LAG(ROUND(pressure_alt)) OVER (ORDER BY time_min) AS prev_altitude,
                        LEAD(ROUND(pressure_alt)) OVER (ORDER BY time_min) AS next_altitude
                    FROM flightdata_{flight_id}
                )

                SELECT

                    SUM(is_start_of_cycle) AS cycle_count
                FROM (
                    SELECT
                        time_min,
                        ROUND(altitude),
                        CASE
                            WHEN ROUND(altitude) > 500 AND (prev_altitude <= 500 OR prev_altitude IS NULL) AND (next_altitude >= 500 OR next_altitude IS NULL) THEN 1
                            ELSE 0
                        END AS is_start_of_cycle
                    FROM AltitudeData
                ) AS StartOfCycleData
                WHERE is_start_of_cycle = 1;"""

        # Put the result of the query in an array
        count_array = pd.read_sql_query(query, engine).to_numpy()

        # Get number of circuits
        num_circuits = count_array[0][0]

        # Dispose of the connection, so we don't overuse it.
        engine.dispose()

        return num_circuits



