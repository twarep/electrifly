from datetime import datetime, timedelta, time
from sys import displayhook
import pandas as pd
from sqlalchemy import create_engine
from weather_forcast_querying import get_forecast_by_current_date
import numpy as np

# How long does 1 single flight take (on average: including time for inspection, flight, charging):
avg_inspection_time_before_flight = 7.41
avg_flight_time = 31.5
avg_charging_time = 58.56
total_flight_time = avg_inspection_time_before_flight + avg_flight_time + avg_charging_time

# Classify the weather data into zones (9 to 10 am -> green zone)
# Need to find a period of time for 30 minutes FOR flight but need 1.5 hours total for everything
    #STRIP INTO TIME INTERVALS

# pull in forecasted weather data (right now it's hardcoded)
forecast_df = get_forecast_by_current_date()
forecast_date = forecast_df["Forecast Date"]
forecast_time_et = forecast_df["Forecast Time"]

explanations_mapping = {'red': [], 'yellow': [], 'green': []}

# store explanations for zone reasoning
explanation_df = pd.DataFrame({
    "Forecast Date": forecast_date,
    "Forecast Time": forecast_time_et,
    "Explanation": [{'red': [], 'yellow': [], 'green': []} for _ in range(len(forecast_df))]
    # "Explanation": np.empty((len(forecast_df), 0)).tolist(),
})

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
        exp = "Visibility is " + str(round(visibility_SM[i],2)) + " which is less than the threshold of 3"
        explanation_df.at[i, 'Explanation']['red'].append(exp)
        
    elif (visibility_SM[i]< 6):
        visability_zone = "yellow"
        exp = "Visibility is " + str(round(visibility_SM[i],2)) + " which is less than the threshold of 6"
        explanation_df.at[i, 'Explanation']['yellow'].append(exp)
    else:
        visability_zone = "green"
        exp = "Visibility is clear"
        explanation_df.at[i, 'Explanation']['green'].append(exp)
    visability_zone_list.append(visability_zone)
# Create a new DataFrame

format = '%H:%M'

visability_zone_df_all = pd.DataFrame({
    "Forecast Date": forecast_date,
    "Forecast Time": forecast_time_et,
    "Visibility SM": visibility_SM,
    "Visibility Zone": visability_zone_list
    
})

#CLOUD (pulled from weathercode):
cloud = forecast_df["Weathercode"]
cloud_zone = ""
cloud_zone_list = []

for i in cloud.index:
    if(pd.isna(cloud[i])):
        cloud_zone = "gray"
    elif cloud[i] == 3:
        cloud_zone = "red"
        exp = "Heavy cloud cover"
        explanation_df.at[i, 'Explanation']['red'].append(exp)
    elif cloud[i] == 2:
        cloud_zone = "yellow"
        exp = "Moderate cloud cover"
        explanation_df.at[i, 'Explanation']['yellow'].append(exp)
    else:
        cloud_zone = "green"
        exp = "Low cloud cover"
        explanation_df.at[i, 'Explanation']['green'].append(exp)
    cloud_zone_list.append(cloud_zone)

# Create a new DataFrame
cloud_zone_df_all = pd.DataFrame({
    "Forecast Date": forecast_date,
    "Forecast Time": forecast_time_et,
    "Cloud": cloud,
    "Cloud Zone": cloud_zone_list
})

#rain 
rain = forecast_df["Weathercode"]
rain_zone = ""
rain_zone_list = []

for i in rain.index:
    if (pd.isna(rain[i])):
        rain_zone = "gray"   
    elif rain[i] == 65:
        rain_zone = "red"
        exp = "Strong rain"
        explanation_df.at[i, 'Explanation']['red'].append(exp)
    elif rain[i] == 63:
        rain_zone = "yellow"
        exp = "Moderate rain"
        explanation_df.at[i, 'Explanation']['yellow'].append(exp)
    else:
        rain_zone = "green"
        exp = "Low rain"
        explanation_df.at[i, 'Explanation']['green'].append(exp)
    rain_zone_list.append(rain_zone)

# Create a new DataFrame
rain_zone_df_all = pd.DataFrame({
    "Forecast Date": forecast_date,
    "Forecast Time": forecast_time_et,
    "Rain": rain,
    "Rain Zone": rain_zone_list
})

#rain showers
rain_shower = forecast_df["Weathercode"]
rain_shower_zone = ""
rain_shower_zone_list = []

