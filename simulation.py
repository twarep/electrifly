from datetime import datetime, timedelta, time
from sys import displayhook
import pandas as pd
from sqlalchemy import create_engine
from weather_forcast_querying import get_forecast_by_current_date
import forecast

# How long does 1 single flight take (on average: including time for inspection, flight, charging):
avg_inspection_time_before_flight = 7.41
avg_flight_time = 31.5
avg_charging_time = 58.56
total_flight_time = avg_inspection_time_before_flight + avg_flight_time + avg_charging_time
print ("This is the total flight time:", total_flight_time)

# Pull in weather data [PETER]
# Classify the weather data into zones (9 to 10 am -> green zone)
# Need to find a period of time for 30 minutes FOR flight but need 1.5 hours total for everything
    #STRIP INTO TIME INTERVALS

#pull in forecasted weather data (right now it's hardcoded)
forecast_df = get_forecast_by_current_date()
forecast_date = forecast_df["Forecast Date"]
forecast_time_et = forecast_df["Forecast Time"]

#VISIBILITY:
visibility = forecast_df["Visibility"]
visability_zone = ""
#visibility (converting m to SM)
visibility_SM = visibility *  0.000621371
visability_zone_list = []

for i in visibility_SM.index:
    if (pd.isna(visibility_SM[i])):
        visability_zone = "gray"
    elif(visibility_SM[i]) < 3:
        visability_zone = "red"
    elif (visibility_SM[i]< 6):
        visability_zone = "yellow"
    else:
        visability_zone = "green"
    visability_zone_list.append(visability_zone)
# Create a new DataFrame
visability_zone_df_all = pd.DataFrame({
    "Forecast Date": forecast_date,
    "Forecast Time": forecast_time_et,
    "Visibility SM": visibility_SM,
    "Visibility Zone": visability_zone_list
})

print(visability_zone_df_all)

#CLOUD (pulled from weathercode):
cloud = forecast_df["Weathercode"]
cloud_zone = ""
cloud_zone_list = []

for i in cloud.index:
    if(pd.isna(cloud[i])):
        cloud_zone = "gray"
    elif cloud[i] == 3:
        cloud_zone = "red"
    elif cloud[i] == 2:
        cloud_zone = "yellow"
    
    else:
        cloud_zone = "green"
    cloud_zone_list.append(cloud_zone)

# Create a new DataFrame
cloud_zone_df_all = pd.DataFrame({
    "Forecast Date": forecast_date,
    "Forecast Time": forecast_time_et,
    "Cloud": cloud,
    "Cloud Zone": cloud_zone_list
})

print(cloud_zone_df_all)

#rain 
rain = forecast_df["Weathercode"]
rain_zone = ""
rain_zone_list = []

for i in rain.index:
    if (pd.isna(rain[i])):
        rain_zone = "gray"   
    elif rain[i] == 65:
        rain_zone = "red"
    elif rain[i] == 63:
        rain_zone = "yellow"
    else:
        rain_zone = "green"
    rain_zone_list.append(rain_zone)

# Create a new DataFrame
rain_zone_df_all = pd.DataFrame({
    "Forecast Date": forecast_date,
    "Forecast Time": forecast_time_et,
    "Rain": rain,
    "Rain Zone": rain_zone_list
})

print(rain_zone_df_all)

#rain showers
rain_shower = forecast_df["Weathercode"]
rain_shower_zone = ""
rain_shower_zone_list = []

for i in rain_shower.index:
    if (pd.isna(rain_shower[i])):
        rain_shower_zone = "gray"
    elif rain_shower[i] == 82:
        rain_shower_zone = "red"
    elif rain_shower[i] == 81:
        rain_shower_zone = "yellow"
    else:
        rain_shower_zone = "green"
    rain_shower_zone_list.append(rain_shower_zone)

# Create a new DataFrame
rain_shower_zone_df_all = pd.DataFrame({
    "Forecast Date": forecast_date,
    "Forecast Time": forecast_time_et,
    "Rain Shower": rain_shower,
    "Rain Shower Zone": rain_shower_zone_list
})

print(rain_shower_zone_df_all)


#thunderstorm (pulled from weathercode)
thunderstorm = forecast_df["Weathercode"]
thunderstorm_zone = ""
thunderstorm_zone_list = []

for i in thunderstorm.index:
    if (pd.isna(thunderstorm[i])):
        thunderstorm_zone = "gray"
    elif thunderstorm[i] == 96:
        thunderstorm_zone = "red"
    else:
        thunderstorm_zone = "green"
    thunderstorm_zone_list.append(thunderstorm_zone)

# Create a new DataFrame
thunderstorm_zone_df_all = pd.DataFrame({
    "Forecast Date": forecast_date,
    "Forecast Time": forecast_time_et,
    "Thunderstorm": thunderstorm,
    "Thunderstorm Zone": thunderstorm_zone_list
})

