# the methods in this script transform scraped flight and weather data into required format
from datetime import datetime
import numpy as np

# takes a pandas df of the overview data as input, drops unneeded columns
def transform_overview_data(df):
  # strip leading whitespace from columns
  df.columns = df.columns.str.lstrip()
  df = drop_cell_temps(df)
  df = drop_remaining_columns(df)
  return df

# drops the cell temperatures for both batteries
def drop_cell_temps(df):
  # variables for each battery and temp
  batteries = range(1, 3)
  temps = range(1, 17)
  for battery in batteries:
    for temp in temps:
      current_battery_temp = "bat " + str(battery) + " cell " + str(temp) + " temp"
      df = df.drop(current_battery_temp, axis=1)
  return df

# drops the remaining columns (manually)
def drop_remaining_columns(df):
  df = df.drop("time(ms)", axis=1)
  df = df.drop("inverter operating time", axis=1)
  df = df.drop("stall_pressure_diff_raw", axis=1)
  df = df.drop("stall_calibrated_value", axis=1)
  df = df.drop("ACC_LONG", axis=1)
  df = df.drop("ACC_LAT", axis=1)
  df = df.drop("ACC_NORM", axis=1)
  df = df.drop("ias_derivative", axis=1)
  df = df.drop("pitch_derivative", axis=1)
  df = df.drop("roll_derivative", axis=1)
  df = df.drop("alt_derivative", axis=1)
  return df

# takes in weather df, drops the irrelevant weather columns
def drop_weather_columns(df):
  df = df.drop("station", axis=1)
  df = df.drop("p01i", axis=1)
  df = df.drop("feel", axis=1)
  df = df.drop("ice_accretion_1hr", axis=1)
  df = df.drop("ice_accretion_3hr", axis=1)
  df = df.drop("ice_accretion_6hr", axis=1)
  df = df.drop("peak_wind_gust", axis=1)
  df = df.drop("peak_wind_drct", axis=1)
  df = df.drop("peak_wind_time", axis=1)
  df = df.drop("snowdepth", axis=1)
  return df

# takes in weather df, converts timestamp into date and time
def weather_datetime_parsing(df):
  # get the timestamps into a list
  timestamp_list = df['valid'].tolist()
  # create lists for new, separated date and time
  weather_date = []
  weather_time_utc = []
  # for each timestamp, separate date and time, push to new list
  for timestamp in timestamp_list:
    datetime_obj = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
    weather_date.append(datetime_obj.date())
    weather_time_utc.append(datetime_obj.time())
  # replace the valid column with the weather date
  df["valid"] = weather_date
  # make a new column after with the weather time in UTC
  df.insert(1, "weather_time_utc", weather_time_utc)
  return df

# takes in weather df, changes column names to those in DB schema
def weather_column_names(df):
  new_columns = ["weather_date", "weather_time_utc", "temperature", "dewpoint",
                 "relative_humidity", "wind_direction", "wind_speed",
                 "pressure_altimeter", "sea_level_pressure", "visibility",
                 "wind_gust", "sky_coverage_1", "sky_coverage_2", "sky_coverage_3",
                 "sky_coverage_4", "sky_level_1", "sky_level_2", "sky_level_3",
                 "sky_level_4", "weather_codes", "metar"]
  # replace the initial column names in the df
  df = df.set_axis(new_columns, axis="columns")
  return df

# cleans data to be ingestible to db
def data_format_cleaning(df):
  # replace "M" values with null
  df.replace("M", np.nan, inplace=True)
  # convert smallint columns to int
  df['wind_direction'] = df['wind_direction'].astype(float).round().astype(int, errors="ignore")
  df['wind_speed'] = df['wind_speed'].astype(float).round().astype(int, errors="ignore")
  df['wind_gust'] = df['wind_gust'].astype(float).round().astype(int, errors="ignore")
  df['sky_level_1'] = df['sky_level_1'].astype(float).round().astype(int, errors="ignore")
  df['sky_level_2'] = df['sky_level_2'].astype(float).round().astype(int, errors="ignore")
  df['sky_level_3'] = df['sky_level_3'].astype(float).round().astype(int, errors="ignore")
  df['sky_level_4'] = df['sky_level_4'].astype(float).round().astype(int, errors="ignore")
  return df

# combine the transformation functions into one
def weather_transformation(df):
  df = drop_weather_columns(df)
  df = weather_datetime_parsing(df)
  df = weather_column_names(df)
  df = data_format_cleaning(df)
  
  return df
