# file with database queries

## Create Flights Table
CREATE_FLIGHTS = """
CREATE TABLE flights (
  id INTEGER PRIMARY KEY, 
  flight_date DATE NOT NULL, 
  flight_time_utc TIME NOT NULL,
  flight_notes VARCHAR(500)
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
  wind_direction SMALLINT NOT NULL,
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