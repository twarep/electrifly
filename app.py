from shiny import App, render, ui, Inputs, Outputs, Session, reactive
from shiny.types import NavSetArg
from typing import List
from htmltools import css
import shinyswatch

import asyncio
from datetime import date
import numpy as np

import shiny.experimental as x

app_ui = ui.page_navbar(
    shinyswatch.theme.zephyr(),
    ui.nav("Upload Data",
           ui.download_button("downloadData", "Flight & Weather Data Refresh", style="background-color: #007bff; color: white;"),
           "\n "),
    ui.nav("Data Analysis", 
           ui.include_css("bootstrap.css"),
           x.ui.card(
                x.ui.card_header("Welcome to ElectriFly's Data Analytics Interface!"),
                # x.ui.card_body("Unlock the power of your data with our intuitive and powerful user interface designed specifically for data analytics. Our platform empowers you to transform raw data into actionable insights, enabling you to make informed decisions and drive your business forward.")
                ),
            ),
    ui.nav("Recommendations", "In Construction! ML Predictions on the way!"),
    title="ElectriFly UI",

)

#arbitrarly downloads this random doc -> functionality needs to change
def server(input: Inputs, output: Outputs, session: Session):
    @session.download(
        filename=lambda: f"{date.today().isoformat()}-{np.random.randint(100,999)}.csv"
    )
    async def downloadData():
        await asyncio.sleep(0.25)
        yield "one,two,three\n"


app = App(app_ui, server)
