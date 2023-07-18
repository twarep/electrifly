# the methods in this script transform scraped flight data into required format

# takes a pandas df of the overview data as input, drops unneeded columns
def transform_overview_data(df):
  # strip leading whitespace from columns
  df.columns = df.columns.str.lstrip()
  df = drop_cell_temps(df)
  df = drop_remaining_columns(df)
  # print(df.head())

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