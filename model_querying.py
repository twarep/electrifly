import pandas as pd
import numpy as np
import os
import joblib
from flight_querying import query_flights



def get_model_prediction(activity, time, power, temperature, visibility, windspeed):

    # Get the connection and 
    activites_conn = query_flights()
    all_activities = activites_conn.get_unique_activity()

    # make columns
    data_dict = {
        "Time Delta": [time], 
        "Average Power": [power], 
        "temperature": [temperature], 
        "Visibility": [visibility], 
        "Wind Speed": [windspeed]
    }

    # Prefix the activities with is_
    for operation in all_activities:
        if operation not in ("NA", "TBD"):
            operation_column = "Activity_is_" + operation
            
            if activity in operation_column:
                data_dict[operation_column] = [True]
            else:
                data_dict[operation_column] = [False]

    # Make the pandas df for 
    pred_dict = pd.DataFrame(data_dict)

    # Get the trained model
    model_filename = 'ML_model_outputs/prescription_linreg_model.joblib'
    model = joblib.load(model_filename)

    prediction = model.predict(pred_dict)

    print(prediction)


get_model_prediction("cruise", 5, 30, 34, 3, 8)