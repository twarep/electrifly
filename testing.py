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

# pull in forecasted weather data (right now it's hardcoded)
forecast_df = get_forecast_by_current_date()
forecast_date = forecast_df["Forecast Date"]
forecast_time_et = forecast_df["Forecast Time"]
# print(forecast_date)
print(forecast_time_et)
print(type(forecast_time_et))


# Convert each time object to string and remove seconds
formatted_time_series = forecast_time_et.apply(lambda x: x.strftime('%H:%M'))

# Print the formatted time series
print(formatted_time_series)
