# file with database queries

## Create Flights Table
CREATE_FLIGHTS = """
CREATE TABLE flights (
  id INTEGER PRIMARY KEY, 
  flight_date DATE NOT NULL, 
  flight_time_utc TIME NOT NULL,
  flight_notes VARCHAR(1000),
  flight_type VARCHAR(100),
  total_weight REAL
);
"""

# Create Weather Table
CREATE_WEATHER = """
CREATE TABLE weather (
  id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  weather_date DATE NOT NULL,
  weather_time_utc TIME NOT NULL,
  temperature REAL NOT NULL,
  dewpoint REAL NOT NULL,
  relative_humidity REAL NOT NULL,
  wind_direction SMALLINT,
  wind_speed SMALLINT NOT NULL,
  pressure_altimeter REAL NOT NULL,
  sea_level_pressure REAL NOT NULL,
  visibility REAL NOT NULL,
  wind_gust SMALLINT,
  sky_coverage_1 VARCHAR(3),
  sky_coverage_2 VARCHAR(3),
  sky_coverage_3 VARCHAR(3),
  sky_coverage_4 VARCHAR(3),
  sky_level_1 SMALLINT,
  sky_level_2 SMALLINT,
  sky_level_3 SMALLINT,
  sky_level_4 SMALLINT,
  weather_codes VARCHAR(12),
  metar VARCHAR(200)
);
"""

# Create intermediate flight and weather table
# Purpose: be able to link weather data to the correct flight
CREATE_FLIGHT_WEATHER = """
CREATE TABLE flight_weather (
  flight_id INTEGER REFERENCES flights(id),
  weather_id INTEGER REFERENCES weather(id)
);
"""

CREATE_FLIGHT_WEATHER_VIEW = """
CREATE OR REPLACE FUNCTION get_flight_data(id integer)
RETURNS TABLE (
    -- Replace the column names and data types with the appropriate ones from flightdata tables
	flight_id int8,
	time_min float8,
	bat_1_current float8,
	bat_1_voltage float8,
	bat_2_current float8,
	bat_2_voltage float8,
	bat_1_soc float8,
	bat_2_soc float8,
	bat_1_soh float8,
	bat_2_soh float8,
	bat_1_min_cell_temp float8,
	bat_2_min_cell_temp float8,
	bat_1_max_cell_temp float8,
	bat_2_max_cell_temp float8,
	bat_1_avg_cell_temp float8 ,
	bat_2_avg_cell_temp float8 ,
	bat_1_min_cell_volt float8 ,
	bat_2_min_cell_volt float8 ,
	bat_1_max_cell_volt float8 ,
	bat_2_max_cell_volt float8 ,
	requested_torque float8 ,
	motor_rpm float8 ,
	motor_power float8 ,
	motor_temp float8 ,
	ias float8 ,
	stall_warn_active float8 ,
	inverter_temp float8 ,
	bat_1_cooling_temp float8 ,
	inverter_cooling_temp_1 float8 ,
	inverter_cooling_temp_2 float8 ,
	remaining_flight_time float8 ,
	pressure_alt float8 ,
	lat float8 ,
	lng float8 ,
	ground_speed float8 ,
	pitch float8 ,
	roll float8 ,
	"time_stamp" float8 ,
	heading float8 ,
	stall_diff_pressure float8 ,
	qng float8 ,
	oat float8 ,
	iso_leakage_current float8 
)
AS
$$
BEGIN
    RETURN QUERY EXECUTE format('SELECT * FROM flightdata_%s WHERE flight_id = %s',id, id);
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE VIEW flight_weather_data_view AS
SELECT
    fw.flight_id AS fw_flight_id,
    ff.flight_date,
    ff.flight_time_utc,
    fd.*,
    w.*
FROM flight_weather fw
JOIN flights ff ON fw.flight_id = ff.id
JOIN weather w ON fw.weather_id = w.id
JOIN LATERAL get_flight_data(fw.flight_id) fd ON true;
"""

CREATE_FORECAST = """
CREATE TABLE forecast (
  id INTEGER PRIMARY KEY, 
  forecast_date DATE NOT NULL, 
  forecast_time_et TIME NOT NULL,
  temperature_2m REAL NOT NULL,
  weathercode SMALLINT NOT NULL,
  windgusts_10m REAL NOT NULL,
  visibility REAL NOT NULL,
  lightning_potential REAL NOT NULL,
  winddirection_10m SMALLINT NOT NULL,
  sunrise_time TIME NOT NULL,
  sunset_time TIME NOT NULL,
);
"""

CREATE_FLIGHT_ACTIVITIES = """
CREATE TABLE flight_activities AS
SELECT flight_id, time_min FROM flightdata_4620
union ALL
SELECT flight_id, time_min FROM flightdata_4940
union ALL
SELECT flight_id, time_min FROM flightdata_4929
union ALL
SELECT flight_id, time_min FROM flightdata_5019
union ALL
SELECT flight_id, time_min FROM flightdata_5021
union ALL
SELECT flight_id, time_min FROM flightdata_5034
union ALL
SELECT flight_id, time_min FROM flightdata_4636
union ALL
SELECT flight_id, time_min FROM flightdata_4842
union ALL
SELECT flight_id, time_min FROM flightdata_4868
union ALL
SELECT flight_id, time_min FROM flightdata_4925
union ALL
SELECT flight_id, time_min FROM flightdata_4978
union ALL
SELECT flight_id, time_min FROM flightdata_5116
union ALL
SELECT flight_id, time_min FROM flightdata_5362;
"""

