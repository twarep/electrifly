from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import pandas as pd
import zipfile
import os
import time
import psycopg2
import shutil
import datetime as dt
from datetime import datetime, date
import re
from transformation import transform_overview_data, weather_transformation
from storage import table_exists, view_exists, db_connect, execute, select, push_flight_metadata, push_flight_data, push_scraper_runtime, relevant_weather
import queries
import platform
import pytz

# Path variables
chromedriver_path = "./dependencies/chromedriver-win64/chromedriver.exe"
def log_last_run_time():
    # check if the scraper_last_run table exists
    conn = db_connect()
    if not table_exists('scraper_last_run', conn):
      execute(queries.SCRAPER_RUNTIME)
    current_time = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Check the system timezone
    system_timezone = dt.datetime.now(dt.timezone.utc).astimezone().tzinfo
    if system_timezone != pytz.timezone('America/New_York'):
        # Convert time to Eastern Time
        wrong_tz = dt.datetime.now()
        est_tz = pytz.timezone('America/New_York')
        est_time = wrong_tz.astimezone(est_tz)
        current_time = est_time.strftime('%Y-%m-%d %H:%M:%S')
    # insert the current time into table
    push_scraper_runtime(current_time)

# converts the string time given by Pipistrel UI to a datetime object
def convert_str_to_datetime(str_datetime: str):

  if re.search(":", str_datetime):

    # convert a.m. and p.m. to readable format
    if str_datetime[-4:] == "a.m.":
      str_datetime = str_datetime[:-4] + "AM"
    elif str_datetime[-4:] == "p.m.":
      str_datetime = str_datetime[:-4] + "PM"
  else:
    if str_datetime[-4:] == "a.m.":
      str_datetime = str_datetime[:-5] + ":00 AM"
    elif str_datetime[-4:] == "p.m.":
      str_datetime = str_datetime[:-5] + ":00 PM"
  
  if "noon" in str_datetime:
    str_datetime = str_datetime.replace("noon", "12:00 PM")

  if "." in str_datetime:
    if "Sept" in str_datetime:
      str_datetime = str_datetime.replace("Sept", "Sep")
    format = "%b. %d, %Y, %I:%M %p"
  else:
    format = "%B %d, %Y, %I:%M %p"

  return datetime.strptime(str_datetime, format)

# returns the relevant weather data for the given scraped flights
def weather_data(date_list, ids_list, driver, download_dir):
  # get the oldest date
  oldest_datetime = min(date_list)
  newest_date = max(date_list).date()
  newest_day = newest_date.day
  # extract each part of the date
  year = oldest_datetime.strftime("%Y")
  month = oldest_datetime.strftime("%m")
  day = oldest_datetime.strftime("%d")
  # get the current date, add 1 day to include today
  current_date = date.today()
  current_year = current_date.year
  current_month = current_date.month
  current_day = current_date.day + 1
  # dynamic download url
  weather_download_url = (
    f"https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?"
    f"station=CYKF&data=all&year1={year}&month1={month}&day1={day}&"
    f"year2={current_year}&month2={current_month}&day2={current_day}&"
    f"tz=Etc%2FUTC&format=onlycomma&latlon=no&elev=no&missing=M&trace=T&direct=yes&"
    f"report_type=3&report_type=4"
  )
  # read the new data into pandas df
  weather_data_path = os.path.join(os.getcwd(),'temp','CYKF.csv')

  # get the weather data
  driver.get(weather_download_url)
  time_counter = 0
  time_to_wait = 15
  # allow 15 seconds to download the weather csv
  while not os.path.exists(weather_data_path):
    time.sleep(1)
    time_counter += 1
    if time_counter > time_to_wait:
      break

  df = pd.read_csv(weather_data_path)
  # transform the weather_data into DB format
  df = weather_transformation(df)
  # map out each weather data field to a flight
  relevant_weather(df, ids_list)

  # delete the temp files from disk
  shutil.rmtree(download_dir,ignore_errors=True)

def environment_setup():
  # Load .env file
  load_dotenv()

  # delete the temp directory if it exists
  temp_dir = os.path.join(os.getcwd(),'temp')
  if os.path.exists(temp_dir) and os.path.isdir(temp_dir):
    shutil.rmtree(temp_dir, ignore_errors=True)
  # set download directory to working directory
  download_dir = os.path.join(os.getcwd(),'temp')

  chrome_options = webdriver.ChromeOptions()

  # download preferences
  prefs = {
      "download.default_directory": download_dir,
      "safebrowsing.enabled": "false"
  }

  data_directory_arg = "user-data-dir=" + download_dir

  chrome_options.add_experimental_option("prefs", prefs)
  chrome_options.add_argument(data_directory_arg)
  # set up Chrome webdriver
  if "Windows" == platform.system():
    driver = webdriver.Chrome(service=ChromeService(chromedriver_path), options=chrome_options)
  else:
    driver = webdriver.Chrome(options=chrome_options)
  
  # get the connection string from the environment variable
  connection_string = os.getenv('DATABASE_URL')

  # connect to the PostgreSQL database
  conn = psycopg2.connect(connection_string)

  # create a cursor object for the db
  cur = conn.cursor()
  return {'driver': driver, 'cursor': cur, 'download_dir': download_dir}

def pipistrel_login(driver):
  # get login credentials for Pipistrel UI
  username = os.getenv("user")
  password = os.getenv("password")

  # go to Pipistrel UI
  pipistrel_ui = os.getenv("PIPISTREL_UI")
  driver.get(pipistrel_ui)

  # log in if the user is not logged in
  if "Paul Parker" not in driver.page_source:
    # find username field and enter the username
    user_form = driver.find_element(By.ID, "id_username")
    user_form.send_keys(username)

    # find password field and enter the password
    pass_form = driver.find_element(By.ID, "id_password")
    pass_form.send_keys(password)

    # click sign in
    driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/form/button").click()

