from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import os
import psycopg2
from time import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from storage import execute, select

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
    
    # Getting the activities -------------------------------------------------------------------------------------------------
    def get_unique_activity(self):
        """
        The function uses psycopg2 to get unique columns
        """

        # Make database connection
        engine = self.connect()

        query_string = "select distinct(activity) from labeled_activities_view order by activity;"
        df = pd.read_sql_query(query_string, engine)
        activities = list(df["activity"].to_numpy())

        # Dispose of the connection, so we don't overuse it.
        engine.dispose()

        # Return the activities
        return activities
    

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

        # Dispose of the connection, so we don't overuse it.
        engine.dispose()

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

        # Make database connection
        engine = self.connect()

        # Select the data based on the query
        flights = pd.read_sql_query(query, engine)

        # Dispose of the connection, so we don't overuse it.
        engine.dispose()

        return flights
    
    # get all Flight IDs ------------------------------------------------------------------------------------------------------------
    def get_flight_ids(self):
        """
        The function runs the following query: SELECT id FROM flights. This gets all the flight IDs in the database.
        """
        query = "SELECT id FROM flights"
        engine = self.connect()
        flight_ids = pd.read_sql_query(query, engine)
        engine.dispose()
        return flight_ids
    
    # add flight to flight activities table ------------------------------------------------------------------------------------------------------------
    def add_flight_activities(self, id: int):
        """
        The function runs the following query: INSERT INTO flight_activities (flight_id, time_min) SELECT flight_id, time_min FROM flightdata_<ID>. 
        This adds the flight with the given id to the flight_activities table
        """
        query = f"INSERT INTO flight_activities (flight_id, time_min) SELECT flight_id, time_min FROM flightdata_{str(id)}"
        execute(query, id)

    # add flight activity to a given flight id and time_min ------------------------------------------------------------------------------------------------------------
    def add_flight_activity(self, flight_id: int, time_min: float, activity: str):
        """
        The function runs the following query: UPDATE flight_activities SET activity={activity} WHERE flight_id={flight_id} AND time_min={time_min}
        This should be run after a flight is labelled and has activity mappings that need to be pushed to the flight_activities table
        """
        query = f"UPDATE flight_activities SET activity='{str(activity)}' WHERE flight_id={str(flight_id)} AND time_min={time_min}"
        execute(query)

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
        The function runs a query to get the fw_flight_id, activity, time, soc, power, soh, date from labeled activities view in 30 sec intervals.
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
                    AVG(motor_power) AS motor_power,
                    AVG(bat_1_soh) AS bat_1_soh,
                    AVG(bat_2_soh) AS bat_2_soh,
                    flight_date AS dates
                FROM
                    labeled_activities_view
                WHERE
                    fw_flight_id = {str(id)} and bat_1_soh != 0 and bat_2_soh != 0
                GROUP BY
                    fw_flight_id, activity, time_min_rounded, dates
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
    
    # Get AVG SOH per month Function (labeled activities view) ---------------------------------------------------------------------------------
    def get_avg_soh_per_month_act_view(self):

        # Make database connection
        engine = self.connect()

        # Make query
        query = f"""
                SELECT 
                    DATE_TRUNC('month', flight_date) as flight_date, 
                    AVG(bat_1_soh) as bat_1_soh, 
                    AVG(bat_2_soh) as bat_2_soh
                FROM 
                    labeled_activities_view 
                WHERE  
                    bat_1_soh != 0 and bat_2_soh != 0
                GROUP BY 
                    DATE_TRUNC('month', flight_date)
                ORDER BY 
                    DATE_TRUNC('month', flight_date);

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
    
    # Get Flight Id, SOH, SOC rate Function -------------------------------------------------------------------------
    def get_flight_soh_soc_rate(self, id: list):
        """
        Function that uses the flight ids to get their respective time, soh, soc, and soc rate of change columns. 
        Then, returns a dictionary of 
        fw_flight_id: {time: [], soc: [], soc_rate_of_change: [], soh: []}
        """
        # Initialize the dictionary
        flight_dict = {}

        # Get the flight data
        flights_df = self.get_flight_data_every_half_min_on_id(id)

        # Change to Numpy
        times = flights_df["time_min_rounded"].to_numpy()
        dates = flights_df["dates"].iloc[0].strftime("%b %d, %Y")
        soc = (flights_df["bat_1_soc"].to_numpy() + flights_df["bat_2_soc"].to_numpy()) / 2 # get soc avg
        soh = (flights_df["bat_1_soh"].to_numpy() + flights_df["bat_2_soh"].to_numpy()) / 2 # get soh avg

        # Calculate SOC rate of change
        # The rate of change for the last entry will be set to 0 since there is no next entry to compare with
        soc_rate_of_change = (soc[1:] - soc[:-1]) / (times[1:] - times[:-1])
        # Append a 0 to soc_rate_of_change to keep the array sizes consistent
        soc_rate_of_change = np.append(soc_rate_of_change, 0)

        flight_dict[id] = {"time_min_rounded": times, "soc": soc, "soc_rate_of_change": soc_rate_of_change, "soh": soh, "dates": dates}

        return flight_dict
    
    # Get Date, SOH Function -------------------------------------------------------------------------
    def get_flight_soh(self):
        """
        Function that gets dates and soh columns. 
        Then, returns a dictionary of {dates: [], soh: []}
        """
        # Initialize the dictionary
        flight_dict = {}

        # Get the flight data
        flights_df = self.get_avg_soh_per_month_act_view()

        dates = flights_df["flight_date"]
        # Change to Numpy
        soh = (flights_df["bat_1_soh"].to_numpy() + flights_df["bat_2_soh"].to_numpy()) / 2 # get soh avg


        flight_dict = {"soh": soh, "dates": dates}

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
    
    def get_last_scraper_runtime(self):
        """
            Function that returns the most recent runtime of the scraper
        """
        return select("select * from scraper_last_run")[0]
    
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
        query = f"""SELECT flight_id AS id, 
                        time_min AS time,
                        ((bat_1_soc + bat_2_soc) / 2) AS soc,
                        ((bat_1_avg_cell_temp + bat_2_avg_cell_temp) / 2) AS cell_temperature,
                        motor_rpm AS motor_rpm, 
                        motor_power AS motor_power,
                        motor_temp AS motor_temperature,
                        ias AS indicated_air_speed,
                        pressure_alt AS pressure_altitude,
                        ground_speed AS ground_speed,
                        oat AS outside_air_temperature,
                        inverter_temp AS inverter_temperature,
                        pitch AS pitch,
                        roll AS roll,
                        activity AS exercise
                    FROM labeled_activities_view
                    WHERE flight_id={flight}"""

        # Select the data based on the query
        flight_data = pd.read_sql_query(query, engine) 

        # Dispose of the connection, so we don't overuse it.
        engine.dispose()

        # Return the data
        return flight_data
    
    # get flight data for labelling ------------------------------------------------------------------------------------------------------------
    def get_flightdata_for_ml_data_label(self, flight: int):
        """
        Function that given a flight id returns the data needed to label exercises for that flight.
        """
        engine = self.connect()

        query = f"""SELECT flight_id AS id, 
                        time_min AS time,
                        ((bat_1_soc + bat_2_soc) / 2) AS soc,
                        ((bat_1_avg_cell_temp + bat_2_avg_cell_temp) / 2) AS cell_temperature,
                        motor_rpm AS motor_rpm, 
                        motor_power AS motor_power,
                        motor_temp AS motor_temperature,
                        ias AS indicated_air_speed,
                        pressure_alt AS pressure_altitude,
                        ground_speed AS ground_speed,
                        oat AS outside_air_temperature,
                        inverter_temp AS inverter_temperature,
                        pitch AS pitch,
                        roll AS roll
                    FROM flightdata_{flight};
                """

        flight_data = pd.read_sql_query(query, engine) 
        engine.dispose()
        return flight_data

    # JOIN ML tables Function ------------------------------------------------------------------------------------------------------------
    def connect_flight_for_ml_data_prescription(self, flight: int):

        # Make database connection
        engine = self.connect()

        query = f"""SELECT time_min AS Time,
                        flight_id AS id, 
                        activity,
                        ((bat_1_soc + bat_2_soc) / 2) AS SOC,
                        ((bat_1_soh + bat_2_soh) / 2) AS SOH,
                        motor_power AS Power,
                        temperature,
                        visibility,
                        wind_speed
                    FROM labeled_activities_view  
                    WHERE labeled_activities_view.flight_id={flight}
                    ORDER BY Time"""

        # Select the data based on the query
        flight_data = pd.read_sql_query(query, engine) 

        # Dispose of the connection, so we don't overuse it.
        engine.dispose()

        # Return the data
        return flight_data
    

    # Getting the weather predictions from the forecast table ----------------------------------------------------------------------------
    # From Example 1 here: https://www.geeksforgeeks.org/get-column-names-from-postgresql-table-using-psycopg2/
    def get_forecast_weather_by_date(self, date: datetime, time: datetime):
        """
        The function uses psycopg2 to get the columns: temperature, wind gust, and visibility from the forecast table
        """

        # Format the time 
        compare_time = datetime.strptime(time, "%I:%M %p").strftime("%H:%M:%S")

        # Make database connection
        engine = self.connect()

        # Make and execute the query
        sql_query = f"""SELECT 
            temperature_2m as temperature, 
            visibility, 
            windgusts_10m as wind_speed 
        FROM forecast
        WHERE forecast_date = \'{date}\' and forecast_time_et = \'{compare_time}\';
        """
        flights = pd.read_sql_query(sql_query, engine)

        temp = flights.iloc[0, 0]
        visibility = flights.iloc[0, 1]
        wind_speed = flights.iloc[0, 2]

        # Dispose of the connection, so we don't overuse it.
        engine.dispose()

        # Return the data
        return temp, visibility, wind_speed
