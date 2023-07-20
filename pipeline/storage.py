# this file has all commands related to storing data in the database

import psycopg2
from sqlalchemy import create_engine
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
  # add new table to db
  df.to_sql(table_name, engine, if_exists="fail", index=False)
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
    # add new table to db
    filtered_df.to_sql("weather", engine, if_exists="append", index=False)
    engine.dispose()    
