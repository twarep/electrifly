from shiny import App, render, ui, Inputs, Outputs, Session, reactive
from shiny.types import NavSetArg
from typing import List
from htmltools import css
import shinyswatch

app_ui = ui.page_navbar(
    shinyswatch.theme.zephyr(),
    ui.nav("Upload Data","upload data content"),
    ui.nav("Data Analysis", "data analysis content"),
    ui.nav("Reccomendations", "reccomendations content"),
    title="Electrifly UI",
    
)


def server(input, output, session):
    @output
    @render.text
    def txt():
        return f"n*2 is {input.n() * 69}"


app = App(app_ui, server)
