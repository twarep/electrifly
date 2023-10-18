import pytest
import pandas as pd
import numpy as np
import transformation
import datetime

def sample_flight_data():
  data = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
          0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
  cols = ["time(ms)", "time(min)", "bat 1 current", "bat 1 voltage", "bat 2 current", 
          "bat 2 voltage", "bat 1 soc", "bat 2 soc", "bat 1 soh", "bat 2 soh", "bat 1 min cell temp", 
          "bat 2 min cell temp", "bat 1 max cell temp", "bat 2 max cell temp", "bat 1 avg cell temp",
          "bat 2 avg cell temp", "bat 1 cell 1 temp", "bat 1 cell 2 temp", "bat 1 cell 3 temp", 
          "bat 1 cell 4 temp", "bat 1 cell 5 temp", "bat 1 cell 6 temp", "bat 1 cell 7 temp", 
          "bat 1 cell 8 temp", "bat 1 cell 9 temp", "bat 1 cell 10 temp", "bat 1 cell 11 temp", 
          "bat 1 cell 12 temp", "bat 1 cell 13 temp", "bat 1 cell 14 temp", "bat 1 cell 15 temp", 
          "bat 1 cell 16 temp", "bat 2 cell 1 temp", "bat 2 cell 2 temp", "bat 2 cell 3 temp", 
          "bat 2 cell 4 temp", "bat 2 cell 5 temp", "bat 2 cell 6 temp", "bat 2 cell 7 temp", 
          "bat 2 cell 8 temp", "bat 2 cell 9 temp", "bat 2 cell 10 temp", "bat 2 cell 11 temp", 
          "bat 2 cell 12 temp", "bat 2 cell 13 temp", "bat 2 cell 14 temp", "bat 2 cell 15 temp",
          "bat 2 cell 16 temp", "bat 1 min cell volt", "bat 2 min cell volt", "bat 1 max cell volt", 
          "bat 2 max cell volt", "inverter operating time", "requested torque", "motor rpm", "motor power", 
          "motor temp", "IAS", "stall_pressure_diff_raw", "stall_warn_active", "stall_calibrated_value", 
          "inverter temp", "bat 1 cooling temp", "inverter cooling temp 1", "inverter cooling temp 2", 
          "remaining flight time", "PRESSURE_ALT", "LAT", "LNG", "GROUND_SPEED", "ACC_LONG", "ACC_LAT", 
          "ACC_NORM", "PITCH", "ROLL", "TIMESTAMP", "HEADING", "STALL_DIFF_PRESSURE", "QNG", "OAT", 
          "ISO leakage current", "ias_derivative", "pitch_derivative", "roll_derivative", "alt_derivative"]
  return pd.DataFrame([data], columns=cols)

def sample_weather_data():
  # get the test csv into a pandas dataframe
  data = ["CYKF", "2023-10-16 00:51", "42.80", "41.00", "93.30", "320.00", "6.00", "0.00", "29.78", "1009.30", 
          "9.00", "M", "BKN", "BKN", "BKN", "OVC", "1800.00", "3000.00", "3500.00", "4400.00", "M", "M", "M", 
          "M", "M", "M", "M", "38.54", "CYKF 160051Z AUTO 32006KT 9SM BKN018 BKN030 BKN035 OVC044 06/05 A2978 RMK SLP093", "M"]
  cols = ["station", "valid", "tmpf", "dwpf", "relh", "drct", "sknt", "p01i", "alti", "mslp", "vsby", "gust",
          "skyc1", "skyc2", "skyc3", "skyc4", "skyl1", "skyl2", "skyl3", "skyl4", "wxcodes", "ice_accretion_1hr",
          "ice_accretion_3hr", "ice_accretion_6hr", "peak_wind_gust", "peak_wind_drct", "peak_wind_time", "feel",
          "metar", "snowdepth"]
  return pd.DataFrame([data], columns=cols)