for i in rain_shower.index:
    if (pd.isna(rain_shower[i])):
        rain_shower_zone = "gray"
    elif rain_shower[i] == 82:
        rain_shower_zone = "red"
        exp = "Strong rain showers"
        explanation_df.at[i, 'Explanation']['red'].append(exp)
    elif rain_shower[i] == 81:
        rain_shower_zone = "yellow"
        exp = "Moderate rain showers"
        explanation_df.at[i, 'Explanation']['yellow'].append(exp)
    else:
        rain_shower_zone = "green"
        exp = "No rain showers"
        explanation_df.at[i, 'Explanation']['yellow'].append(exp)
    rain_shower_zone_list.append(rain_shower_zone)

# Create a new DataFrame
rain_shower_zone_df_all = pd.DataFrame({
    "Forecast Date": forecast_date,
    "Forecast Time": forecast_time_et,
    "Rain Shower": rain_shower,
    "Rain Shower Zone": rain_shower_zone_list
})


#thunderstorm (pulled from weathercode)
thunderstorm = forecast_df["Weathercode"]
thunderstorm_zone = ""
thunderstorm_zone_list = []

for i in thunderstorm.index:
    if (pd.isna(thunderstorm[i])):
        thunderstorm_zone = "gray"
    elif thunderstorm[i] == 96:
        thunderstorm_zone = "red"
        exp = "Thunderstorms"
        explanation_df.at[i, 'Explanation']['red'].append(exp)
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

#snow fall (pulled from weathercode): this includes snow fall, snow grains and snow showers
snowfall = forecast_df["Weathercode"]
snowfall_zone = ""
snowfall_zone_list = []

for i in snowfall.index:
    if (pd.isna(snowfall[i])):
        snowfall_zone = "gray"
    elif (snowfall[i] == 71) or (snowfall[i] == 73) or (snowfall[i] == 75) or (snowfall[i] == 77) or (snowfall[i] == 85) or (snowfall[i] == 86):
        snowfall_zone = "red"
        exp = "Snowfall"
        explanation_df.at[i, 'Explanation']['red'].append(exp)
    else:
        snowfall_zone = "green"
        exp = "No snowfall"
        explanation_df.at[i, 'Explanation']['green'].append(exp)
    snowfall_zone_list.append(snowfall_zone)
    
# Create a new DataFrame
snowfall_zone_df_all = pd.DataFrame({
    "Forecast Date": forecast_date,
    "Forecast Time": forecast_time_et,
    "Snowfall": snowfall,
    "Snowfall Zone": snowfall_zone_list
})
    
# freezing rain and freezing drizzle (both under freezing rain)
freezing_rain_zone = ""
freezing_rain = forecast_df["Weathercode"] 
freezing_rain_zone_list = []

for i in freezing_rain.index:
    if (pd.isna(freezing_rain[i])):
        freezing_rain_zone = "gray"
    elif (freezing_rain[i] == 66) or (freezing_rain[i] == 67) or (freezing_rain[i] == 56) or (freezing_rain[i] == 57):
        freezing_rain_zone = "red"
        exp = "Freezing rain"
        explanation_df.at[i, 'Explanation']['red'].append(exp)
    else:
        freezing_rain_zone = "green"
        exp = "No freezing rain"
        explanation_df.at[i, 'Explanation']['green'].append(exp)
    freezing_rain_zone_list.append(freezing_rain_zone)


# Create a new DataFrame
freezing_rain_df_all = pd.DataFrame({
    "Forecast Date": forecast_date,
    "Forecast Time": forecast_time_et,
    "Freezing Rain": freezing_rain,
    "Freezing Rain Zone": freezing_rain_zone_list
})

#gust (MAKE SURE TO DOWNLOAD CSV WITH UNITS AS KNOTS)
wind_gusts_zone = ""
wind_gusts = forecast_df["Wind Gusts"] 
wind_gusts_zone_list = []

for i in wind_gusts.index:
    if (pd.isna(wind_gusts[i])):
        wind_gusts_zone = "gray"    
    elif (wind_gusts[i]) >= 30:
        wind_gusts_zone = "red"
        exp = "Wind gust is " + str(round(wind_gusts[i],2)) + " which is greater than the threshold of 30"
        explanation_df.at[i, 'Explanation']['red'].append(exp)
    elif (wind_gusts[i] >= 25):
        wind_gusts_zone = "yellow"
        exp = "Wind gust is " + str(round(wind_gusts[i],2)) + " which is greater than the threshold of 25"
        explanation_df.at[i, 'Explanation']['yellow'].append(exp)
    else:
        wind_gusts_zone = "green"
        exp = "No wind gust"
        explanation_df.at[i, 'Explanation']['green'].append(exp)
    wind_gusts_zone_list.append(wind_gusts_zone)


# Create a new DataFrame
wind_gusts_df_all = pd.DataFrame({
    "Forecast Date": forecast_date,
    "Forecast Time": forecast_time_et,
    "Wind Gusts": wind_gusts,
    "Wind Gusts Zone": wind_gusts_zone_list
})

