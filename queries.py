# file with database queries

## Create Flights Table
CREATE_FLIGHTS = """
CREATE TABLE flights (
  id INTEGER PRIMARY KEY, 
  flight_date DATE NOT NULL, 
  flight_time_utc TIME NOT NULL,
  flight_notes VARCHAR(1000)
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
	bat_1_soc int8,
	bat_2_soc int8,
	bat_1_soh int8,
	bat_2_soh int8,
	bat_1_min_cell_temp int8,
	bat_2_min_cell_temp int8,
	bat_1_max_cell_temp int8,
	bat_2_max_cell_temp int8,
	bat_1_avg_cell_temp int8 ,
	bat_2_avg_cell_temp int8 ,
	bat_1_min_cell_volt float8 ,
	bat_2_min_cell_volt float8 ,
	bat_1_max_cell_volt float8 ,
	bat_2_max_cell_volt float8 ,
	requested_torque int8 ,
	motor_rpm int8 ,
	motor_power int8 ,
	motor_temp float8 ,
	ias float8 ,
	stall_warn_active int8 ,
	inverter_temp float8 ,
	bat_1_cooling_temp int8 ,
	inverter_cooling_temp_1 int8 ,
	inverter_cooling_temp_2 int8 ,
	remaining_flight_time int8 ,
	pressure_alt float8 ,
	lat float8 ,
	lng float8 ,
	ground_speed float8 ,
	pitch float8 ,
	roll float8 ,
	"time_stamp" int8 ,
	heading float8 ,
	stall_diff_pressure float8 ,
	qng float8 ,
	oat float8 ,
	iso_leakage_current int8 
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
    fd.*,
    w.*
FROM flight_weather fw
JOIN flights ff ON fw.flight_id = ff.id
JOIN weather w ON fw.weather_id = w.id
JOIN LATERAL get_flight_data(fw.flight_id) fd ON true;
"""