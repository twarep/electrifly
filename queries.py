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

with flightweather_joined2 AS (
    SELECT
        fw.flight_id,
        f.flight_date,
        f.flight_time_utc,
        f.flight_type,
        f.total_weight,
        w.id as weather_id,
        w.weather_date,
        w.weather_time_utc,
        w.temperature,
        w.dewpoint,
        w.relative_humidity,
        w.wind_direction,
        w.wind_speed,
        w.pressure_altimeter,
        w.sea_level_pressure,
        w.visibility,
        w.wind_gust,
        w.sky_coverage_1,
        w.sky_coverage_2,
        w.sky_coverage_3,
        w.sky_coverage_4,
        w.sky_level_1,
        w.sky_level_2,
        w.sky_level_3,
        w.sky_level_4,
        w.weather_codes,
        w.metar
    FROM
        flight_weather fw
    JOIN weather w ON fw.weather_id = w.id
    join flights f  on f.id = fw.flight_id 

),

duplicate_flightweather_joined2 as (
	select 
		fw.flight_id as fw_flight_id,
		fw.flight_date,
		fw.flight_time_utc,
		fw.flight_type,
		fw.total_weight,
		fw.weather_id,
		fw.weather_date,
		fw.weather_time_utc, 
		fw.temperature,
		fw.dewpoint,
        fw.relative_humidity,
        fw.wind_direction,
		fw.wind_speed,
		fw.pressure_altimeter,
        fw.sea_level_pressure,
        fw.visibility,
        fw.wind_gust,
        fw.sky_coverage_1,
        fw.sky_coverage_2,
        fw.sky_coverage_3,
        fw.sky_coverage_4,
        fw.sky_level_1,
        fw.sky_level_2,
        fw.sky_level_3,
        fw.sky_level_4,
        fw.weather_codes,
        fw.metar,
		
        fd.flight_id as flight_id,
		fd.time_min, 
		fd.bat_1_current, 
		fd.bat_1_voltage, 
		fd.bat_2_current, 
		fd.bat_2_voltage, 
		fd.bat_1_soc, 
		fd.bat_2_soc, 
		fd.bat_1_soh, 
		fd.bat_2_soh, 
		fd.bat_1_min_cell_temp, 
		fd.bat_2_min_cell_temp, 
		fd.bat_1_max_cell_temp, 
		fd.bat_2_max_cell_temp, 
		fd.bat_1_avg_cell_temp, 
		fd.bat_2_avg_cell_temp, 
		fd.bat_1_min_cell_volt, 
		fd.bat_2_min_cell_volt, 
		fd.bat_1_max_cell_volt, 
		fd.bat_2_max_cell_volt, 
		fd.requested_torque, 
		fd.motor_rpm, 
		fd.motor_power, 
		fd.motor_temp, 
		fd.ias, 
		fd.stall_warn_active, 
		fd.inverter_temp, 
		fd.bat_1_cooling_temp, 
		fd.inverter_cooling_temp_1, 
		fd.inverter_cooling_temp_2, 
		fd.remaining_flight_time, 
		fd.pressure_alt, fd.lat, fd.lng, 
		fd.ground_speed, fd.pitch, fd.roll, 
		fd.time_stamp, fd.heading, 
		fd.stall_diff_pressure, fd.qng, 
		fd.oat, fd.iso_leakage_current,
		ABS(EXTRACT(epoch FROM (fw.flight_time_utc + (fd.time_min || ' minutes')::interval  - fw.weather_time_utc) ) / 60) as time_diff_current
	from flightweather_joined2 fw 
		join get_flight_data(fw.flight_id) fd(flight_id, time_min, bat_1_current, bat_1_voltage, bat_2_current, bat_2_voltage, bat_1_soc, bat_2_soc, bat_1_soh, bat_2_soh, bat_1_min_cell_temp, bat_2_min_cell_temp, bat_1_max_cell_temp, bat_2_max_cell_temp, bat_1_avg_cell_temp, bat_2_avg_cell_temp, bat_1_min_cell_volt, bat_2_min_cell_volt, bat_1_max_cell_volt, bat_2_max_cell_volt, requested_torque, motor_rpm, motor_power, motor_temp, ias, stall_warn_active, inverter_temp, bat_1_cooling_temp, inverter_cooling_temp_1, inverter_cooling_temp_2, remaining_flight_time, pressure_alt, lat, lng, ground_speed, pitch, roll, time_stamp, heading, stall_diff_pressure, qng, oat, iso_leakage_current)
		on fw.flight_id = fd.flight_id 
),

ranked_data as(
	SELECT *,
		row_number () OVER(PARTITION BY fw_flight_id, time_min ORDER BY time_diff_current asc) as row_num
	FROM duplicate_flightweather_joined2
	order by fw_flight_id asc
)

select * from ranked_data where row_num = 1;
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
SELECT flight_id, time_min FROM flightdata_5034;
"""

ADD_ACTIVITY_COLUMN = """
ALTER TABLE flight_activities
ADD COLUMN activity VARCHAR(255) DEFAULT 'NA';
"""

LABEL_4620 = """
UPDATE flight_activities
SET activity = CASE
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
    ELSE activity  -- Keep the existing value for other rows
END
WHERE flight_id = 4620;
"""

LABEL_4929 = """
UPDATE flight_activities
SET activity = CASE
    WHEN flight_id = 4929 AND (time_min BETWEEN 7.65 AND 8.5) THEN 'takeoff'
    WHEN flight_id = 4929 AND (time_min BETWEEN 8.6 AND 10.9) THEN 'climb'
    WHEN flight_id = 4929 AND (time_min BETWEEN 11 AND 28.8) THEN 'cruise'
    WHEN flight_id = 4929 AND (time_min BETWEEN 28.9 AND 30.4) THEN 'descent'
    WHEN flight_id = 4929 AND (time_min BETWEEN 30.5 AND 35) THEN 'landing'
    ELSE activity  -- Keep the existing value for other rows
END
WHERE flight_id = 4929;
"""

LABEL_4940 = """
UPDATE flight_activities
SET activity = CASE
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
    ELSE activity  -- Keep the existing value for other rows
END
WHERE flight_id = '4940';
"""

LABEL_5019 = """
UPDATE flight_activities
SET activity = CASE
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
    ELSE activity  -- Keep the existing value for other rows
END
WHERE flight_id = '5019';
"""

LABEL_5021 = """
UPDATE flight_activities
SET activity = CASE
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
    ELSE activity  -- Keep the existing value for other rows
END
WHERE flight_id = '5021';
"""

LABEL_5034 = """
UPDATE flight_activities
SET activity = CASE
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
    ELSE activity  -- Keep the existing value for other rows
END
WHERE flight_id = '5034';
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
