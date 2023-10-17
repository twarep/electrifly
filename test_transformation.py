import pytest
import pandas as pd
from transformation import drop_cell_temps, drop_remaining_columns

# get the test csv into a pandas dataframe
def sample_flight_data():
  data = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
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
  actual_df = drop_cell_temps(df)
  assert actual_df.equals(expected_df)

def test_drop_remaining_columns():
  df = sample_flight_data()
  expected_data = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
  expected_cols = ["time(min)", "bat 1 current", "bat 1 voltage", "bat 2 current", 
                   "bat 2 voltage", "bat 1 soc", "bat 2 soc", "bat 1 soh", "bat 2 soh", "bat 1 min cell temp", 
                   "bat 2 min cell temp", "bat 1 max cell temp", "bat 2 max cell temp", "bat 1 avg cell temp",
                   "bat 2 avg cell temp", "bat 1 min cell volt", "bat 2 min cell volt", "bat 1 max cell volt", 
                   "bat 2 max cell volt", "requested torque", "motor rpm", "motor power", 
                   "motor temp", "IAS", "stall_warn_active",
                   "inverter temp", "bat 1 cooling temp", "inverter cooling temp 1", "inverter cooling temp 2", 
                   "remaining flight time", "PRESSURE_ALT", "LAT", "LNG", "GROUND_SPEED", "PITCH", "ROLL", "TIMESTAMP", "HEADING", "STALL_DIFF_PRESSURE", "QNG", "OAT", 
                   "ISO leakage current"]
  expected_df = pd.DataFrame([expected_data], columns=expected_cols)
  actual_df = drop_cell_temps(df)
  actual_df = drop_remaining_columns(actual_df)
  assert actual_df.equals(expected_df)