from shiny import App, render, ui, Inputs, Outputs, Session, reactive
from shiny.types import NavSetArg
from typing import List
from htmltools import css
import shinyswatch
import numpy as np
import matplotlib.pyplot as plt

import asyncio
from datetime import date
import numpy as np

from ipywidgets import widgets, interactive

app_ui = ui.page_navbar(
    shinyswatch.theme.zephyr(),
    ui.nav("Upload Data",
           ui.download_button("downloadData", "Flight & Weather Data Refresh", style="background-color: #007bff; color: white;"),
           "\n "),
    ui.nav("Data Analysis", ui.div("SOC vs. Time Across Multiple Flights"), ui.output_plot("basic_plot")),
    ui.nav("Recommendations", "recommendations content"),
    title="Electrifly UI"
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
    @render.plot(alt="A basic plot")
    def basic_plot():
        x = [1, 2, 3]
        y = [1, 2, 3]
        plt.plot(x, y)


app = App(app_ui, server, debug=True)