print(thunderstorm_zone_df_all)


#snow fall (pulled from weathercode): this includes snow fall, snow grains and snow showers
snowfall = forecast_df["Weathercode"]
snowfall_zone = ""
snowfall_zone_list = []

for i in snowfall.index:
    if (pd.isna(snowfall[i])):
        snowfall_zone = "gray"
    elif (snowfall[i] == 71) or (snowfall[i] == 73) or (snowfall[i] == 75) or (snowfall[i] == 77) or (snowfall[i] == 85) or (snowfall[i] == 86):
        snowfall_zone = "red"
    else:
        snowfall_zone = "green"
    snowfall_zone_list.append(snowfall_zone)
    
# Create a new DataFrame
snowfall_zone_df_all = pd.DataFrame({
    "Forecast Date": forecast_date,
    "Forecast Time": forecast_time_et,
    "Snowfall": snowfall,
    "Snowfall Zone": snowfall_zone_list
})

print(snowfall_zone_df_all)

    
# freezing rain and freezing drizzle (both under freezing rain)
freezing_rain_zone = ""
freezing_rain = forecast_df["Weathercode"] 
freezing_rain_zone_list = []

for i in freezing_rain.index:
    if (pd.isna(freezing_rain[i])):
        freezing_rain_zone = "gray"
    elif (freezing_rain[i] == 66) or (freezing_rain[i] == 67) or (freezing_rain[i] == 56) or (freezing_rain[i] == 57):
        freezing_rain_zone = "red"
    else:
        freezing_rain_zone = "green"
    freezing_rain_zone_list.append(freezing_rain_zone)


# Create a new DataFrame
freezing_rain_df_all = pd.DataFrame({
    "Forecast Date": forecast_date,
    "Forecast Time": forecast_time_et,
    "Freezing Rain": freezing_rain,
    "Freezing Rain Zone": freezing_rain_zone_list
})

print(freezing_rain_df_all)

#gust (MAKE SURE TO DOWNLOAD CSV WITH UNITS AS KNOTS)
wind_gusts_zone = ""
wind_gusts = forecast_df["Wind Gusts"] 
wind_gusts_zone_list = []

for i in wind_gusts.index:
    if (pd.isna(wind_gusts[i])):
        wind_gusts_zone = "gray"    
    elif (wind_gusts[i]) >= 30:
        wind_gusts_zone = "red"
    elif (wind_gusts[i] >= 25):
        wind_gusts_zone = "yellow"
    else:
        wind_gusts_zone = "green"
    wind_gusts_zone_list.append(wind_gusts_zone)


# Create a new DataFrame
wind_gusts_df_all = pd.DataFrame({
    "Forecast Date": forecast_date,
    "Forecast Time": forecast_time_et,
    "Wind Gusts": wind_gusts,
    "Wind Gusts Zone": wind_gusts_zone_list
})

print(wind_gusts_df_all)


#temperature 
temperature_zone = ""
temperature = forecast_df["Temperature (°C)"] 
temperature_zone_list = []
for i in temperature.index:
    if (pd.isna(temperature[i])):
        temperature_zone = "gray"
    elif (temperature[i] > 35) or (temperature[i] < -20):
        temperature_zone = "red"
    elif (temperature[i] > 30) or (temperature[i] < -10):
        temperature_zone = "yellow"
    else:
        temperature_zone = "green"
    temperature_zone_list.append(temperature_zone)
# Create a new DataFrame
temperature_df_all = pd.DataFrame({
    "Forecast Date": forecast_date,
    "Forecast Time": forecast_time_et,
    "Temperature": temperature,
    "Temperature Zone": temperature_zone_list
})

print(temperature_df_all)


# lightning_potential_index_zone = ""
# lightning_potential_index = forecast_df["Lightning Potential"] 
# lightning_potential_index_zone_list = []

# for i in lightning_potential_index.index:
#     if (pd.isna(lightning_potential_index[i])):
#         lightning_potential_index_zone = "gray"
#     elif (lightning_potential_index[i] > 0):
#         lightning_potential_index_zone = "yellow"
#     else:
#         lightning_potential_index = "green"
#     lightning_potential_index_zone_list.append(lightning_potential_index_zone)

# # Create a new DataFrame
# lightning_potential_index_df_all = pd.DataFrame({
#     "Forecast Date": forecast_date,
#     "Forecast Time": forecast_time_et,
#     "Lightning Potential Index": lightning_potential_index,
#     "Lightning Potential Index": lightning_potential_index_zone_list
# })

# print(lightning_potential_index_df_all)

#sunrise "If any part of the flight is between: 
# RED is 30 mins AFTER sunset and 30 mins BEFORE sunrise 
#yellow as (15 mins BEFORE sunset to 30 mins AFTER sunset) and (30 mins BEFORE sunrise to 15 min after sunrise)
# green as 15 min after sunrise and 15 mins before sunset

