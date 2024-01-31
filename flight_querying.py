from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import os
import psycopg2
from time import time
from datetime import datetime
from dateutil.relativedelta import relativedelta


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

    
    # Getting the flight data column names -------------------------------------------------------------------------------------------------
    # From Example 1 here: https://www.geeksforgeeks.org/get-column-names-from-postgresql-table-using-psycopg2/
    def get_flight_columns(self):
        """
        The function uses psycopg2 to get the column name 
        """

        # Make database connection
        engine = self.connect()

        # Make and execute the query
        sql_query = 'SELECT * FROM flightdata_4620 LIMIT 1'
        flights = pd.read_sql_query(sql_query, engine)

        # Save the column names to an array
        columns = [column for column in flights.columns if column not in ["flight_id"]]

        # Return the columns
        return columns
    

    # Get Flights Function -----------------------------------------------------------------------------------------------------------------
    def get_flights(self, columns: list, table):
        """
        The function runs the following query: SELECT {columns} FROM {table}. This gets all the flight id's and dates of the flight.
        """

        # Make query
        if len(columns) == 0:
            query = f"SELECT * FROM {table}"
        else:
            str_column = "".join([f"{column}, " for column in columns])[:-2]
            query = f"SELECT {str_column} FROM {table}"

        print(query)

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
        query = f"SELECT * FROM flights WHERE id = {str(id)}"

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
    def get_flight_data_every_half_min_on_id(self, id: int):
        """
        The function runs a query to get the fw_flight_id, activity, time, soc, and power from labeled activities view in 30 sec intervals.
        """
        # Make database connection
        engine = self.connect()

        # Make query
        query = f"""
                SELECT
                    fw_flight_id,
                    activity,
                    ROUND(time_min*2)/2 AS time_min_rounded,
                    AVG(bat_1_soc) AS bat_1_soc,
                    AVG(bat_2_soc) AS bat_2_soc,
                    AVG(motor_power) AS motor_power
                FROM
                    labeled_activities_view
                WHERE
                    fw_flight_id = {str(id)}
                GROUP BY
                    fw_flight_id, activity, time_min_rounded
                ORDER BY
                    fw_flight_id, activity, time_min_rounded;

                """

        # Select the data based on the query
        flight_data = pd.read_sql_query(query, engine)

        # Dispose of the connection, so we don't overuse it.
        engine.dispose()

        return flight_data
    

    # Get Flight Data for every half minute Function ------------------------------------------------------------------------------------------------------------
    def get_temp_data_every_half_min_on_id(self, columns: list, id: int):
        """
        The function runs a query to get the fw_flight_id, time, soc, and temp from flight_weather_data_view in 30 sec intervals.
        """
        # Make database connection
        engine = self.connect()

        # Make query
        query = f"""
                SELECT
                    fw_flight_id,
                    ROUND(time_min*2)/2 AS time_min_rounded,
                    AVG(bat_1_soc) AS bat_1_soc,
                    AVG(bat_2_soc) AS bat_2_soc,
                    AVG(temperature) AS temperature
                FROM
                    flight_weather_data_view
                WHERE
                    fw_flight_id = {str(id)} 
                GROUP BY
                    fw_flight_id, time_min_rounded
                ORDER BY
                    fw_flight_id, time_min_rounded;
                """

        # Select the data based on the query
        flight_data = pd.read_sql_query(query, engine)

        # Dispose of the connection, so we don't overuse it.
        engine.dispose()

        return flight_data


    # Get Flight Id and Dates Function ---------------------------------------------------------------------------------------------------
    def get_flight_id_and_dates(self, columns, table):
        """
        Function gets all flight ids and dates and returns a dictionary of flight_id : flight_date 
        """

        # Initialize the dictionary
        flight_dict = {}

        # Get all the flights
        flights_df = self.get_flights(columns, table)

        # Change to Numpy
        ids = flights_df[columns[0]].to_numpy()
        flight_dates = flights_df[columns[1]].to_numpy()

        if len(columns) > 2:
            flight_times = flights_df[columns[2]].to_numpy()
            datetimes = [datetime.combine(flight_dates[i], flight_times[i]) - relativedelta(hours=5) for i in range(len(flight_dates))]

        # Loop over all the flight dates to input into dictionary
        for i in range(len(flight_dates)):
            
            # Create a string object to show the date in mm/dd/year format. Create Key: Value relation.
            if len(columns) > 2:
                date = datetimes[i].strftime("%b %d, %Y at %I:%M %p")
            else:
                date = flight_dates[i].strftime("%B %d, %Y")

            id = str(ids[i])
            flight_dict[id] = date

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
            flight_date_df = self.get_flight_by_id(id)

            # Change to Numpy
            times = flights_df["time_min"].to_numpy()
            soc = (flights_df["bat_1_soc"].to_numpy() + flights_df["bat_2_soc"].to_numpy()) / 2
            date = flight_date_df["flight_date"].iloc[0].strftime("%b %d, %Y")

            flight_dict[id] = {"soc": soc, "time_min": times, "date": date}

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
            flight_date_df = self.get_flight_by_id(id)

            # Change to Numpy
            times = flights_df["time_min"].to_numpy()
            motor_power = flights_df["motor_power"].to_numpy()
            date = flight_date_df["flight_date"].iloc[0].strftime("%b %d, %Y")

            flight_dict[id] = {"motor_power": motor_power, "time_min": times, "date": date}

        return flight_dict
    

    # Get Flight Id, Motor power, SOC rate, and activities Function -------------------------------------------------------------------------
    def get_flight_power_soc_rate(self, id: list, activities_filter: list):
        """
        Function that uses the flight ids to get their respective time, motor power, soc, soc rate of change, and activity columns. 
        Then, returns a dictionary of 
        fw_flight_id: {time: [], motor_power: [], soc: [], soc_rate_of_change: [], activity: []}
        """
        # Initialize the dictionary
        flight_dict = {}

        # Get the flight data
        flights_df = self.get_flight_data_every_half_min_on_id(id)

        # Change to Numpy
        times = flights_df["time_min_rounded"].to_numpy()
        motor_power = flights_df["motor_power"].to_numpy()
        activity = flights_df["activity"].to_numpy()
        soc = (flights_df["bat_1_soc"].to_numpy() + flights_df["bat_2_soc"].to_numpy()) / 2 # get soc avg

        # Calculate SOC rate of change
        # The rate of change for the last entry will be set to 0 since there is no next entry to compare with
        soc_rate_of_change = (soc[1:] - soc[:-1]) / (times[1:] - times[:-1])
        # Append a 0 to soc_rate_of_change to keep the array sizes consistent
        soc_rate_of_change = np.append(soc_rate_of_change, 0)

        # Filter based on activities_filter
        # If certain activities are selected by the user in the filter, update the variables
        # Otherwise, it will default to all activities in the flight
        if(len(activities_filter) != 0):
            filter_mask = np.isin(activity, activities_filter)
            times = times[filter_mask]
            motor_power = motor_power[filter_mask]
            soc = soc[filter_mask]
            soc_rate_of_change = soc_rate_of_change[filter_mask]
            activity = activity[filter_mask]

        flight_dict[id] = {"time_min_rounded": times, "motor_power": motor_power, "soc": soc, "soc_rate_of_change": soc_rate_of_change, "activity": activity}

        return flight_dict
    

    # Function --------------------------------------------------------------------------------
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
    

    def get_flight_activities(self):
        """
            Function that gets a list of all possible unique flight activities from the labeled_activities_view
            Query: select distinct activity from labeled_activities_view;
        """
        engine = self.connect()
        query = f"""select distinct activity from labeled_activities_view;"""

        # Put the result of the query in a list
        activities_list = pd.read_sql_query(query, engine).to_numpy().tolist()
        result_list = []

        for i in range(len(activities_list)):
            result_list.append(activities_list[i][0])

        # Dispose of the connection, so we don't overuse it.
        engine.dispose()

        return result_list
    
    
    def get_soc_roc_stats_by_id(self, flight_id):
        """
        Function that uses a flight id to get the soc rate of change and calculates its stats (min, max, mean, standard deviation, variance). 
        Then, returns the statistics in a dataframe.
        """
        engine = self.connect()

        # Get the flight data
        result_df = self.get_flight_data_every_half_min_on_id(flight_id)

        # Change to Numpy
        times = result_df["time_min_rounded"].to_numpy()
        activity = result_df["activity"].to_numpy()
        soc = (result_df["bat_1_soc"].to_numpy() + result_df["bat_2_soc"].to_numpy()) / 2 # get soc avg

        # Calculate SOC rate of change
        # The rate of change for the last entry will be set to 0 since there is no next entry to compare with
        soc_rate_of_change = (soc[1:] - soc[:-1]) / (times[1:] - times[:-1])

        # Append a 0 to soc_rate_of_change to keep the array sizes consistent
        soc_rate_of_change = np.append(soc_rate_of_change, 0)

        # Dispose of the connection, so we don't overuse it.
        engine.dispose()

        # Add activity and SOC information into dataframe
        df = pd.DataFrame({
            "Activity": activity,
            "SOC Rate of Change": soc_rate_of_change
        })

        # Compute max, min, mean, standard deviation, and variance, and reset index
        statistics_df = df.groupby('Activity')['SOC Rate of Change'].agg(['max', 'min', 'mean', 'std', 'var']).reset_index()

        return statistics_df

    # JOIN ML tables Function ------------------------------------------------------------------------------------------------------------
    def connect_flight_for_ml_data_label(self, flight: int):

        # Make database connection
        engine = self.connect()

        # Make the query
        query = f"""SELECT tfa.time_min AS Time,
                        tfa.flight_id AS id, 
                        tfa.activity AS Exercise,
                        tfa.temperature AS Environment_Temperature,
                        tfa.dewpoint AS Dewpoint,
                        tfa.relative_humidity AS Humidity,
                        tfa.wind_speed AS Wind_Speed,
                        tfa.visibility AS Visibility,
                        ((fl.bat_1_soc + fl.bat_2_soc) / 2) AS SOC,
                        ((fl.bat_1_avg_cell_temp + fl.bat_2_avg_cell_temp) / 2) AS Cell_Temperature,
                        fl.motor_rpm AS Motor_RPM, 
                        fl.motor_power AS Motor_Power,
                        fl.motor_temp AS Motor_Temperature,
                        fl.ias AS Indicated_Air_Speed,
                        fl.pressure_alt AS Pressure_Altitude,
                        fl.ground_speed AS Ground_Speed,
                        fl.oat AS Outside_Air_Temperature,
                        fl.inverter_temp AS Inverter_Temperature,
                        fl.pitch AS Pitch,
                        fl.roll AS Roll
                    FROM labeled_activities_view \"tfa\" 
                    INNER JOIN flightdata_{flight} \"fl\" 
                        ON tfa.time_min=fl.time_min AND tfa.flight_id=fl.flight_id
                    WHERE fl.flight_id={flight}"""

        # Select the data based on the query
        flight_data = pd.read_sql_query(query, engine) 

        # Dispose of the connection, so we don't overuse it.
        engine.dispose()

        # Return the data
        return flight_data
    

    # JOIN ML tables Function ------------------------------------------------------------------------------------------------------------
    def connect_flight_for_ml_data_prescription(self, flight: int):

        # Make database connection
        engine = self.connect()

        # Make the query
        query = f"""SELECT 
                        fw_flight_id, 
                        activity,
                        time_min AS time,
                        ((bat_1_soc + bat_2_soc) / 2) AS soc,
                        motor_power AS power
                    FROM labeled_activities_view  
                    WHERE fw_flight_id={flight}
                    ORDER BY time;
        """

        # Select the data based on the query
        flight_data = pd.read_sql_query(query, engine) 

        # Dispose of the connection, so we don't overuse it.
        engine.dispose()

        # Return the data
        return flight_data


