from shiny import App, render, ui, Inputs, Outputs, Session, reactive
from shiny.types import NavSetArg
from typing import List
from htmltools import css

app_ui = ui.page_fluid(
    ui.tags.style(
        """
        .nav-pills {
            background: rgba(130, 189, 245, 0.8);
        }
        .nav-pills .nav-link{
            color: black;
        }
        .nav-pills .nav-link.active{
            background: rgba(39, 99, 168, 0.8);
            color: white;
        }
        .nav-pills a:hover {
            background: rgba(130, 189, 245, 0.8);
            color: white; 
        }
        """
    ),
    ui.navset_pill(
        
        ui.nav("Upload Data",
               "upload data content"),
        ui.nav("Data Analysis", 
               "data analysis content"),
        ui.nav("Reccomendations", 
               "reccomendations content"),
    ),
    
)


def server(input, output, session):
    @output
    @render.text
    def txt():
        return f"n*2 is {input.n() * 69}"


app = App(app_ui, server)