def test_drop_cell_temps():
  df = sample_flight_data()
  expected_data = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
  expected_cols = ["time(ms)", "time(min)", "bat 1 current", "bat 1 voltage", "bat 2 current", 
                   "bat 2 voltage", "bat 1 soc", "bat 2 soc", "bat 1 soh", "bat 2 soh", "bat 1 min cell temp", 
                   "bat 2 min cell temp", "bat 1 max cell temp", "bat 2 max cell temp", "bat 1 avg cell temp",
                   "bat 2 avg cell temp", "bat 1 min cell volt", "bat 2 min cell volt", "bat 1 max cell volt", 
                   "bat 2 max cell volt", "inverter operating time", "requested torque", "motor rpm", "motor power", 
                   "motor temp", "IAS", "stall_pressure_diff_raw", "stall_warn_active", "stall_calibrated_value", 
                   "inverter temp", "bat 1 cooling temp", "inverter cooling temp 1", "inverter cooling temp 2", 
                   "remaining flight time", "PRESSURE_ALT", "LAT", "LNG", "GROUND_SPEED", "ACC_LONG", "ACC_LAT", 
                   "ACC_NORM", "PITCH", "ROLL", "TIMESTAMP", "HEADING", "STALL_DIFF_PRESSURE", "QNG", "OAT", 
                   "ISO leakage current", "ias_derivative", "pitch_derivative", "roll_derivative", "alt_derivative"]
  expected_df = pd.DataFrame([expected_data], columns=expected_cols)
  actual_df = transformation.drop_cell_temps(df)
  pd.testing.assert_frame_equal(actual_df, expected_df)

def test_drop_remaining_columns():
  df = sample_flight_data()
  expected_data = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
  expected_cols = ["time(min)", "bat 1 current", "bat 1 voltage", "bat 2 current", 
                   "bat 2 voltage", "bat 1 soc", "bat 2 soc", "bat 1 soh", "bat 2 soh", "bat 1 min cell temp", 
                   "bat 2 min cell temp", "bat 1 max cell temp", "bat 2 max cell temp", "bat 1 avg cell temp",
                   "bat 2 avg cell temp", "bat 1 min cell volt", "bat 2 min cell volt", "bat 1 max cell volt", 
                   "bat 2 max cell volt", "requested torque", "motor rpm", "motor power", "motor temp", "IAS", 
                   "stall_warn_active", "inverter temp", "bat 1 cooling temp", "inverter cooling temp 1", 
                   "inverter cooling temp 2", "remaining flight time", "PRESSURE_ALT", "LAT", "LNG", "GROUND_SPEED",
                   "PITCH", "ROLL", "TIMESTAMP", "HEADING", "STALL_DIFF_PRESSURE", "QNG", "OAT", "ISO leakage current"]
  expected_df = pd.DataFrame([expected_data], columns=expected_cols)
  actual_df = transformation.drop_cell_temps(df)
  actual_df = transformation.drop_remaining_columns(actual_df)
  pd.testing.assert_frame_equal(actual_df, expected_df)

def test_drop_weather_columns():
  df = sample_weather_data()
  expected_data = ["2023-10-16 00:51", "42.80", "41.00", "93.30", "320.00", "6.00", "29.78", "1009.30", 
                   "9.00", "M", "BKN", "BKN", "BKN", "OVC", "1800.00", "3000.00", "3500.00", "4400.00", "M", 
                   "CYKF 160051Z AUTO 32006KT 9SM BKN018 BKN030 BKN035 OVC044 06/05 A2978 RMK SLP093"]
  expected_cols = ["valid", "tmpf", "dwpf", "relh", "drct", "sknt", "alti", "mslp", "vsby", "gust",
                   "skyc1", "skyc2", "skyc3", "skyc4", "skyl1", "skyl2", "skyl3", "skyl4", "wxcodes", "metar"]
  expected_df = pd.DataFrame([expected_data], columns=expected_cols)
  actual_df = transformation.drop_weather_columns(df)
  pd.testing.assert_frame_equal(actual_df, expected_df)


