import requests
import pandas as pd
from dotenv import load_dotenv
import os
import queries
from storage import db_connect, execute, table_exists
from sqlalchemy import create_engine

# get data
api_url = "https://api.open-meteo.com/v1/forecast?latitude=43.4668&longitude=-80.5164&minutely_15=temperature_2m,weathercode,windgusts_10m,visibility,lightning_potential&hourly=winddirection_180m&windspeed_unit=kn&timezone=America%2FNew_York&forecast_days=3"
response = requests.get(api_url)
data = response.json()

# parse data into pandas df
df_15 = pd.DataFrame(data["minutely_15"])
df_15['time'] = pd.to_datetime(df_15['time'])
df_1h = pd.DataFrame(data["hourly"])
df_1h['time'] = pd.to_datetime(df_1h['time'])
df_combined = pd.merge(df_15, df_1h, on="time", how="left")
df_combined['winddirection_180m'].fillna(method='ffill', inplace=True)
df_combined.insert(0, 'forecast_time_et', df_combined['time'].dt.time)
df_combined.insert(0, 'forecast_date', df_combined['time'].dt.date)
df_combined.pop(df_combined.columns[2])

# drop the forecast table if it exists
load_dotenv()
connection_string = os.getenv('DATABASE_URL')
conn = db_connect()
if table_exists("forecast", conn):
  execute("DROP TABLE forecast;")

# push the data to the forecast table
engine_string = "postgresql+psycopg2" + os.getenv('DATABASE_URL')[8:]
engine = create_engine(engine_string)
# add new table to db
df_combined.to_sql("forecast", engine, if_exists="fail", index=False)