#temperature 
temperature_zone = ""
temperature = forecast_df["Temperature (°C)"] 
temperature_zone_list = []
for i in temperature.index:
    if (pd.isna(temperature[i])):
        temperature_zone = "gray"
    elif (temperature[i] > 35) or (temperature[i] < -20):
        temperature_zone = "red"
        exp = "Temperature is " + str(round(temperature[i],2)) + " which is less than the threshold of -20 or greater than the threshold of 35"
        explanation_df.at[i, 'Explanation']['red'].append(exp)
    elif (temperature[i] > 30) or (temperature[i] < -10):
        temperature_zone = "yellow"
        exp = "Temperature is " + str(round(temperature[i],2)) + " which is less than the threshold of -10 or greater than the threshold of 30"
        explanation_df.at[i, 'Explanation']['yellow'].append(exp)
    else:
        temperature_zone = "green"
        exp = "Temperature is safe for flight"
        explanation_df.at[i, 'Explanation']['green'].append(exp)
    temperature_zone_list.append(temperature_zone)
# Create a new DataFrame
temperature_df_all = pd.DataFrame({
    "Forecast Date": forecast_date,
    "Forecast Time": forecast_time_et,
    "Temperature": temperature,
    "Temperature Zone": temperature_zone_list
})

sunrise = forecast_df["Sunrise"]
sunset = forecast_df["Sunset"] 
delta_thirty = timedelta(minutes=30)
delta_fifteen = timedelta(minutes=15)

sunrise_sunset_zone = ""
sunrise_sunset_zone_list = []

for i in forecast_time_et.index:
    sunset_30 = datetime.combine(forecast_date[i],sunset[i])
    sunrise_30 = datetime.combine(forecast_date[i],sunrise[i])
    if (forecast_time_et[i] > (sunset_30 + delta_thirty).time()) or (forecast_time_et[i] < (sunrise_30-delta_thirty).time()):
        sunrise_sunset_zone = "red"
        exp = "Time is 30 minutes after sunset or 30 minutes before sunrise"
        explanation_df.at[i, 'Explanation']['red'].append(exp)
        
    elif (((sunset_30 - delta_fifteen).time()) < (forecast_time_et[i]) < (sunset_30 + delta_thirty).time()) or (((sunrise_30 - delta_thirty).time() < (forecast_time_et[i]) < (sunrise_30 + delta_fifteen).time())):
        sunrise_sunset_zone = "yellow"
        exp = "Time is 15 minutes after sunset or 15 minutes before sunrise"
        explanation_df.at[i, 'Explanation']['yellow'].append(exp)
    else:
        sunrise_sunset_zone = "green"
        exp = "Time is safe for flight"
        explanation_df.at[i, 'Explanation']['green'].append(exp)
    sunrise_sunset_zone_list.append(sunrise_sunset_zone)

# Create a new DataFrame
sunrise_sunset_df_all = pd.DataFrame({
    "Forecast Date": forecast_date,
    "Forecast Time": forecast_time_et,
    "Sunrise": sunrise,
    "Sunset": sunset,
    "Sunrise Sunset Zone": sunrise_sunset_zone_list
})
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
    "Sunrise Sunset Zone": sunrise_sunset_zone_list,
    "Explanation": explanation_df['Explanation']
})

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

# print(forecast_time_et)
# forecast_time_et = forecast_time_et
# forecast_df_datetime = pd.to_datetime(forecast_df["Forecast Time"])
# forecast_time_et = forecast_df_datetime.dt.strftime('%H:%M')
# format = '%H:%M'
# string_time = forecast_time_et.strftime(format)
# formatted_list = [forecast_time_et.strftime('%H:%M')]
# formatted_list = [time.strftime('%H:%M') for time in forecast_time_et]
# new_test = pd.DataFrame({
#     "Forecast Time": forecast_time_et,
# })
# new_test["forecast_time_et"] = new_test['forecast_time_et'].dt.strftime('%H:%M')
# print(new_test["forecast_time_et"])test = {"a": 1}

final_zones_color = pd.DataFrame({
    "Forecast Date": forecast_date,
    "Forecast Time": forecast_time_et,
    "Zone": zones_df_all['final_zone'],
    "Explanation": explanation_df['Explanation'] # if yellow or red, add in explanatory data structure
    # {(date, time, zone): [rain > 0, cloud cover > 50%]}
})
#extract each date into its own column
#get rid of the duplicate time columns
#stitch it together in a dataframe

displayhook(final_zones_color.iloc[96])