ADD_ACTIVITY_COLUMN = """
ALTER TABLE flight_activities
ADD COLUMN activity VARCHAR(255) DEFAULT 'NA';
"""

LABEL_4620 = """
UPDATE flight_activities
SET activity = CASE
    WHEN flight_id = 4620 AND time_min < 13.5 THEN 'pre-flight'
    WHEN flight_id = 4620 AND (time_min BETWEEN 13.5 AND 14.5) THEN 'takeoff'
    WHEN flight_id = 4620 AND (time_min BETWEEN 14.6 AND 15.5) THEN 'climb'
    WHEN flight_id = 4620 AND (time_min BETWEEN 15.6 AND 16.9) THEN 'cruise'
    WHEN flight_id = 4620 AND (time_min BETWEEN 17 AND 18.2) THEN 'landing'
    WHEN flight_id = 4620 AND (time_min BETWEEN 18.3 AND 19) THEN 'takeoff'
    WHEN flight_id = 4620 AND (time_min BETWEEN 19.1 AND 20.1) THEN 'climb'
    WHEN flight_id = 4620 AND (time_min BETWEEN 20.2 AND 22.1) THEN 'cruise'
    WHEN flight_id = 4620 AND (time_min BETWEEN 22.2 AND 23.6) THEN 'landing'
    WHEN flight_id = 4620 AND (time_min BETWEEN 23.7 AND 24.6) THEN 'takeoff'
    WHEN flight_id = 4620 AND (time_min BETWEEN 24.7 AND 25.36) THEN 'climb'
    WHEN flight_id = 4620 AND (time_min BETWEEN 25.4 AND 27.8) THEN 'cruise'
    WHEN flight_id = 4620 AND (time_min BETWEEN 27.9 AND 29.6) THEN 'landing'
    WHEN flight_id = 4620 AND (time_min BETWEEN 29.7 AND 30.7) THEN 'takeoff'
    WHEN flight_id = 4620 AND (time_min BETWEEN 30.8 AND 31.4) THEN 'climb'
    WHEN flight_id = 4620 AND (time_min BETWEEN 31.5 AND 33) THEN 'cruise'
    WHEN flight_id = 4620 AND (time_min BETWEEN 33 AND 34) THEN 'descent'
    WHEN flight_id = 4620 AND (time_min BETWEEN 34 AND 35.5) THEN 'landing'
    WHEN flight_id = 4620 AND (time_min BETWEEN 35.6 AND 36.5) THEN 'takeoff'
    WHEN flight_id = 4620 AND (time_min BETWEEN 36.6 AND 37.4) THEN 'climb'
    WHEN flight_id = 4620 AND (time_min BETWEEN 37.5 AND 38.9) THEN 'cruise'
    WHEN flight_id = 4620 AND (time_min BETWEEN 39 AND 39.8) THEN 'descent'
    WHEN flight_id = 4620 AND (time_min BETWEEN 39.8 AND 40.8) THEN 'landing'
    WHEN flight_id = 4620 AND (time_min BETWEEN 40.9 AND 42) THEN 'takeoff'
    WHEN flight_id = 4620 AND (time_min BETWEEN 42.1 AND 42.9) THEN 'climb'
    WHEN flight_id = 4620 AND (time_min BETWEEN 43 AND 45.2) THEN 'cruise'
    WHEN flight_id = 4620 AND (time_min BETWEEN 45.3 AND 46.4) THEN 'descent'
    WHEN flight_id = 4620 AND (time_min BETWEEN 46.5 AND 48) THEN 'landing'
    WHEN flight_id = 4620 AND time_min > 48 THEN 'post-flight'
    ELSE activity  -- Keep the existing value for other rows
END
WHERE flight_id = 4620;
"""

LABEL_4929 = """
UPDATE flight_activities
SET activity = CASE
    WHEN flight_id = 4929 AND time_min < 7.65 THEN 'pre-flight'
    WHEN flight_id = 4929 AND (time_min BETWEEN 7.65 AND 8.5) THEN 'takeoff'
    WHEN flight_id = 4929 AND (time_min BETWEEN 8.6 AND 10.9) THEN 'climb'
    WHEN flight_id = 4929 AND (time_min BETWEEN 11 AND 28.8) THEN 'cruise'
    WHEN flight_id = 4929 AND (time_min BETWEEN 28.9 AND 30.4) THEN 'descent'
    WHEN flight_id = 4929 AND (time_min BETWEEN 30.5 AND 35) THEN 'landing'
    WHEN flight_id = 4929 AND time_min > 35 THEN 'post-flight'
    ELSE activity  -- Keep the existing value for other rows
END
WHERE flight_id = 4929;
"""

