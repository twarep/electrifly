from dotenv import load_dotenv
import os
import psycopg2
import pytest
import queries

class TestDatabase:
  # test the connection
  def test_connect(self):
    load_dotenv()
    connection_string = os.getenv('TEST_DATABASE_URL')
    conn = psycopg2.connect(connection_string)

  # use the connection as a fixture for other tests
  @pytest.fixture
  def connect(self):
    load_dotenv()
    connection_string = os.getenv('TEST_DATABASE_URL')
    conn = psycopg2.connect(connection_string)
    yield conn

  def test_create_tables(self, connect):
    cur = connect.cursor()
    table_list = ['flights', 'weather', 'flight_weather']
    create_queries = {'flights': queries.CREATE_FLIGHTS, 
                      'weather': queries.CREATE_WEATHER, 
                      'flight_weather': queries.CREATE_FLIGHT_WEATHER}
    for table in table_list:
      cur.execute(create_queries[table])