from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import os
import time
import psycopg2

# Load .env file
load_dotenv()

chrome_options = Options()
chrome_options.add_argument("--headless")

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

    # query database for this flight ID
    #cur.execute('SELECT flight_id FROM flights WHERE flight_id = %s', (current_flight_id, ))
    #flight_id = cur.fetchone()

    # if the flight id is in the database, skip it
    #if flight_id is not None:
    #    continue
    # otherwise add the flight details to database
    #else:
        # click this row
        # row.click()
    row.click()

    # get the link to download CSV
    download_csv_link = driver.find_element(By.LINK_TEXT, "Download CSV file")
    time.sleep(4)
    download_csv_link.click()
    break

