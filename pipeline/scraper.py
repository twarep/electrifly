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
from datetime import datetime
import re
from transformation import transform_overview_data

# converts the string time given by Pipistrel UI to a datetime object
def convert_str_to_datetime(str_datetime):
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

  format = "%B %d, %Y, %I:%M %p"
  return datetime.strptime(str_datetime, format)

# returns the relevant weather data for the given scraped flights
def weather_data(date_list):
  # get the weather data
  driver.get("https://mesonet.agron.iastate.edu/request/download.phtml?network=CA_ON_ASOS")
  # get the oldest date
  oldest_datetime = min(date_list)
  # extract each part of the date
  year = oldest_datetime.strftime("%Y")
  month = oldest_datetime.strftime("%m")
  day = oldest_datetime.strftime("%d")
  # find the relevant date dropdowns
  year_select = Select(driver.find_element(By.NAME, "year1"))
  month_select = Select(driver.find_element(By.NAME, "month1"))
  day_select = Select(driver.find_element(By.NAME, "day1"))
  time.sleep(3)
  # select data from that oldest date
  year_select.select_by_value(year)
  month_select.select_by_value(month[1:])
  if int(day) < 10:
    day_select.select_by_value(day[1:])
  else:
    day_select.select_by_value(day)
  # select the waterloo airport only (cykf)
  waterloo_airport_option = Select(driver.find_element(By.ID, "stations_in"))
  waterloo_airport_option.select_by_value("CYKF")
  driver.find_element(By.ID, "stations_add").click()
  # click on the correct download option
  download_option = Select(driver.find_element(By.NAME, "direct"))
  download_option.select_by_value("yes")
  # click on the get data button
  driver.find_element(By.XPATH, "/html/body/main/div/div[3]/div[2]/input[4]").click()
  time.sleep(5)
  # read the new data into pandas df
  weather_data_path = os.getcwd() + "/temp/CYKF.csv"
  df = pd.read_csv(weather_data_path)
  print(df.head())
  # delete the temp files from disk
  shutil.rmtree(download_dir)

# Load .env file
load_dotenv()

# set download directory to working directory
download_dir = os.getcwd() + "/temp"

# download preferences
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
}

chrome_options = Options()
chrome_options.add_experimental_option("prefs", prefs)

# set up Chrome webdriver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

# get the connection string from the environment variable
connection_string = os.getenv('DATABASE_URL')

# connect to the PostgreSQL database
conn = psycopg2.connect(connection_string)

# create a cursor object for the db
cur = conn.cursor()

# get login credentials for Pipistrel UI
username = os.getenv("user")
password = os.getenv("password")

# go to Pipistrel UI
pipistrel_ui = os.getenv("PIPISTREL_UI")
driver.get(pipistrel_ui)

# find username field and enter the username
user_form = driver.find_element(By.ID, "id_username")
user_form.send_keys(username)

# find password field and enter the password
pass_form = driver.find_element(By.ID, "id_password")
pass_form.send_keys(password)

# click sign in
driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/form/button").click()

# click on the aircraft to get details for the plane we are flying
aircraft_details = driver.find_element(By.CLASS_NAME, "clickable-aircraft").click()

# then get each data row for the given plane
rows = driver.find_elements(By.CLASS_NAME, "clickable-aircraft")

# tracks if there is a next page in the table
is_next_page = True

# list of dates to determine how far back to scrape weather data
date_list = []

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
    # skip all rows except for flight tests
    if current_flight_type not in ["Flight test and charging", "Flight test"]:
      continue

    # TODO: break criteria ################ will activate this once database schema is set up
    # query database for this flight ID
    #cur.execute('SELECT flight_id FROM flights WHERE flight_id = %s', (current_flight_id, ))
    #flight_id = cur.fetchone()

    # if the flight id is in the database, stop checking for new data
    #if flight_id is not None:
    #    break
    # otherwise add the flight details to database
    #else:
        # date_list.append(current_flight_datetime)
        # click this row
        # row.click()

    ###########################################
    # if we are scraping this record, add the time to the list of times
    date_list.append(current_flight_datetime)
    row.click()
    
    download_csv_link = driver.find_elements(By.LINK_TEXT, "Download CSV file")
    # if the file is currently processing, there will be no download link, so skip this one for now
    if not download_csv_link:
      driver.back()
    else:       
      # get the download link
      current_download_link = download_csv_link[0].get_attribute("href")
      # get the name of the file to download
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
      transform_overview_data(df)
      # delete the temp files from disk
      shutil.rmtree(download_dir)
      driver.back()
      
    # locate the row after page refresh
    time.sleep(0.1)
    rows = driver.find_elements(By.CLASS_NAME, "clickable-aircraft")

  # check for more pages of data
  next_page = driver.find_elements(By.LINK_TEXT, "Next")
  # if there is, go to the next page, otherwise 
  if next_page:
    time.sleep(5)
    next_page[0].click()
    rows = driver.find_elements(By.CLASS_NAME, "clickable-aircraft")
  else:
    break

weather_data(date_list)