sunrise = forecast_df["Sunrise"]
sunset = forecast_df["Sunset"] 
print(type(sunrise))
print(forecast_time_et)
print(sunrise)
delta_thirty = timedelta(minutes=30)
delta_fifteen = timedelta(minutes=15)

sunrise_sunset_zone = ""
sunrise_sunset_zone_list = []


for i in forecast_time_et.index:
    print(type(sunset[i]))
    sunset_30 = datetime.combine(forecast_date[i],sunset[i])
    sunrise_30 = datetime.combine(forecast_date[i],sunrise[i])
    if (forecast_time_et[i] > (sunset_30 + delta_thirty).time()) or (forecast_time_et[i] < (sunrise_30-delta_thirty).time()):
        sunrise_sunset_zone = "red"
    # elif ((forecast_time_et[i] < (sunset_30 - delta_fifteen).time()) and (forecast_time_et[i] > (sunset_30 + delta_thirty).time())) or ((forecast_time_et[i] < (sunrise_30 - delta_thirty).time()) and (forecast_time_et[i] > (sunrise_30 + delta_fifteen).time())):
    #     sunrise_sunset_zone = "yellow"
    elif (((sunset_30 - delta_fifteen).time()) < (forecast_time_et[i]) < (sunset_30 + delta_thirty).time()) or (((sunrise_30 - delta_thirty).time() < (forecast_time_et[i]) < (sunrise_30 + delta_fifteen).time())):
        sunrise_sunset_zone = "yellow"
    else:
        sunrise_sunset_zone = "green"
    sunrise_sunset_zone_list.append(sunrise_sunset_zone)
# Create a new DataFrame
sunrise_sunset_df_all = pd.DataFrame({
    "Forecast Date": forecast_date,
    "Forecast Time": forecast_time_et,
    "Sunrise": sunrise,
    "Sunset": sunset,
    "Sunrise Sunset Zone": sunrise_sunset_zone_list
})

print(sunrise_sunset_df_all)
sunrise_sunset_df_all.to_csv('sunrise_sunset_df_all')

zones_df_all = pd.DataFrame({
    "Forecast Date": forecast_date,
    "Forecast Time": forecast_time_et,
    "Visibility Zone": visability_zone_list,
    "Cloud Zone": cloud_zone_list,
    "Rain Zone": rain_zone_list,
    "Rain Shower Zone": rain_shower_zone_list,
    "Thunderstorm Zone": thunderstorm_zone_list,
    "Snowfall Zone": snowfall_zone_list,
    "Freezing Rain Zone": freezing_rain_zone_list,
    "Wind Gusts Zone": wind_gusts_zone_list,
    "Temperature Zone": temperature_zone_list,
    "Sunrise": sunrise,
    "Sunset": sunset,
    "Sunrise Sunset Zone": sunrise_sunset_zone_list
    # "Lightning Potential Index": lightning_potential_index_zone_list
})

print(zones_df_all)

# Function to prioritize colors
def prioritize_colors(row):
    if 'gray' in row.values:
        return 'gray'
    if 'red' in row.values:
        return 'red'
    elif 'yellow' in row.values:
        return 'yellow'
    else:
        return 'green'

# Create a new column 'final_color' based on the prioritized colors
zones_df_all['final_zone'] = zones_df_all.apply(prioritize_colors, axis=1)
print(zones_df_all)
zones_df_all.to_csv('zones_df_all')


final_zones_color = pd.DataFrame({
    "Forecast Date": forecast_date,
    "Forecast Time": forecast_time_et,
    "Zone": zones_df_all['final_zone']
})

#extract each date into its own column
#get rid of the duplicate time columns
#stitch it together in a dataframe

displayhook(final_zones_color.iloc[96])

df0 = final_zones_color.iloc[0:96, 1] 
df1 = final_zones_color.iloc[0:96, 2] 
df2 = final_zones_color.iloc[96:192, 2] 
df2 = df2.reset_index() 
df3 = final_zones_color.iloc[192:288, 2] 
df3 = df3.reset_index() 
print(df0)
print(df1)
print(df2)
print(df3)

# new_df = final_zones_color['Forecast Date'].unique()
# print(new_df)

first_date= final_zones_color.iloc[0, 0]
print(first_date) 
second_date= final_zones_color.iloc[96, 0]
print(second_date) 
third_date= final_zones_color.iloc[192, 0]
print(third_date) 


full = [df0, df1, df2, df3]
result_table_colours = pd.concat(full, axis=1)
result_table_colours.columns = ["Forecast Time", first_date, "index", second_date, "index", third_date]
del result_table_colours['index']
print(result_table_colours)

final_zones_color.to_csv('final_zones_color')
result_table_colours.to_csv('result_table_colours')