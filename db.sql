-- Create Flights Table
CREATE TABLE flights (
  id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY, 
  flight_date DATE NOT NULL, 
  flight_time_utc TIME NOT NULL,
  flight_notes VARCHAR(1000)
  );

-- Create Weather Table
CREATE TABLE weather (
  id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  weather_date DATE NOT NULL, -- this will be parsed from valid
  weather_time_utc TIME NOT NULL, -- this will be parsed from valid
  temperature REAL NOT NULL, -- in fahrenheit at 2 meters
  dewpoint REAL NOT NULL, -- in fahrenheit at 2 meters
  relative_humidity REAL NOT NULL, -- in %
  wind_direction SMALLINT, -- in degrees from true north
  wind_speed SMALLINT NOT NULL, -- in knots
  pressure_altimeter REAL NOT NULL, -- in inches
  sea_level_pressure REAL NOT NULL, -- in millibar, note this is on average off by 1.02 millibars, according to https://www.sensorsone.com/inhg-to-mbar-conversion-table/
  visibility REAL NOT NULL, -- in miles
  wind_gust SMALLINT, -- in knots, this one has a lot of nulls so we might remove it entirely
  sky_coverage_1 VARCHAR(3), -- sky coverage by level, does have significant nulls
  sky_coverage_2 VARCHAR(3),
  sky_coverage_3 VARCHAR(3),
  sky_coverage_4 VARCHAR(3), -- most nulls are for the higher sky levels
  sky_level_1 SMALLINT, -- sky level altitude in feet, does have significant nulls 
  sky_level_2 SMALLINT,
  sky_level_3 SMALLINT,
  sky_level_4 SMALLINT, -- most nulls are for the higher sky levels
  weather_codes VARCHAR(12), -- space separated weather codes
  metar VARCHAR(200) -- raw METAR format observation
);

-- Create intermediate flight and weather table
-- Purpose: be able to link weather data to the correct flight
CREATE TABLE flight_weather (
  flight_id INTEGER REFERENCES flights(id),
  weather_id INTEGER REFERENCES weather(id)
  );

-- Create flight data table
-- NOTE: this table will only be created once a flight id exists in the database
-- it will use the id column from the flights table, and then populate flight data
-- each table will have a unique name, flightdata_<flight_id>, where <flight_id> might be 4710:
CREATE TABLE flightdata_4710 (
  flight_id INTEGER REFERENCES flights(id),
  time_min DOUBLE PRECISION NOT NULL,
  bat_1_current REAL NOT NULL,
  bat_1_voltage REAL NOT NULL,
  bat_2_current REAL NOT NULL,
  bat_2_voltage REAL NOT NULL,
  bat_1_soc SMALLINT NOT NULL,
  bat_2_soc SMALLINT NOT NULL,
  bat_1_soh SMALLINT NOT NULL,
  bat_2_soh SMALLINT NOT NULL,
  bat_1_min_cell_temp SMALLINT NOT NULL,
  bat_2_min_cell_temp SMALLINT NOT NULL,
  bat_1_max_cell_temp SMALLINT NOT NULL,
  bat_2_max_cell_temp SMALLINT NOT NULL,
  bat_1_avg_cell_temp SMALLINT NOT NULL,
  bat_2_avg_cell_temp SMALLINT NOT NULL,
  bat_1_min_cell_volt REAL NOT NULL,
  bat_2_min_cell_volt REAL NOT NULL,
  bat_1_max_cell_volt REAL NOT NULL,
  bat_2_max_cell_volt REAL NOT NULL,
  requested_torque SMALLINT NOT NULL,
  motor_rpm SMALLINT NOT NULL,
  motor_power SMALLINT NOT NULL,
  motor_temp DOUBLE PRECISION NOT NULL,
  ias DOUBLE PRECISION NOT NULL,
  stall_warn_active SMALLINT NOT NULL,
  inverter_temp DOUBLE PRECISION NOT NULL,
  bat_1_cooling_temp SMALLINT NOT NULL,
  inverter_cooling_temp_1 SMALLINT NOT NULL,
  inverter_cooling_temp_2 SMALLINT NOT NULL,
  remaining_flight_time SMALLINT NOT NULL,
  pressure_alt DOUBLE PRECISION NOT NULL,
  lat DOUBLE PRECISION NOT NULL,
  lng DOUBLE PRECISION NOT NULL,
  ground_speed REAL NOT NULL,
  pitch DOUBLE PRECISION NOT NULL,
  roll DOUBLE PRECISION NOT NULL,
  time_stamp INTEGER NOT NULL,
  heading DOUBLE PRECISION NOT NULL,
  stall_diff_pressure DOUBLE PRECISION NOT NULL,
  qng DOUBLE PRECISION NOT NULL,
  oat REAL NOT NULL,
  iso_leakage_current SMALLINT NOT NULL
);
