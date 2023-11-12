from datetime import datetime, timedelta
current_date = datetime.now()

# Format the date as a string in the format YYYY-MM-DD


print(current_date)

forecast_date=current_date+timedelta(days=2)
formatted_date = forecast_date.strftime('%Y-%m-%d')
print(formatted_date)