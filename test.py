from flight_querying import query_flights
from weather_querying import query_weather
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
import pandas as pd
import plotly.express as px
import plotly.io as pio


# Load .env file
load_dotenv()

mapbox_access_token = os.getenv('MAPBOX_PUBLIC_TOKEN')

# https://medium.com/technology-hits/working-with-maps-in-python-with-mapbox-and-plotly-6f454522ccdd

wwfc_lat = 43.45567935107457
wwfc_lon = -80.3881582036048

gps_df = pd.DataFrame({"Lat": [wwfc_lat], "Long": [wwfc_lon]})

# fig = go.Figure(go.Scattermapbox(
#         lat=[wwfc_lat],
#         lon=[wwfc_lon],
#         mode='markers',
#         marker=go.scattermapbox.Marker(
#             size=14
#         ),
#         text=['WWFC'],
#     ))

# fig.update_layout(
#     hovermode='closest',
#     mapbox=dict(
#         accesstoken=mapbox_access_token,
#         style="mapbox://styles/vik01/clki9bf0f00ly01qmdmx7bh0a",
#         bearing=0,
#         center=go.layout.mapbox.Center(
#             lat=wwfc_lat,
#             lon=wwfc_lon
#         ),
#         pitch=0,
#         zoom=20
#     )
# )

fig = px.scatter_mapbox(gps_df, lat="Lat", lon="Long",
                  color_continuous_scale=["black", "purple", "red" ], size_max=30, zoom=12.5,
                  height = 600, width = 1000, #center = dict(lat = g.center)
                        title='Pipistrel Velis Electro Flight',
                       #mapbox_style="open-street-map"
                       )
fig.update_layout(font_size=16,  title={'xanchor': 'center','yanchor': 'top', 'y':0.9, 'x':0.5,}, 
        title_font_size = 24, mapbox_accesstoken=mapbox_access_token, mapbox_style = "mapbox://styles/vik01/clki9bf0f00ly01qmdmx7bh0a")
fig.update_traces(marker=dict(size=6))

fig.show()