LABEL_4940 = """
UPDATE flight_activities
SET activity = CASE
    WHEN flight_id = '4940' AND time_min < 9.9 THEN 'pre-flight'
    WHEN flight_id = '4940' AND (time_min BETWEEN 9.9 AND 11) THEN 'takeoff'
    WHEN flight_id = '4940' AND (time_min BETWEEN 11.1 AND 16) THEN 'climb'
    WHEN flight_id = '4940' AND (time_min BETWEEN 16.1 AND 18.7) THEN 'cruise'
    WHEN flight_id = '4940' AND (time_min BETWEEN 18.8 AND 19.3) THEN 'power off stall'
    WHEN flight_id = '4940' AND (time_min BETWEEN 19.4 AND 20.4) THEN 'cruise'
    WHEN flight_id = '4940' AND (time_min BETWEEN 20.5 AND 21.9) THEN 'steep turns'
    WHEN flight_id = '4940' AND (time_min BETWEEN 22 AND 25.7) THEN 'cruise'
    WHEN flight_id = '4940' AND (time_min BETWEEN 25.8 AND 29) THEN 'steep turns'
    WHEN flight_id = '4940' AND (time_min BETWEEN 29.1 AND 31.7) THEN 'cruise'
    WHEN flight_id = '4940' AND (time_min BETWEEN 31.8 AND 33) THEN 'descent'
    WHEN flight_id = '4940' AND (time_min BETWEEN 33.1 AND 35.9) THEN 'cruise'
    WHEN flight_id = '4940' AND (time_min BETWEEN 36 AND 38.4) THEN 'descent'
    WHEN flight_id = '4940' AND (time_min BETWEEN 38.5 AND 40.7) THEN 'landing'
    WHEN flight_id = '4940' AND time_min > 40.7 THEN 'post-flight'
    ELSE activity  -- Keep the existing value for other rows
END
WHERE flight_id = '4940';
"""

LABEL_5019 = """
UPDATE flight_activities
SET activity = CASE
    WHEN flight_id = '5019' AND time_min < 7.2 THEN 'pre-flight'
    WHEN flight_id = '5019' AND (time_min BETWEEN 7.2 AND 8) THEN 'takeoff'
    WHEN flight_id = '5019' AND (time_min BETWEEN 8.1 AND 10.5) THEN 'climb'
    WHEN flight_id = '5019' AND (time_min BETWEEN 10.6 AND 16.1) THEN 'cruise'
    WHEN flight_id = '5019' AND (time_min BETWEEN 16.2 AND 19) THEN 'climb'
    WHEN flight_id = '5019' AND (time_min BETWEEN 19.1 AND 20.9) THEN 'descent'
    WHEN flight_id = '5019' AND (time_min BETWEEN 21 AND 21.55) THEN 'climb'
    WHEN flight_id = '5019' AND (time_min BETWEEN 21.6 AND 22.4) THEN 'descent'
    WHEN flight_id = '5019' AND (time_min BETWEEN 22.5 AND 25) THEN 'steep turns'
    WHEN flight_id = '5019' AND (time_min BETWEEN 25.1 AND 26) THEN 'climb'
    WHEN flight_id = '5019' AND (time_min BETWEEN 26.1 AND 27.4) THEN 'descent'
    WHEN flight_id = '5019' AND (time_min BETWEEN 27.5 AND 28.2) THEN 'steep turns'
    WHEN flight_id = '5019' AND (time_min BETWEEN 28.3 AND 30.7) THEN 'cruise'
    WHEN flight_id = '5019' AND (time_min BETWEEN 30.8 AND 34.9) THEN 'descent'
    WHEN flight_id = '5019' AND (time_min BETWEEN 35 AND 36.4) THEN 'landing'
    WHEN flight_id = '5019' AND (time_min BETWEEN 36.5 AND 37.2) THEN 'takeoff'
    WHEN flight_id = '5019' AND (time_min BETWEEN 37.3 AND 38) THEN 'climb'
    WHEN flight_id = '5019' AND (time_min BETWEEN 38.1 AND 38.8) THEN 'cruise'
    WHEN flight_id = '5019' AND (time_min BETWEEN 38.9 AND 40.3) THEN 'landing'
    WHEN flight_id = '5019' AND (time_min BETWEEN 40.4 AND 41.1) THEN 'takeoff'
    WHEN flight_id = '5019' AND (time_min BETWEEN 41.1 AND 42.2) THEN 'climb'
    WHEN flight_id = '5019' AND (time_min BETWEEN 42.3 AND 45) THEN 'landing'
    WHEN flight_id = '5019' AND time_min > 45 THEN 'post-flight'
    ELSE activity  -- Keep the existing value for other rows
END
WHERE flight_id = '5019';
"""

