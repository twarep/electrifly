from shiny import App, render, ui, Inputs, Outputs, Session, reactive
from shiny.types import NavSetArg
from typing import List
from htmltools import css
import shinyswatch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import asyncio
from datetime import date
import numpy as np
from os import listdir
from os.path import isfile, join

mypath = "./test_data/"


def get_test_data(only_data = True):
    # Set up data names variable
    data_file_names = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    # Return if only names were specified
    if only_data:
        return [name[14:name.index('.')].replace('.csv', '').replace('-', ' ').capitalize()
                for name in data_file_names]
    # Data variables
    data = {}
    # Get all data from files and store in data dictionary
    for file in data_file_names:
        data_df = pd.read_csv(join(mypath, file))
        soc = (data_df[' bat 1 soc'].to_numpy() + data_df[' bat 2 soc'].to_numpy()) / 2
        time_minutes = data_df[' time(min)'].to_numpy()
        data[file[14:file.index('.')].replace('.csv', '').replace('-', ' ').capitalize()] = {'soc': soc, 'time': time_minutes}
    # Return data
    return data


# ui.output_plot("basic_plot"),
app_ui = ui.page_navbar(
    shinyswatch.theme.zephyr(),
    ui.nav("Upload Data",
           ui.download_button("downloadData", "Flight & Weather Data Refresh", style="background-color: #007bff; color: white;"),
           "\n "
        ),
    ui.nav("Data Analysis", 
            ui.div("SOC vs. Time Across Multiple Flights"), 
            ui.layout_sidebar(
                ui.panel_sidebar(
                    ui.input_select(
                        "state",
                        "Choose flight date(s):",
                        get_test_data(),
                        selected=get_test_data()[0],
                        multiple=True,
                    )
                ),
                ui.panel_main(
                    ui.output_plot("interactive")
                ),
            ),
        ),  
    ui.nav("Recommendations", 
           "recommendations content"),
    title="Electrifly UI",
)

#arbitrarly downloads this random doc -> functionality needs to change
def server(input: Inputs, output: Outputs, session: Session):

    @session.download(
        filename=lambda: f"{date.today().isoformat()}-{np.random.randint(100,999)}.csv"
    )
    async def downloadData():
        await asyncio.sleep(0.25)
        yield "one,two,three\n"


    @output
    @render.plot(alt="An interactive plot")
    def interactive():
        # Get the data from the 
        data = get_test_data(False)

        # Plot the graphs
        for date in input.state():
            if date in data.keys():
                soc = data[date]['soc']
                time = data[date]['time']
                plt.plot(time, soc, label=date)

        # Add labels and legend to plot
        plt.xlabel("time (min)")
        plt.ylabel("SOC")
        plt.title("Time vs SOC")
        plt.legend(loc="lower left")



app = App(app_ui, server, debug=True)
