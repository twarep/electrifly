from datetime import datetime, timedelta, time
from sys import displayhook
import pandas as pd
from sqlalchemy import create_engine
from weather_forcast_querying import get_forecast_by_current_date
import numpy as np

# How long does 1 single flight take (on average: including time for inspection, flight, charging):
avg_inspection_time_before_flight = 7.41
avg_flight_time = 31.5
avg_charging_time = 58.56
total_flight_time = avg_inspection_time_before_flight + avg_flight_time + avg_charging_time

# Classify the weather data into zones (9 to 10 am -> green zone)
# Need to find a period of time for 30 minutes FOR flight but need 1.5 hours total for everything
    #STRIP INTO TIME INTERVALS

# Getting the dates to be used in the ML UI:
# Get current date
current_date = datetime.now().date()
string_current_date = current_date.strftime("%b %d, %Y")

# Get tomorrow's date
tomorrow_date = current_date + timedelta(days=1)
string_tomorrow_date = tomorrow_date.strftime("%b %d, %Y")

# Get the day after tomorrow's date
day_after_tomorrow_date = current_date + timedelta(days=2)
string_day_after_tomorrow_date = day_after_tomorrow_date.strftime("%b %d, %Y")

# Create a list and add the dates
list_of_dates = [string_current_date, string_tomorrow_date, string_day_after_tomorrow_date]
print(list_of_dates)