LABEL_5021 = """
UPDATE flight_activities
SET activity = CASE
    WHEN flight_id = '5021' AND time_min < 10.2 THEN 'pre-flight'
    WHEN flight_id = '5021' AND (time_min BETWEEN 10.2 AND 11.1) THEN 'takeoff'
    WHEN flight_id = '5021' AND (time_min BETWEEN 11.2 AND 13.5) THEN 'climb'
    WHEN flight_id = '5021' AND (time_min BETWEEN 13.6 AND 20.9) THEN 'cruise'
    WHEN flight_id = '5021' AND (time_min BETWEEN 21 AND 25.1) THEN 'slow flight'
    WHEN flight_id = '5021' AND (time_min BETWEEN 25.2 AND 26) THEN 'descent'
    WHEN flight_id = '5021' AND (time_min BETWEEN 26.1 AND 29.5) THEN 'slow flight'
    WHEN flight_id = '5021' AND (time_min BETWEEN 29.6 AND 30.7) THEN 'climb'
    WHEN flight_id = '5021' AND (time_min BETWEEN 30.8 AND 31.1) THEN 'power off stall'
    WHEN flight_id = '5021' AND (time_min BETWEEN 31.5 AND 32) THEN 'power on stall'
    WHEN flight_id = '5021' AND (time_min BETWEEN 32.1 AND 33.9) THEN 'cruise'
    WHEN flight_id = '5021' AND (time_min BETWEEN 34 AND 36) THEN 'steep turns'
    WHEN flight_id = '5021' AND (time_min BETWEEN 36.1 AND 39.1) THEN 'cruise'
    WHEN flight_id = '5021' AND (time_min BETWEEN 39.2 AND 42) THEN 'descent'
    WHEN flight_id = '5021' AND (time_min BETWEEN 42.1 AND 47.2) THEN 'landing'
    WHEN flight_id = '5021' AND time_min > 47.2 THEN 'post-flight'
    ELSE activity  -- Keep the existing value for other rows
END
WHERE flight_id = '5021';
"""

LABEL_5034 = """
UPDATE flight_activities
SET activity = CASE
    WHEN flight_id = '5034' AND time_min < 17.9 THEN 'pre-flight'
    WHEN flight_id = '5034' AND (time_min BETWEEN 17.9 AND 19) THEN 'takeoff'
    WHEN flight_id = '5034' AND (time_min BETWEEN 19.1 AND 21.5) THEN 'climb'
    WHEN flight_id = '5034' AND (time_min BETWEEN 21.6 AND 26.2) THEN 'cruise'
    WHEN flight_id = '5034' AND (time_min BETWEEN 27.3 AND 27.75) THEN 'power off stall'
    WHEN flight_id = '5034' AND (time_min BETWEEN 28.15 AND 28.5) THEN 'power off stall'
    WHEN flight_id = '5034' AND (time_min BETWEEN 29 AND 30.3) THEN 'climb'
    WHEN flight_id = '5034' AND (time_min BETWEEN 30.4 AND 30.7) THEN 'power on stall'
    WHEN flight_id = '5034' AND (time_min BETWEEN 30.9 AND 31.2) THEN 'power on stall'
    WHEN flight_id = '5034' AND (time_min BETWEEN 31.6 AND 32.9) THEN 'power off stall'
    WHEN flight_id = '5034' AND (time_min BETWEEN 33 AND 34.1) THEN 'climb'
    WHEN flight_id = '5034' AND (time_min BETWEEN 34.2 AND 35.1) THEN 'steep turns'
    WHEN flight_id = '5034' AND (time_min BETWEEN 35.2 AND 38.4) THEN 'cruise'
    WHEN flight_id = '5034' AND (time_min BETWEEN 38.5 AND 41.9) THEN 'descent'
    WHEN flight_id = '5034' AND (time_min BETWEEN 42 AND 43.2) THEN 'landing'
    WHEN flight_id = '5034' AND (time_min BETWEEN 43.3 AND 44) THEN 'takeoff'
    WHEN flight_id = '5034' AND (time_min BETWEEN 44.1 AND 44.9) THEN 'climb'
    WHEN flight_id = '5034' AND (time_min BETWEEN 45 AND 46.2) THEN 'cruise'
    WHEN flight_id = '5034' AND (time_min BETWEEN 46.3 AND 50) THEN 'landing'
    WHEN flight_id = '5034' AND time_min > 50 THEN 'post-flight'
    ELSE activity  -- Keep the existing value for other rows
END
WHERE flight_id = '5034';
"""

