from datetime import datetime
from pandas import pd
# How long does 1 single flight take (on average: including time for inspection, flight, charging):
avg_inspection_time_before_flight = 7.41
avg_flight_time = 31.5
avg_charging_time = 58.56
total_flight_time = avg_inspection_time_before_flight + avg_flight_time + avg_charging_time
print (total_flight_time)

# Pull in weather data [PETER]
# Classify the weather data into zones (9 to 10 am -> green zone)
# Need to find a period of time for 30 minutes FOR flight but need 1.5 hours total for everything
    #STRIP INTO TIME INTERVALS

#pull in forecasted weather data (right now it's hardcoded)
visibility = 14600.00


#visibility (converting m to SM)
visability_zone = ""
visibility_SM = visibility *  0.000621371

if (visibility_SM) < 3:
    visability_zone = "red"
elif (visibility_SM < 6):
    visability_zone = "yellow"
elif (pd.isna(visibility_SM)):
    visability_zone == "gray"
else:
    visability_zone = "green"

#cloud (pulled from weathercode)
cloud_zone = ""
cloud = 0 # hardcoded value, will pull from forecasted weather data

if cloud == 3:
    cloud_zone = "red"
elif cloud == 2:
    cloud_zone = "yellow"
elif (pd.isna(cloud)):
    cloud_zone == "gray"
else:
    cloud_zone = "green"

#rain 
rain_zone = ""
rain = 0 # hardcoded value, will pull from forecasted weather data

if rain == 65:
    rain_zone = "red"
elif rain == 63:
    rain_zone = "yellow"
elif (pd.isna(rain)):
    rain_zone == "gray"
else:
    rain_zone = "green"

#rain showers
rain_shower_zone = ""
rain_shower = 0 # hardcoded value, will pull from forecasted weather data

if rain_shower == 82:
    rain_shower_zone = "red"
elif rain_shower == 81:
    rain_shower_zone = "yellow"
elif (pd.isna(rain_shower)):
    rain_shower_zone == "gray"
else:
    rain_shower_zone = "green"

#thunderstorm (pulled from weathercode)
thunderstorm_zone = ""
thunderstorm = 0 # hardcoded value, will pull from forecasted weather data

if thunderstorm == 96:
    thunderstorm_zone = "red"
elif (pd.isna(thunderstorm)):
    thunderstorm_zone == "gray"
else:
    thunderstorm_zone = "green"

#snow fall (pulled from weathercode): this includes snow fall, snow grains and snow showers
snowfall_zone = ""
snowfall = 0 # hardcoded value, will pull from forecasted weather data

if (snowfall == 71) or (snowfall == 73) or (snowfall == 75) or (snowfall == 77) or (snowfall == 85) or (snowfall == 86):
    snowfall_zone = "red"
elif (pd.isna(snowfall)):
    snowfall_zone == "gray"
else:
    snowfall_zone = "green"
    
# freezing rain and drizzle
freezing_rain_zone = ""
freezing_drizzle_zone = ""
freezing_rain = 0 # hardcoded value, will pull from forecasted weather data
freezing_drizzle = 0 # hardcoded value, will pull from forecasted weather data

if (freezing_rain == 66) or (freezing_rain == 67) or (freezing_drizzle == 56) or (freezing_drizzle == 57):
    freezing_rain_zone = "red"
    freezing_drizzle_zone = "red"
elif (pd.isna(freezing_rain) or pd.isna(freezing_drizzle)):
    freezing_rain_zone = "gray"
    freezing_drizzle_zone = "gray"
else:
    freezing_rain_zone = "green"
    freezing_drizzle_zone = "green"


#gust (MAKE SURE TO DOWNLOAD CSV WITH UNITS AS KNOTS)
wind_gusts_zone = ""
wind_gusts = 0

if (wind_gusts) >= 30:
    wind_gusts_zone = "red"
elif (wind_gusts >= 25):
    wind_gusts_zone = "yellow"
elif (pd.isna(wind_gusts)):
    wind_gusts_zone == "gray"
else:
    wind_gusts_zone = "green"

#temperature 
temperature_zone = ""
temperature = 0 # hardcoded value, will pull from forecasted weather data

if (temperature > 35) or (temperature < -20):
    temperature_zone = "red"
elif (temperature > 30) or (temperature < -10):
    temperature_zone = "yellow"
elif (pd.isna(temperature)):
    temperature_zone == "gray"
else:
    temperature_zone = "green"

#lightning potential -> double check!! -> JOANNA MAKE QUESTION
lightning_potential_index_zone = ""
lightning_potential_index = 0

if (lightning_potential_index > 0):
    lightning_potential_index_zone = "red"
elif (lightning_potential_index == 0):
    lightning_potential_index_zone = "yellow"
#ACC SHOULD BE GREEN: -> but it would never be green makes no sense
elif (pd.isna(lightning_potential_index)):
    lightning_potential_index_zone == "gray"
else:
    lightning_potential_index = "green"

#time of day 
time_of_day_zone = ""
#make sure this is the datetime datatype
time_of_day = 0 # This is the format from data: 2023-10-28T07:52


dt = datetime.strptime(time_of_day, "%Y-%m-%dT%H:%M")

print(dt)  # Example - This will print: 2023-10-28 07:52:00

#loop through time column, check if each of the times in a row are less than sunrise -> red