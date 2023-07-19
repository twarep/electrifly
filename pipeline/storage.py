# this file has all commands related to storing data in the database

import psycopg2
import os
from dotenv import load_dotenv

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
  print(list(df.columns.values))
  print(flight_id)