import subprocess
import time
from datetime import datetime

# Define the times at which you want to run the scraper.py script
scheduled_times = ["08:00", "12:00", "16:00", "21:29", "21:42", "00:00"]

# Define the path to your scraper.py script
scraper_script_path = "scraper.py"

# Variable to store the timestamp of the most recent run
most_recent_run_time = None

def run_scraper():
    global most_recent_run_time
    current_time = time.strftime("%H:%M")

    if current_time in scheduled_times:
        print(f"Running scraper.py at {current_time}")
        subprocess.run(["python", scraper_script_path])
        most_recent_run_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Sleep for a minute before checking the time again
    time.sleep(60)

# Function to get the most recent run time
def get_most_recent_run_time():
    return most_recent_run_time

while True:
    run_scraper()
