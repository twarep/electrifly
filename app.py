from shiny import App, render, ui, Inputs, Outputs, Session, reactive
from shiny.types import NavSetArg
from typing import List
from htmltools import css
import shinyswatch
import pandas as pd
import asyncio
from datetime import date
import numpy as np
import shiny.experimental as x
import psycopg2
import sqlalchemy as sa


def connect_to_db(provider: str):
    provider == "PostgreSQL"
    db_url = "postgresql+psycopg2://user:YU37CrnJMLjG@ep-snowy-pond-543889.us-east-2.aws.neon.tech:5432/electrifly-db"
    engine = sa.create_engine(db_url)
    return engine

app_ui = ui.page_navbar(
    shinyswatch.theme.zephyr(),
    ui.nav("Upload Data",
           ui.download_button("downloadData", "Flight & Weather Data Refresh", style="background-color: #007bff; color: white;"),
           "\n ",

            ui.div(ui.input_switch("expandDataGrid", "Expand Columns", False),
                style="margin-top:40px;"),

            ui.div(
                ui.include_css("bootstrap.css"), ui.h4("Most Recent Flight and Weather Data Records"), 
                style="margin-top: 3px;"),  

            ui.div(ui.output_data_frame("data_df"),
                    ui.include_css("bootstrap.css"),
                    style="margin-top: 2px; max-height: 3000px;",),
           ),
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

    @reactive.Calc
    def data():
        engine = connect_to_db("PostgreSQL")
        query = "SELECT * FROM flight_weather_data_view LIMIT 10;"
        # Execute the query and fetch the data into a DataFrame
        data_df = pd.read_sql(query, con=engine)
        return data_df
    
    @output
    @render.data_frame
    def data_df():
        if input.expandDataGrid():
            return data()
        else:
            data_df = data()
            collapsed_columns = data_df.loc[:,["flight_id", "time_min", "bat_1_current",
                                               "bat_2_current","bat_1_voltage", "bat_2_voltage", "bat_1_soc", 
                                               "bat_2_soc","motor_power", "motor_temp"]]
            return collapsed_columns

app = App(app_ui, server)