def get_plane_info(driver):
  # click on the aircraft to get details for the plane we are flying
  driver.find_element(By.CLASS_NAME, "clickable-aircraft").click()

# create tables if they don't exist
def create_tables():
  table_list = ['flights', 'weather', 'flight_weather']
  create_queries = {'flights': queries.CREATE_FLIGHTS, 
                    'weather': queries.CREATE_WEATHER, 
                    'flight_weather': queries.CREATE_FLIGHT_WEATHER}
  for table in table_list:
    conn = db_connect()
    if not table_exists(table, conn):
      execute(create_queries[table])

# create views if they don't exist
def create_views():
  view_list = ['flight_weather_data_view']
  create_queries = {'flight_weather_data_view': queries.CREATE_FLIGHT_WEATHER_VIEW}
  for view in view_list:
    execute(create_queries[view])

# create the flight_activities table and views
def flight_activity_tables_views():
  query_list = [queries.CREATE_FLIGHT_ACTIVITIES,
                queries.ADD_ACTIVITY_COLUMN,
                queries.LABEL_4620, queries.LABEL_4929,
                queries.LABEL_4940, queries.LABEL_5019,
                queries.LABEL_5021, queries.LABEL_5034,
                queries.LABEL_4636,queries.LABEL_4842,
                queries.LABEL_4868,queries.LABEL_4925,
                queries.LABEL_4978,queries.LABEL_5116,
                queries.LABEL_5362,
                queries.LABELED_ACTIVITIES_VIEW,
                queries.PILOT_WEIGHTS
                ]
  for query in query_list:
    execute(query)

def scrape(driver, cur, download_dir):
  # then get each data row for the given plane
  rows = driver.find_elements(By.CLASS_NAME, "clickable-aircraft")

  # tracks if there is a next page in the table
  is_next_page = True

  # list of dates to determine how far back to scrape weather data
  date_list = []
  # list of flight ids added to db to properly link weather to flights
  ids_list = []

  # get flight data while we have more pages of data to look through
  while is_next_page:
    
    # Iterate over the rows and extract the data from each column
    for row in rows:

      # find all of the table elements in the given row
      cells = row.find_elements(By.TAG_NAME, "td")

      # get the data from each row into a list
      row_data = [cell.text for cell in cells]
      current_flight_id = row_data[0]
      current_flight_str_datetime = row_data[1]
      current_flight_datetime = convert_str_to_datetime(current_flight_str_datetime)
      current_flight_type = row_data[2]
      current_flight_notes = row_data[4]

      # query database for this flight ID
      cur.execute('SELECT 1 FROM flights WHERE id = %s', (int(current_flight_id), ))
      flight_id = cur.fetchone()

      # if the flight id is in the database, skip this row
      if flight_id is not None:
          continue
      # otherwise click on flight details
      else:
          # click this row
          row.click()
      
      download_csv_link = driver.find_elements(By.LINK_TEXT, "Download CSV file")
      # if the file is currently processing, there will be no download link, so skip this one for now
      if not download_csv_link:
        driver.back()
      else:      
        # get the download link
        current_download_link = download_csv_link[0].get_attribute("href")
        # check if the current filename is available, if not then continue
        if str(current_flight_id) not in str(current_download_link):
          driver.back()
          continue
        push_flight_metadata(current_flight_id, current_flight_datetime, current_flight_notes, current_flight_type)
        ids_list.append(current_flight_id)
        date_list.append(current_flight_datetime)   
        current_file_name = os.path.basename(current_download_link)
        # click the link
        download_csv_link[0].click()
        new_file_path = os.path.join(download_dir, current_file_name)
        timeout = 0
        # wait until the file downloads
        while not os.path.exists(new_file_path):
          time.sleep(0.05)
          timeout += 0.05
          # timeout the download at 25 seconds
          if timeout == 25:
            raise Exception("Timeout of 25 seconds reached to download. Please try again.")
        # extract the downloaded file
        with zipfile.ZipFile(new_file_path, 'r') as zip:
          zip.extractall(download_dir)
        # open all new files as pandas data frames
        normal_data_path = new_file_path[:-4] + ".csv"
        df = pd.read_csv(normal_data_path)
        # transform the data into something to put into the database
        df = transform_overview_data(df)
        # push the flight data into the database
        push_flight_data(df, current_flight_id, current_flight_type)
        # delete the temp files from disk
        shutil.rmtree(download_dir, ignore_errors=True)
        driver.back()
        
      # locate the row after page refresh
      time.sleep(0.1)
      rows = driver.find_elements(By.CLASS_NAME, "clickable-aircraft")

    # check for more pages of data
    next_page = driver.find_elements(By.LINK_TEXT, "Next")
    # if there is, go to the next page, otherwise break
    if next_page:
      time.sleep(0.05)
      next_page[0].click()
      rows = driver.find_elements(By.CLASS_NAME, "clickable-aircraft")
    else:
      is_next_page = False
      break
  if ids_list:
    weather_data(date_list, ids_list, driver, download_dir)
  else:
    print("There are no new flights to push to database.")

  conn = db_connect()
  # check if flight_activities table exists and the manually labelled flightdata exists
  if not table_exists('flight_activities', conn) and select(queries.MANUAL_FLIGHTS_TO_LABEL)[0]:
    flight_activity_tables_views()
    print("Flight activity table and view added, with six manually labelled flights, and pilot weights added")

if __name__ == '__main__':
  log_last_run_time()
  env = environment_setup()
  pipistrel_login(env['driver'])
  get_plane_info(env['driver'])
  create_tables()
  create_views()
  scrape(env['driver'], env['cursor'], env['download_dir'])