LABEL_4636 = """
UPDATE flight_activities
SET activity = CASE
    WHEN flight_id = '4636' AND time_min < 13.8 THEN 'pre-flight'
    WHEN flight_id = '4636' AND (time_min BETWEEN 13.8 AND 14.44) THEN 'takeoff'
    WHEN flight_id = '4636' AND (time_min BETWEEN 14.45 AND 15.36) THEN 'climb'
    WHEN flight_id = '4636' AND (time_min BETWEEN 15.37 AND 17.25) THEN 'cruise'
    WHEN flight_id = '4636' AND (time_min BETWEEN 17.26 AND 19.08) THEN 'landing'
    WHEN flight_id = '4636' AND (time_min BETWEEN 19.09 AND 19.74) THEN 'takeoff'
    WHEN flight_id = '4636' AND (time_min BETWEEN 19.75 AND 20.4) THEN 'climb'
    WHEN flight_id = '4636' AND (time_min BETWEEN 20.41 AND 22.23) THEN 'cruise'
    WHEN flight_id = '4636' AND (time_min BETWEEN 22.24 AND 24.75) THEN 'landing'
    WHEN flight_id = '4636' AND (time_min BETWEEN 24.76 AND 25.46) THEN 'takeoff'
    WHEN flight_id = '4636' AND (time_min BETWEEN 25.47 AND 26.7) THEN 'climb'
    WHEN flight_id = '4636' AND (time_min BETWEEN 26.71 AND 27.82) THEN 'cruise'
    WHEN flight_id = '4636' AND (time_min BETWEEN 27.83 AND 30.22) THEN 'landing'
    WHEN flight_id = '4636' AND (time_min BETWEEN 30.24 AND 31.08) THEN 'takeoff'
    WHEN flight_id = '4636' AND (time_min BETWEEN 31.09 AND 31.98) THEN 'climb'
    WHEN flight_id = '4636' AND (time_min BETWEEN 31.99 AND 32.94) THEN 'cruise'
    WHEN flight_id = '4636' AND (time_min BETWEEN 32.95 AND 35.28) THEN 'landing'
    WHEN flight_id = '4636' AND (time_min BETWEEN 35.29 AND 36.2) THEN 'takeoff'
    WHEN flight_id = '4636' AND (time_min BETWEEN 36.21 AND 37.28) THEN 'climb'
    WHEN flight_id = '4636' AND (time_min BETWEEN 37.29 AND 38.54) THEN 'cruise'
    WHEN flight_id = '4636' AND (time_min BETWEEN 38.55 AND 40.98) THEN 'landing'
    WHEN flight_id = '4636' AND (time_min BETWEEN 40.99 AND 41.66) THEN 'takeoff'
    WHEN flight_id = '4636' AND (time_min BETWEEN 41.67 AND 42.78) THEN 'climb'
    WHEN flight_id = '4636' AND (time_min BETWEEN 42.79 AND 43.98) THEN 'cruise'
    WHEN flight_id = '4636' AND (time_min BETWEEN 43.99 AND 46.16) THEN 'landing'
    WHEN flight_id = '4636' AND (time_min BETWEEN 46.17 AND 46.92) THEN 'takeoff'
    WHEN flight_id = '4636' AND (time_min BETWEEN 46.93 AND 47.94) THEN 'climb'
    WHEN flight_id = '4636' AND (time_min BETWEEN 47.95 AND 49.62) THEN 'cruise'
    WHEN flight_id = '4636' AND (time_min BETWEEN 49.63 AND 52.44) THEN 'landing'
    WHEN flight_id = '4636' AND time_min >= 52.45 THEN 'post-flight'
    ELSE activity  -- Keep the existing value for other rows
END
WHERE flight_id = '4636';
"""

LABEL_4842 = """
UPDATE flight_activities
SET activity = CASE
    WHEN flight_id = '4842' AND  time_min < 14.06 THEN 'pre-flight'
    WHEN flight_id = '4842' AND (time_min BETWEEN 14.06 AND 14.90) THEN 'takeoff'
    WHEN flight_id = '4842' AND (time_min BETWEEN 14.90 AND 16.04) THEN 'climb'
    WHEN flight_id = '4842' AND (time_min BETWEEN 16.04 AND 17.21) THEN 'cruise'
    WHEN flight_id = '4842' AND (time_min BETWEEN 17.22 AND 18.96) THEN 'landing'
    WHEN flight_id = '4842' AND (time_min BETWEEN 19.02 AND 19.78) THEN 'takeoff'
    WHEN flight_id = '4842' AND (time_min BETWEEN 19.78 AND 21.54) THEN 'climb'
    WHEN flight_id = '4842' AND (time_min BETWEEN 21.54 AND 22.24) THEN 'cruise'
    WHEN flight_id = '4842' AND (time_min BETWEEN 22.24 AND 22.28) THEN 'landing'
    WHEN flight_id = '4842' AND (time_min BETWEEN 22.40 AND 24.58) THEN 'landing'
    WHEN flight_id = '4842' AND (time_min BETWEEN 24.58 AND 25.62) THEN 'takeoff'
    WHEN flight_id = '4842' AND (time_min BETWEEN 25.62 AND 26.84) THEN 'climb'
    WHEN flight_id = '4842' AND (time_min BETWEEN 26.84 AND 28.28) THEN 'cruise'
    WHEN flight_id = '4842' AND (time_min BETWEEN 28.28 AND 30.36) THEN 'landing'
    WHEN flight_id = '4842' AND (time_min BETWEEN 30.36 AND 31.18) THEN 'takeoff'
    WHEN flight_id = '4842' AND (time_min BETWEEN 31.18 AND 31.34) THEN 'climb'
    WHEN flight_id = '4842' AND (time_min BETWEEN 31.34 AND 31.46) THEN 'takeoff'
    WHEN flight_id = '4842' AND (time_min BETWEEN 31.46 AND 32.58) THEN 'climb'
    WHEN flight_id = '4842' AND (time_min BETWEEN 32.58 AND 34.44) THEN 'cruise'
    WHEN flight_id = '4842' AND (time_min BETWEEN 34.44 AND 37.14) THEN 'landing'
    WHEN flight_id = '4842' AND (time_min BETWEEN 37.14 AND 38.02) THEN 'takeoff'
    WHEN flight_id = '4842' AND (time_min BETWEEN 38.02 AND 39.26) THEN 'climb'
    WHEN flight_id = '4842' AND (time_min BETWEEN 39.26 AND 40.36) THEN 'cruise'
    WHEN flight_id = '4842' AND (time_min BETWEEN 40.36 AND 42.82) THEN 'landing'
    WHEN flight_id = '4842' AND (time_min BETWEEN 42.82 AND 43.84) THEN 'takeoff'
    WHEN flight_id = '4842' AND (time_min BETWEEN 43.84 AND 44.90) THEN 'climb'
    WHEN flight_id = '4842' AND (time_min BETWEEN 44.90 AND 45.84) THEN 'cruise'
    WHEN flight_id = '4842' AND (time_min BETWEEN 45.84 AND 45.88) THEN 'descent'
    WHEN flight_id = '4842' AND (time_min BETWEEN 45.88 AND 49.68) THEN 'landing'
    WHEN flight_id = '4842' AND  time_min >49.68 THEN 'post-flight'
    ELSE activity  -- Keep the existing value for other rows
END
WHERE flight_id = '4842';
"""
LABEL_4868 = """
UPDATE flight_activities
SET activity = CASE
    WHEN flight_id = '4868' AND (time_min < 11.12) THEN 'pre-flight'
    WHEN flight_id = '4868' AND (time_min BETWEEN 11.12 AND 12.04) THEN 'takeoff'
    WHEN flight_id = '4868' AND (time_min BETWEEN 12.06 AND 14.94) THEN 'climb'
    WHEN flight_id = '4868' AND (time_min BETWEEN 14.96 AND 20.62) THEN 'cruise'
    WHEN flight_id = '4868' AND (time_min BETWEEN 20.64 AND 21.82) THEN 'slow flight'
    WHEN flight_id = '4868' AND (time_min BETWEEN 21.84 AND 22.24) THEN 'power off stall'
    WHEN flight_id = '4868' AND (time_min BETWEEN 22.32 AND 22.62) THEN 'climb'
    WHEN flight_id = '4868' AND (time_min BETWEEN 22.64 AND 24.4) THEN 'cruise'
    WHEN flight_id = '4868' AND (time_min BETWEEN 24.5 AND 25) THEN 'steep turns'
    WHEN flight_id = '4868' AND (time_min BETWEEN 25.1 AND 31.30) THEN 'cruise'
    WHEN flight_id = '4868' AND (time_min BETWEEN 31.32 AND 34.30) THEN 'landing'
    WHEN flight_id = '4868' AND (time_min BETWEEN 34.32 AND 35.32) THEN 'takeoff'
    WHEN flight_id = '4868' AND (time_min BETWEEN 35.34 AND 36.42) THEN 'climb'
    WHEN flight_id = '4868' AND (time_min BETWEEN 36.44 AND 37.96) THEN 'cruise'
    WHEN flight_id = '4868' AND (time_min BETWEEN 37.98 AND 38.00) THEN 'descent'
    WHEN flight_id = '4868' AND (time_min BETWEEN 38.02 AND 40.54) THEN 'landing'
    WHEN flight_id = '4868' AND (time_min BETWEEN 40.54 AND 56.00) THEN 'post-flight'
    ELSE activity  -- Keep the existing value for other rows
END
WHERE flight_id = '4868';

"""