def test_weather_datetime_parsing():
  df = sample_weather_data()
  expected_data = [datetime.date(2023, 10, 16), datetime.time(0, 51, 0), "42.80", "41.00", "93.30", "320.00", "6.00", "29.78", "1009.30", 
                   "9.00", "M", "BKN", "BKN", "BKN", "OVC", "1800.00", "3000.00", "3500.00", "4400.00", "M", 
                   "CYKF 160051Z AUTO 32006KT 9SM BKN018 BKN030 BKN035 OVC044 06/05 A2978 RMK SLP093"]
  expected_cols = ["valid", "weather_time_utc", "tmpf", "dwpf", "relh", "drct", "sknt", "alti", "mslp", "vsby", "gust",
                   "skyc1", "skyc2", "skyc3", "skyc4", "skyl1", "skyl2", "skyl3", "skyl4", "wxcodes", "metar"]
  expected_df = pd.DataFrame([expected_data], columns=expected_cols)
  actual_df = transformation.drop_weather_columns(df)
  actual_df = transformation.weather_datetime_parsing(actual_df)
  pd.testing.assert_frame_equal(actual_df, expected_df)


def test_weather_column_names():
  df = sample_weather_data()
  expected_data = [datetime.date(2023, 10, 16), datetime.time(0, 51, 0), "42.80", "41.00", "93.30", "320.00", "6.00", "29.78", "1009.30", 
                   "9.00", "M", "BKN", "BKN", "BKN", "OVC", "1800.00", "3000.00", "3500.00", "4400.00", "M", 
                   "CYKF 160051Z AUTO 32006KT 9SM BKN018 BKN030 BKN035 OVC044 06/05 A2978 RMK SLP093"]
  expected_cols = ["weather_date", "weather_time_utc", "temperature", "dewpoint", "relative_humidity", "wind_direction", "wind_speed",
                   "pressure_altimeter", "sea_level_pressure", "visibility", "wind_gust", "sky_coverage_1", "sky_coverage_2", 
                   "sky_coverage_3", "sky_coverage_4", "sky_level_1", "sky_level_2", "sky_level_3", "sky_level_4", "weather_codes", "metar"]
  expected_df = pd.DataFrame([expected_data], columns=expected_cols)
  actual_df = transformation.drop_weather_columns(df)
  actual_df = transformation.weather_datetime_parsing(actual_df)
  actual_df = transformation.weather_column_names(actual_df)
  pd.testing.assert_frame_equal(actual_df, expected_df)


def test_data_format_cleaning():
  df = sample_weather_data()
  expected_data = [datetime.date(2023, 10, 16), datetime.time(0, 51, 0), "42.80", "41.00", "93.30", 320, 6, "29.78", "1009.30", 
                   "9.00", np.nan, "BKN", "BKN", "BKN", "OVC", 1800, 3000, 3500, 4400, np.nan, 
                   "CYKF 160051Z AUTO 32006KT 9SM BKN018 BKN030 BKN035 OVC044 06/05 A2978 RMK SLP093"]
  expected_cols = ["weather_date", "weather_time_utc", "temperature", "dewpoint", "relative_humidity", "wind_direction", "wind_speed",
                   "pressure_altimeter", "sea_level_pressure", "visibility", "wind_gust", "sky_coverage_1", "sky_coverage_2", 
                   "sky_coverage_3", "sky_coverage_4", "sky_level_1", "sky_level_2", "sky_level_3", "sky_level_4", "weather_codes", "metar"]
  expected_df = pd.DataFrame([expected_data], columns=expected_cols)
  actual_df = transformation.drop_weather_columns(df)
  actual_df = transformation.weather_datetime_parsing(actual_df)
  actual_df = transformation.weather_column_names(actual_df)
  actual_df = transformation.data_format_cleaning(actual_df)
  pd.testing.assert_frame_equal(actual_df, expected_df, check_dtype=False)
