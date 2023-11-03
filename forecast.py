import requests
import pandas as pd
from dotenv import load_dotenv
import os
from storage import db_connect, execute

# api_url = "https://api.open-meteo.com/v1/forecast?latitude=43.4668&longitude=-80.5164&minutely_15=temperature_2m,weathercode,windgusts_10m,visibility,lightning_potential&hourly=winddirection_180m&windspeed_unit=kn&forecast_days=3"
api_url = "https://api.open-meteo.com/v1/forecast?latitude=43.4668&longitude=-80.5164&minutely_15=temperature_2m,weathercode,windgusts_10m,visibility,lightning_potential&hourly=winddirection_180m&windspeed_unit=kn&timezone=America%2FNew_York&forecast_days=3"
response = requests.get(api_url)
if response.status_code == 200:
    print(response.json())
else:
    print(f'Failed to fetch data. Status code: {response.status_code}')

data = response.json()
df_15 = pd.DataFrame(data["minutely_15"])
df_15['time'] = pd.to_datetime(df_15['time'])
print(df_15.head())
df_1h = pd.DataFrame(data["hourly"])
df_1h['time'] = pd.to_datetime(df_1h['time'])
print(df_1h.head())

df_combined = pd.merge(df_15, df_1h, on="time", how="left")
df_combined['winddirection_180m'].fillna(method='ffill', inplace=True)


load_dotenv()
connection_string = os.getenv('DATABASE_URL')

#