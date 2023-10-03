from datetime import datetime, date

str_datetime = "Oct. 1, 2023, 8:20 PM"
if "." in str_datetime:
  format = "%b. %d, %Y, %I:%M %p"
else:
  format = "%B %d, %Y, %I:%M %p"
conv = datetime.strptime(str_datetime, format)
print(conv)
test = datetime(2023, 10, 1, 20, 20)
print(test)