LABEL_4925 = """
UPDATE flight_activities
SET activity = CASE
    WHEN flight_id = '4925' AND (time_min < 9.82) THEN 'pre-flight'
    WHEN flight_id = '4925' AND (time_min BETWEEN 9.82 AND 10.78) THEN 'takeoff'
    WHEN flight_id = '4925' AND (time_min BETWEEN 10.79 AND 11.75) THEN 'climb'
    WHEN flight_id = '4925' AND (time_min BETWEEN 11.76 AND 12.82) THEN 'cruise'
    WHEN flight_id = '4925' AND (time_min BETWEEN 12.83 AND 15.40) THEN 'landing'
    WHEN flight_id = '4925' AND (time_min BETWEEN 15.41 AND 16.07) THEN 'takeoff'
    WHEN flight_id = '4925' AND (time_min BETWEEN 16.08 AND 16.97) THEN 'climb'
    WHEN flight_id = '4925' AND (time_min BETWEEN 16.98 AND 18.04) THEN 'cruise'
    WHEN flight_id = '4925' AND (time_min BETWEEN 18.05 AND 20.20) THEN 'landing'
    WHEN flight_id = '4925' AND (time_min BETWEEN 20.21 AND 20.88) THEN 'takeoff'
    WHEN flight_id = '4925' AND (time_min BETWEEN 20.89 AND 21.82) THEN 'climb'
    WHEN flight_id = '4925' AND (time_min BETWEEN 21.83 AND 23.12) THEN 'cruise'
    WHEN flight_id = '4925' AND (time_min BETWEEN 23.13 AND 25.07) THEN 'landing'
    WHEN flight_id = '4925' AND (time_min BETWEEN 25.08 AND 25.76) THEN 'takeoff'
    WHEN flight_id = '4925' AND (time_min BETWEEN 25.77 AND 26.54) THEN 'climb'
    WHEN flight_id = '4925' AND (time_min BETWEEN 26.55 AND 27.56) THEN 'cruise'
    WHEN flight_id = '4925' AND (time_min BETWEEN 27.58 AND 29.74) THEN 'landing'
    WHEN flight_id = '4925' AND (time_min BETWEEN 29.75 AND 30.46) THEN 'takeoff'
    WHEN flight_id = '4925' AND (time_min BETWEEN 30.48 AND 31.21) THEN 'climb'
    WHEN flight_id = '4925' AND (time_min BETWEEN 31.22 AND 31.94) THEN 'cruise'
    WHEN flight_id = '4925' AND (time_min BETWEEN 31.95 AND 34.36) THEN 'landing'
    WHEN flight_id = '4925' AND (time_min BETWEEN 34.37 AND 35.12) THEN 'takeoff'
    WHEN flight_id = '4925' AND (time_min BETWEEN 35.13 AND 35.90) THEN 'climb'
    WHEN flight_id = '4925' AND (time_min BETWEEN 35.91 AND 36.80) THEN 'cruise'
    WHEN flight_id = '4925' AND (time_min BETWEEN 36.81 AND 36.98) THEN 'descent'
    WHEN flight_id = '4925' AND (time_min BETWEEN 36.99 AND 39.04) THEN 'landing'
    WHEN flight_id = '4925' AND (time_min BETWEEN 39.05 AND 39.74) THEN 'takeoff'
    WHEN flight_id = '4925' AND (time_min BETWEEN 39.75 AND 40.49) THEN 'climb'
    WHEN flight_id = '4925' AND (time_min BETWEEN 40.50 AND 41.34) THEN 'cruise'
    WHEN flight_id = '4925' AND (time_min BETWEEN 41.35 AND 41.62) THEN 'descent'
    WHEN flight_id = '4925' AND (time_min BETWEEN 41.63 AND 43.90) THEN 'landing'
    WHEN flight_id = '4925' AND (time_min > 43.91) THEN 'post-flight'
    ELSE activity  -- Keep the existing value for other rows
END
WHERE flight_id = '4925';

"""

