# this file has all commands related to storing data in the database

import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.types import Float
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pandas as pd

# this function creates and returns a connection to the database
def db_connect():
  # Load .env file
  load_dotenv()

  # Get the connection string from the environment variable
  connection_string = os.getenv('DATABASE_URL')

  # Connect to the PostgreSQL database
  conn = psycopg2.connect(connection_string)
  return conn

# this function disconnects the given connection from the database
def db_disconnect(conn):
  conn.close()

# this function checks if the given table exists
def table_exists(table, conn):
  
  # create a cursor object to interact with the database
  cursor = conn.cursor()
  
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
  db_disconnect(conn)
  
  return exists

# this function checks if the given view exists
def view_exists(view, conn):
  
  # create a cursor object to interact with the database
  cursor = conn.cursor()
  
  # check if the given view exists
  cursor.execute("""
      SELECT EXISTS (
          SELECT 1
          FROM pg_catalog.pg_views
          WHERE viewname = %s
      );
  """, (view,))
  # fetch the result
  exists = cursor.fetchone()[0]
  
  # close the cursor and the connection
  cursor.close()
  db_disconnect(conn)
  
  return exists

# this function executes the given create query
def execute(query, data=None):
  conn = db_connect()
  # create a cursor object to interact with the database
  cursor = conn.cursor()
  
  # create the flights table
  cursor.execute(query, data)
  
  # commit the transaction
  conn.commit()
  
  # close the cursor and the connection
  cursor.close()
  db_disconnect(conn)

# this function executes the given select query
def select(query, params=None):
  conn = db_connect()
  # create a cursor object to interact with the database
  cursor = conn.cursor()
  
  # execute the query
  cursor.execute(query, params)

  result = cursor.fetchone()
  
  # close the cursor and the connection
  cursor.close()
  db_disconnect(conn)

  return result

# takes in flight metadata and pushes it to the flights table
def push_flight_metadata(id, datetime, notes):
  # separate date and time
  date = datetime.date()
  time = datetime.time()
  insert_query = "INSERT INTO flights (id, flight_date, flight_time_utc, flight_notes) VALUES (%s, %s, %s, %s)"
  values = (id, date, time, notes)
  execute(insert_query, values)

# takes in flight data df, and pushes it to its own data table
def push_flight_data(df, flight_id):
  columns = list(df.columns.values)
  # lowercase and underscore the spaces
  modified_columns = [col.replace(" ", "_").lower() for col in columns]
  # fix the time columns
  modified_columns[0] = "time_min"
  modified_columns[36] = "time_stamp"
  # replace the initial column names in the df
  df = df.set_axis(modified_columns, axis="columns")
  # add the flight_id column to df
  df.insert(0, "flight_id", int(flight_id))
  # table name
  table_name = "flightdata_" + str(flight_id)
  # create sqlalchemy connection
  engine_string = "postgresql+psycopg2" + os.getenv('DATABASE_URL')[8:]
  engine = create_engine(engine_string)
  # set column types explicitly for error prevention for empty columns
  explicit_columns = {'lat': Float(), 'lng': Float(), 'ground_speed': Float(),
                      'motor_temp': Float(), 'ias': Float(), 'inverter_temp': Float(),
                      'pressure_alt': Float(), 'pitch': Float(), 'roll': Float(),
                      'heading': Float(), 'stall_diff_pressure': Float(), 'qng': Float(),
                      'oat': Float()}
  # add new table to db
  df.to_sql(table_name, engine, if_exists="fail", index=False, dtype=explicit_columns)
  engine.dispose()  

# query weather df for all records in between the given times
def query_weather_df(df, date, start_time, end_time):
  # Filter the DataFrame based on the conditions
  filtered_df = df[
      (df['weather_date'] == date) &
      (df['weather_time_utc'] >= start_time) &
      (df['weather_time_utc'] <= end_time)
  ]
  return filtered_df

# creates a relationship between flight id and weather id
def weather_flight_rel(filtered_df):
  weather_id_list = []
  flight_id_list = []
  min_time_list = []
  max_time_list = []
  # query filtered_df to get the id of all records with the needed dates and times
  for index, row in filtered_df.iterrows():
    weather_date = row["weather_date"]
    weather_time_utc = row["weather_time_utc"]
    weather_query = "SELECT id FROM weather WHERE weather_date=%s AND weather_time_utc=%s"
    weather_values = (weather_date, weather_time_utc,)
    # get weather id for the current record
    current_weather_id = select(weather_query, weather_values)
    weather_id_list.append(current_weather_id[0])
    # find flight id that occurred on the same day
    flight_query = "SELECT id FROM flights WHERE flight_date=%s"
    flight_values = (weather_date,)
    current_flight_id = select(flight_query, flight_values)
    flight_id_list.append(current_flight_id[0])
    # get the min and max times for the given flight
    min_time_query = "SELECT MIN(weather_time_utc) FROM weather WHERE weather_date=%s"
    max_time_query = "SELECT MAX(weather_time_utc) FROM weather WHERE weather_date=%s"
    current_flight_min_time = select(min_time_query, flight_values)
    min_time_list.append(current_flight_min_time[0])
    current_flight_max_time = select(max_time_query, flight_values)
    max_time_list.append(current_flight_max_time[0])
    # push these values to flight_weather table
    flight_weather_insert_query = "INSERT INTO flight_weather (flight_id, weather_id) VALUES (%s, %s)"
    values = (current_flight_id[0], current_weather_id[0])
    execute(flight_weather_insert_query, values)



# takes in weather dataframe and id list, queries flights to 
# determine which weather data corresponds to which flight
def relevant_weather(df, id_list):
  id_query = "SELECT flight_date, flight_time_utc FROM flights WHERE id= %s"
  # loop through each id and get the flight date and time
  for id in id_list:
    flight_info = select(id_query, (id,))
    current_date = flight_info[0]
    current_time = flight_info[1]
    # query how long this flight was in minutes
    flight_len_query = "SELECT MAX(time_min) FROM flightdata_" + str(id)
    flight_len = select(flight_len_query)
    datetime_obj = datetime.combine(current_date, current_time)
    # calculate the end time of the flight
    flight_end_datetime = datetime_obj + timedelta(minutes=flight_len[0])
    flight_end_time = flight_end_datetime.time()
    # given the start and end times, query the weather df for all records in that time period
    filtered_df = query_weather_df(df, current_date, current_time, flight_end_time)
    # create sqlalchemy connection
    engine_string = "postgresql+psycopg2" + os.getenv('DATABASE_URL')[8:]
    engine = create_engine(engine_string)
    # insert new weather data into weather table
    filtered_df.to_sql("weather", engine, if_exists="append", index=False)
    # create relationship between flight and newly added weather data
    weather_flight_rel(filtered_df)
    engine.dispose()


