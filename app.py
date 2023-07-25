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
from mysql import connector
import psycopg2
import sqlalchemy as sa

# def connect_to_db(provider: str):
#     conn = psycopg2.connect(
#         user="user",
#         password="YU37CrnJMLjG",
#         host="ep-snowy-pond-543889.us-east-2.aws.neon.tech",
#         port="5432",
#         database="electrifly-db")
#     return conn

def connect_to_db(provider: str):
    provider == "PostgreSQL"
    db_url = "postgresql+psycopg2://user:YU37CrnJMLjG@ep-snowy-pond-543889.us-east-2.aws.neon.tech:5432/electrifly-db"
    engine = sa.create_engine(db_url)
    return engine


plane_data_df = pd.DataFrame(
                {"Id": [2345, 2346, 2347, 2348,0,0,0,0,0,0,0,0,0,0], 
                 "Battery 1 SOC": [100, 87, 61, 43,0,0,0,0,0,0,0,0,0,0], 
                 "Battery 2 SOC": [100, 88, 61, 43,0,0,0,0,0,0,0,0,0,0], 
                 "Battery 1 Average Temperature (°C)": [19, 21, 24, 25,0,0,0,0,0,0,0,0,0,0], 
                 "Battery 2 Average Temperature (°C)": [19, 20, 24, 25,0,0,0,0,0,0,0,0,0,0],
                 "Indicated Airspeed (Knots)": [0, 59.71556, 71.93128, 83.11363,0,0,0,0,0,0,0,0,0,0], 
                 "Requested Torque": [0, 857, 758, 385,0,0,0,0,0,0,0,0,0,0]})
 # Define the list of columns to be initially shown in the collapsed view