LABEL_4978 = """
UPDATE flight_activities
SET activity = CASE
    WHEN flight_id = '4978' AND (time_min < 15.1 ) THEN 'pre-flight'
    WHEN flight_id = '4978' AND (time_min BETWEEN 15.2 AND 18) THEN 'takeoff'
    WHEN flight_id = '4978' AND (time_min BETWEEN 18.1 AND 24) THEN 'cruise'
    WHEN flight_id = '4978' AND (time_min BETWEEN 24.1 AND 27) THEN 'HASEL'
    WHEN flight_id = '4978' AND (time_min BETWEEN 27.1 AND 31) THEN 'slow flight'
    WHEN flight_id = '4978' AND (time_min BETWEEN 31.1 AND 34) THEN 'cruise'
    WHEN flight_id = '4978' AND (time_min BETWEEN 34.1 AND 36) THEN 'climb'
    WHEN flight_id = '4978' AND (time_min BETWEEN 36.1 AND 39) THEN 'cruise'
    WHEN flight_id = '4978' AND (time_min BETWEEN 39.1 AND 40.20) THEN 'descent'
    WHEN flight_id = '4978' AND (time_min BETWEEN 40.21 AND 42.44) THEN 'cruise'
    WHEN flight_id = '4978' AND (time_min BETWEEN 42.45 AND 46) THEN 'landing'
    WHEN flight_id = '4978' AND (time_min > 46) THEN 'post-flight'
    ELSE activity  -- Keep the existing value for other rows
END
WHERE flight_id = '4978';

"""

LABEL_5116 = """
UPDATE flight_activities
SET activity = CASE
    WHEN flight_id = '5116' AND (time_min < 12.24) THEN 'pre-flight'
    WHEN flight_id = '5116' AND (time_min BETWEEN 12.24 AND 12.94) THEN 'takeoff'
    WHEN flight_id = '5116' AND (time_min BETWEEN 12.95 AND 14.44) THEN 'climb'
    WHEN flight_id = '5116' AND (time_min BETWEEN 14.45 AND 28.01) THEN 'cruise'
    WHEN flight_id = '5116' AND (time_min BETWEEN 28.02 AND 28.76) THEN 'descent'
    WHEN flight_id = '5116' AND (time_min BETWEEN 28.77 AND 29.84) THEN 'landing'
    WHEN flight_id = '5116' AND (time_min BETWEEN 29.85 AND 30.39) THEN 'takeoff'
    WHEN flight_id = '5116' AND (time_min BETWEEN 30.40 AND 31.46) THEN 'climb'
    WHEN flight_id = '5116' AND (time_min BETWEEN 31.47 AND 32.19) THEN 'cruise'
    WHEN flight_id = '5116' AND (time_min BETWEEN 32.20 AND 33.03) THEN 'descent'
    WHEN flight_id = '5116' AND (time_min BETWEEN 33.04 AND 34.98) THEN 'landing'
    WHEN flight_id = '5116' AND (time_min > 34.98 ) THEN 'post-flight'
    ELSE activity  -- Keep the existing value for other rows
END
WHERE flight_id = '5116';
"""

