from shiny import App, render, ui, Inputs, Outputs, Session, reactive
from shiny.types import NavSetArg
from typing import List
from htmltools import css
import shinyswatch

import asyncio
from datetime import date
import numpy as np

app_ui = ui.page_navbar(
    shinyswatch.theme.zephyr(),
    ui.nav("Upload Data","upload data content"),
    ui.nav("Data Analysis", "data analysis content"),
    ui.nav("Reccomendations", "reccomendations content"),
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


app = App(app_ui, server)
