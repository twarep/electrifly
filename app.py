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

plane_data_df = pd.DataFrame(
                {"Id": [2345, 2346, 2347, 2348], 
                 "Battery 1 SOC": [100, 87, 61, 43], 
                 "Battery 2 SOC": [100, 88, 61, 43], 
                 "Battery 1 Average Temperature (°C)": [19, 21, 24, 25], 
                 "Battery 2 Average Temperature (°C)": [19, 20, 24, 25],
                 "Indicated Airspeed (Knots)": [0, 59.71556, 71.93128, 83.11363], 
                 "Requested Torque": [0, 857, 758, 385]})
 # Define the list of columns to be initially shown in the collapsed view
collapsed_columns = plane_data_df.loc[:,["Indicated Airspeed (Knots)","Requested Torque","Battery 2 Average Temperature (°C)"]]



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
            ui.div(ui.input_switch("expandDataGrid", "Expand Table", False),
                   style="margin-top: 20px;",
                   ),
            ui.div(ui.output_data_frame("plane_data"),
                    ui.include_css("bootstrap.css"),
                    style="margin-top: 20px;",
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
    # df: reactive.Value[pd.DataFrame] = reactive.Value(plane_data_df)
   
    @output
    @render.data_frame
    def plane_data():
        if input.expandDataGrid():
            return plane_data_df
        else: 
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