app_ui = ui.page_navbar(
    shinyswatch.theme.zephyr(),
    ui.nav("Upload Data",
           ui.download_button("downloadData", "Flight & Weather Data Refresh", style="background-color: #007bff; color: white;"),
           "\n ",
        #    ui.input_select(
        #    "selection_mode",
        #    "Selection mode",
        #    {"none": "(None)", "single": "Single", "multiple": "Multiple"},
        #    selected="multiple",
        # ),
            # ui.input_switch("gridstyle", "Grid", True),
            # ui.input_switch("fullwidth", "Take full width", True),
            # ui.input_switch("fixedheight", "Fixed height", True),
            
            # ui.div(ui.input_switch("fixedheight", "Fixed height", True), 
            #        ui.input_switch("expandDataGrid", "Expand Table", False),
            #        style="margin-top: 20px;"),

            # ui.h2("Shiny for Python Database Connections"),
            # #ui.input_select(id="select_db", label="Selected Database:", choices=["MySQL", "PostgreSQL"], selected="MySQL"),
            # ui.hr(),
            # ui.output_text(id="out_db_details"),
            # ui.output_table(id="out_table"),
           
            # ui.page_fixed(
            # ui.div(
                # ui.include_css("bootstrap.css"), ui.h1("Most Recent Records"), 
                # style="margin-top: 20px;"),
            ui.div(ui.input_switch("expandDataGrid", "Expand Columns", False),
                style="margin-top:40px;"),
            ui.row(
            ui.column(4.5,
            ui.div(
                ui.include_css("bootstrap.css"), ui.h4("Most Recent Flight and Weather Data Records"), 
                style="margin-top: 3px;"),
            ),
            # ui.column(2,
            #     ui.div(ui.input_switch("expandDataGrid", "Expand Columns", False),
            #     style="margin-top: 10px;"),
            # ),
            
            ),
            # style="float:left" ),
           
            ui.div(ui.output_data_frame("data_df"),
                    ui.include_css("bootstrap.css"),
                    style="margin-top: 2px; max-height: 3000px;",
                   ),
            
        #     ui.panel_fixed(
        #     ui.output_text_verbatim("detail"),
        #     right="10px",
        #     bottom="10px",
        #     top="10px",
        # ),
            
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

    # @reactive.Calc
    # def db_info():
    #     if input.select_db() == "MySQL":
    #         conn = connect_to_db(provider="MySQL")
    #         stmt = "SELECT CONCAT(VERSION(), ' | ', CURRENT_USER());"
    #     else:
    #         conn = connect_to_db(provider="PostgreSQL")
    #         stmt = "SELECT datname || ' | ' || datid FROM pg_stat_activity WHERE state = 'active';"
    #     cursor = conn.cursor()
    #     cursor.execute(stmt)
    #     res = cursor.fetchall()
    #     conn.close()
    #     return str(res[0])

    # @reactive.Calc
    # def data():
    #     conn = connect_to_db(provider=input.select_db())
    #     stmt = "SELECT * FROM combined_flight_weather_data"
    #     df = pd.read_sql(stmt, con=conn)
    #     return df


    @reactive.Calc
    def data():
        engine = connect_to_db("PostgreSQL")
            
        # # Define the table names outside of the data() function
        # metadata = sa.MetaData()
        # flight_weather_table = sa.Table('flight_weather', metadata, autoload=True, autoload_with=engine)
        # weather_table = sa.Table('weather', metadata, autoload=True, autoload_with=engine)
        
        # # Define the function to get flight data
        # def get_flight_data(flight_id):
        #     table_name = f"flightdata_{flight_id}"
        #     flightdata_table = sa.Table(table_name, metadata, autoload=True, autoload_with=engine)
        #     return sa.select([flightdata_table]).where(flightdata_table.c.flight_id == flight_id)
        
        # # Define the main query
        # combined_query = sa.select([
        #     flight_weather_table.c.flight_id.label('fw_flight_id'),
        #     *get_flight_data(flight_weather_table.c.flight_id).columns,
        #     weather_table
        # ]).select_from(
        #     flight_weather_table.join(weather_table, flight_weather_table.c.weather_id == weather_table.c.id)
        # ).apply_labels()

        query = "SELECT * FROM flight_weather_data_view LIMIT 10;"
        
        # Execute the query and fetch the data into a DataFrame
        data_df = pd.read_sql(query, con=engine)
        return data_df




    # @output
    # @render.text
    # def out_db_details():
    #     return f"Current database: {db_info()}"

    # @output
    # @render.table
    # def out_table():
    #     return data()
    
    # df: reactive.Value[pd.DataFrame] = reactive.Value(plane_data_df)
   
    @output
    @render.data_frame
    def data_df():
        if input.expandDataGrid():
            return data()
        else:
            data_df = data()
            collapsed_columns = data_df.loc[:,["flight_id", "time_min", "bat_1_current",
                                               "bat_2_current","bat_1_voltage", "bat_2_voltage", "bat_1_soc", 
                                               "bat_2_soc","requested_torque","motor_power", "motor_temp", "pitch", "roll"]]
            return collapsed_columns
        
    # def grid():
    #     # height = 350 if input.fixedheight() else None
    #     # width = "100%" if input.fullwidth() else "fit-content"
    #     # if input.gridstyle():
        
    #     return render.DataGrid(
                
    #             df(),

    #             # row_selection_mode=input.selection_mode(),
    #             # height=height,
    #             # width=width,
    #         )
    #     # else:
    #     #     return render.DataTable(
    #     #         df(),
    #     #         row_selection_mode=input.selection_mode(),
    #     #         height=height,
    #     #         width=width,
    #     #     )

    # @reactive.Effect
    # @reactive.event(input.grid_cell_edit)
    # def handle_edit():
    #     edit = input.grid_cell_edit()
    #     df_copy = df().copy()
    #     df_copy.iat[edit["row"], edit["col"]] = edit["new_value"]
    #     df.set(df_copy)

    # @output
    # @render.text
    # def detail():
    #     if (
    #         input.grid_selected_rows() is not None
    #         and len(input.grid_selected_rows()) > 0
    #     ):
    #         # "split", "records", "index", "columns", "values", "table"
    #         return df().iloc[list(input.grid_selected_rows())]
   
    # @reactive.Effect
    # @reactive.event(input.expandDataGrid)
    # def expand_collapse_data_grid():
    #     columns_to_show = df().columns if input.expandDataGrid else collapsed_columns
    #     df_copy = df()[columns_to_show]
    #     df.set(df_copy)


app = App(app_ui, server)