LABEL_5362 = """
UPDATE flight_activities
SET activity = CASE
    WHEN flight_id = '5362' AND (time_min < 17.08) THEN 'pre-flight'
    WHEN flight_id = '5362' AND (time_min BETWEEN 17.08 AND 17.42) THEN 'takeoff'
    WHEN flight_id = '5362' AND (time_min BETWEEN 17.43 AND 20.8) THEN 'climb'
    WHEN flight_id = '5362' AND (time_min BETWEEN 20.81 AND 23.91) THEN 'cruise'
    WHEN flight_id = '5362' AND (time_min BETWEEN 23.92 AND 24.4) THEN 'descent'
    WHEN flight_id = '5362' AND (time_min BETWEEN 24.41 AND 25.42) THEN 'HASEL'
    WHEN flight_id = '5362' AND (time_min BETWEEN 25.43 AND 26.39) THEN 'steep turn'
    WHEN flight_id = '5362' AND (time_min BETWEEN 26.4 AND 27.35) THEN 'power off stall'
    WHEN flight_id = '5362' AND (time_min BETWEEN 27.36 AND 28.15) THEN 'slow flight'
    WHEN flight_id = '5362' AND (time_min BETWEEN 28.16 AND 28.81) THEN 'descent'
    WHEN flight_id = '5362' AND (time_min BETWEEN 28.82 AND 31.15) THEN 'cruise'
    WHEN flight_id = '5362' AND (time_min BETWEEN 31.16 AND 32.45) THEN 'descent'
    WHEN flight_id = '5362' AND (time_min BETWEEN 32.46 AND 34.01) THEN 'landing'
    WHEN flight_id = '5362' AND (time_min BETWEEN 34.02 AND 34.39) THEN 'takeoff'
    WHEN flight_id = '5362' AND (time_min BETWEEN 34.4 AND 35.79) THEN 'climb'
    WHEN flight_id = '5362' AND (time_min BETWEEN 35.8 AND 36.9) THEN 'cruise'
    WHEN flight_id = '5362' AND (time_min BETWEEN 36.91 AND 38.75) THEN 'landing'
    WHEN flight_id = '5362' AND (time_min > 38.76) THEN 'post-flight'
    ELSE activity  -- Keep the existing value for other rows
END
WHERE flight_id = '5362';
"""

LABELED_ACTIVITIES_VIEW = """
CREATE OR REPLACE VIEW labeled_activities_view AS
SELECT
    f.*,
    COALESCE(fa.activity, 'TBD') AS activity
FROM flight_weather_data_view f
LEFT JOIN flight_activities fa ON f.flight_id = fa.flight_id AND f.time_min = fa.time_min;
"""

MANUAL_FLIGHTS_TO_LABEL = """
SELECT 
    COUNT(*) = COUNT(CASE WHEN table_name IN ('flightdata_4620', 'flightdata_4929', 'flightdata_4940', 'flightdata_5019', 'flightdata_5021', 'flightdata_5034') THEN 1 END) AS all_tables_exist
FROM 
    information_schema.tables
WHERE 
    table_schema = 'your_schema_name'
    AND table_name IN ('flightdata_4620', 'flightdata_4929', 'flightdata_4940', 'flightdata_5019', 'flightdata_5021', 'flightdata_5034')
"""

SCRAPER_RUNTIME = """
CREATE TABLE scraper_last_run (
    runtime TIMESTAMP
);
"""

PILOT_WEIGHTS = """
UPDATE flights SET total_weight=1296.42 WHERE id=4620;
UPDATE flights SET total_weight=1237.22 WHERE id=4622;
UPDATE flights SET total_weight=1264.62 WHERE id=4633;
UPDATE flights SET total_weight=1205.42 WHERE id=4636;
UPDATE flights SET total_weight=1185.62 WHERE id=4669;
UPDATE flights SET total_weight=1199.22 WHERE id=4766;
UPDATE flights SET total_weight=1242.62 WHERE id=4783;
UPDATE flights SET total_weight=1205.42 WHERE id=4802;
UPDATE flights SET total_weight=1253.42 WHERE id=4850;
UPDATE flights SET total_weight=1253.42 WHERE id=4853;
UPDATE flights SET total_weight=1194.22 WHERE id=4857;
UPDATE flights SET total_weight=1253.42 WHERE id=4860;
UPDATE flights SET total_weight=1253.42 WHERE id=4862;
UPDATE flights SET total_weight=1075.42 WHERE id=4871;
UPDATE flights SET total_weight=1164.22 WHERE id=4901;
UPDATE flights SET total_weight=1075.42 WHERE id=4904;
UPDATE flights SET total_weight=1248.42 WHERE id=4906;
UPDATE flights SET total_weight=1164.22 WHERE id=4909;
UPDATE flights SET total_weight=1164.22 WHERE id=4915;
UPDATE flights SET total_weight=1075.42 WHERE id=4919;
UPDATE flights SET total_weight=1075.42 WHERE id=4921;
UPDATE flights SET total_weight=1075.42 WHERE id=4923;
UPDATE flights SET total_weight=1045.42 WHERE id=4925;
UPDATE flights SET total_weight=1045.42 WHERE id=4927;
UPDATE flights SET total_weight=1045.42 WHERE id=4929;
UPDATE flights SET total_weight=1075.42 WHERE id=4936;
UPDATE flights SET total_weight=1075.42 WHERE id=4938;
UPDATE flights SET total_weight=1225.42 WHERE id=4940;
UPDATE flights SET total_weight=1075.42 WHERE id=4975;
UPDATE flights SET total_weight=1231.62 WHERE id=4976;
UPDATE flights SET total_weight=1231.62 WHERE id=4978;
UPDATE flights SET total_weight=1231.62 WHERE id=4981;
UPDATE flights SET total_weight=1045.42 WHERE id=4990;
UPDATE flights SET total_weight=1201.62 WHERE id=4992;
UPDATE flights SET total_weight=1231.62 WHERE id=5037;
UPDATE flights SET total_weight=1231.62 WHERE id=5039;
UPDATE flights SET total_weight=1195.42 WHERE id=5064;
"""
