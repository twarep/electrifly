import subprocess
import time

# Define the times at which you want to run the scraper.py script
scheduled_times = ["08:00", "12:00", "16:00", "20:00", "00:00"]

# Define the path to your scraper.py script
scraper_script_path = "scraper.py"

while True:
    current_time = time.strftime("%H:%M")
    
    if current_time in scheduled_times:
        print(f"Running scraper.py at {current_time}")
        subprocess.run(["python", scraper_script_path])
    
    # Sleep for a minute before checking the time again
    time.sleep(60)
