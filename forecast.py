import requests
import pandas as pd
import os
from storage import db_connect, execute, table_exists
from sqlalchemy import create_engine

# get data
def get_forcast_from_today():
    
    # NOTE: Please don't add the execute('DROP TABLE forecast;') here because it is already added to the function
    # weather_forecast_querying.get_forecast_by_current_date()
    
    # get the api call
    api_url = "https://api.open-meteo.com/v1/forecast?latitude=43.4668&longitude=-80.5164&minutely_15=temperature_2m,weathercode,windgusts_10m,visibility,lightning_potential&hourly=winddirection_10m&daily=sunrise,sunset&wind_speed_unit=kn&timezone=America%2FNew_York&forecast_days=3"
    response = requests.get(api_url)
    data = response.json()

    # parse data into pandas df
    df_15 = pd.DataFrame(data["minutely_15"])
    df_15['time'] = pd.to_datetime(df_15['time'])
    df_1h = pd.DataFrame(data["hourly"])
    df_1h['time'] = pd.to_datetime(df_1h['time'])
    df_daily = pd.DataFrame(data["daily"])
    df_daily['time'] = pd.to_datetime(df_daily['time'])
    df_daily['sunrise'] = pd.to_datetime(df_daily['sunrise'])
    df_daily['sunset'] = pd.to_datetime(df_daily['sunset'])
    df_combined = pd.merge(df_15, df_1h, on="time", how="left")
    df_combined = pd.merge(df_combined, df_daily, on="time", how="left")
    df_combined['winddirection_10m'].fillna(method='ffill', inplace=True)
    df_combined['sunrise'].fillna(method='ffill', inplace=True)
    df_combined['sunset'].fillna(method='ffill', inplace=True)
    df_combined.insert(0, 'forecast_time_et', df_combined['time'].dt.time)
    df_combined.insert(0, 'forecast_date', df_combined['time'].dt.date)
    df_combined.pop(df_combined.columns[2])
    df_combined.insert(2, 'sunset_time', df_combined['sunset'].dt.time)
    df_combined.insert(2, 'sunrise_time', df_combined['sunrise'].dt.time)
    df_combined.pop(df_combined.columns[-1])
    df_combined.pop(df_combined.columns[-1])

    # push the data to the forecast table
    engine_string = "postgresql+psycopg2" + os.getenv('DATABASE_URL')[8:]
    engine = create_engine(engine_string)

    # add new table to db
    df_combined.to_sql("forecast", engine, if_exists="fail", index=False)