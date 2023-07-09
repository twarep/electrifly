from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import pandas as pd
import zipfile
import os
import time
import psycopg2
import shutil

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
username = os.getenv("username")
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

# Iterate over the rows and extract the data from each column
for row in rows:
    # find all of the table elements in the given row
    cells = row.find_elements(By.TAG_NAME, "td")
    # get the data from each row into a list
    row_data = [cell.text for cell in cells]
    current_flight_id = row_data[0]

    # TODO: break criteria ################ will activate this once database schema is set up
    # query database for this flight ID
    #cur.execute('SELECT flight_id FROM flights WHERE flight_id = %s', (current_flight_id, ))
    #flight_id = cur.fetchone()

    # if the flight id is in the database, stop checking for new data
    #if flight_id is not None:
    #    break
    # otherwise add the flight details to database
    #else:
        # click this row
        # row.click()

    ###########################################
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
      downloaded = False
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
      print(df.head())
      # delete the temp files from disk
      # shutil.rmtree(download_dir)
      break # NOTE: the break should be removed once the database check is uncommented
      
    # Re-locate the row after page refresh
    time.sleep(0.1)
    rows = driver.find_elements(By.CLASS_NAME, "clickable-aircraft")