# Convert each time object to string and remove seconds
formatted_time_series = forecast_time_et.apply(lambda x: x.strftime('%H:%M'))
print(type(formatted_time_series))
# day 1
df0 = final_zones_color.iloc[0:96, 1]
# df0_formatted = df0.apply(lambda x: x.strftime('%H:%M'))
df0 = final_zones_color.iloc[0:96, 1].apply(lambda x: x.strftime('%H:%M'))
df1 = final_zones_color.iloc[0:96, 2:4]

# day 2
df2 = final_zones_color.iloc[96:192, 2:4] 
df2 = df2.reset_index() 

# day 3
df3 = final_zones_color.iloc[192:288, 2:4] 
df3 = df3.reset_index() 

first_date= final_zones_color.iloc[0, 0]
second_date= final_zones_color.iloc[96, 0]
third_date= final_zones_color.iloc[192, 0]


# Converting dates into readable
formatted_first_date = first_date.strftime("%b %d, %Y")
formatted_second_date = second_date.strftime("%b %d, %Y")
formatted_third_date = third_date.strftime("%b %d, %Y")

# df_formatted = pd.DataFrame({'Time': formatted_time_series})

full = [df0, df1, df2, df3]
zones_table = pd.concat(full, axis=1)
zones_table.columns = ["Forecast Time", formatted_first_date, "Explanation 1", "index", formatted_second_date, 
                                "Explanation 2", "index", formatted_third_date, "Explanation 3"]
del zones_table['index']
# separates the explanations from the zone colours
explanation_cols = ["Forecast Time", formatted_first_date, formatted_second_date, formatted_third_date]
removal_cols = ["Forecast Time", "Explanation 1", "Explanation 2", "Explanation 3"]
explanations_table = pd.DataFrame(data=zones_table[["Forecast Time", "Explanation 1", "Explanation 2", "Explanation 3"]], index=zones_table.index)
explanations_table = explanations_table.rename(columns={"Explanation 1": formatted_first_date, "Explanation 2": formatted_second_date, "Explanation 3": formatted_third_date})

# remove the explanation columns from the zones_table
for col in removal_cols[1:]:
    zones_table.pop(col)

for r in zones_table.index:
    for c in zones_table.columns[1:]:
        if zones_table.at[r, c] == "red":
            current_explanation = explanations_table.at[r, c]["red"]
            explanation_str = ", ".join(current_explanation)
            explanations_table.loc[r, c] = explanation_str
        elif zones_table.at[r, c] == "yellow":
            current_explanation = explanations_table.at[r, c]["yellow"]
            explanation_str = ", ".join(current_explanation)
            explanations_table.loc[r, c] = explanation_str
        elif zones_table.at[r, c] == "green":
            current_explanation = explanations_table.at[r, c]["green"]
            explanation_str = ", ".join(current_explanation)
            explanations_table.loc[r, c] = explanation_str


#STEP 1: Find the total flight tight 97.47 -> approx 105 -> 6 or 7 blocks

#STEP 2: Find consecutive timeslots where it's green or yellow
# feasible_flights = pd.DataFrame('number', 'Date', 'Start')
# feasible_flights = pd.DataFrame(columns=["Start Time", "Finish Time"])
start_times = []
finish_times = []

countSafe = 0
countModSafe = 0
cellBlock = 0
#print(zones_table)
#print(zones_table.columns)

# new_full = [df0, df1, df2, df3]
# zones_table_new = pd.concat(full, axis=1)

dayOne = zones_table.iloc[:, 0:2]
date = dayOne.iloc[:, 0]
colour = dayOne.iloc[:, 1]

consecutive = False
number = 0
number_ui = []
# Assuming dayOne is a DataFrame with one column
numRows = len(dayOne[formatted_first_date])
for i in range(numRows):
    count = 0
    if (dayOne.iloc[i, 1] == 'green') and (i != numRows) and (i+1 != numRows) and (i+2 != numRows):
        count += 1
        
        for j in range(i + 1, i + 3):
            
            if dayOne.iloc[j, 1] == 'green': 
                
                count += 1
                if count == 3:
                    consecutive = True
                    StartTime = dayOne.iloc[j-2, 0]
                    

                    FinishTime = dayOne.iloc[j, 0]
                    format = '%H:%M'
                    number += 1
                    StartTime = StartTime.strftime(format)
                    FinishTime = FinishTime.strftime(format)

                    start_times.append(StartTime)
                    finish_times.append(FinishTime)
                    number_ui.append(number)
                    count = 0

            else:
                count = 0            
                consecutive = False

feasible_flights = pd.DataFrame({
    "Flight No.": number_ui,
    "Start Time": start_times,
    "Finish Time": finish_times
})

print(feasible_flights)
