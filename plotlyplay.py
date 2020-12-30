import numpy as np
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

log.debug("Reading csv...")
df = pd.read_csv("InstrumentData2020.csv", index_col=0)
df["datetime"] = pd.to_datetime(df["datetime"])
df = df.set_index("datetime")
conversions = {
    "wind": complex,
    "water": complex,
    "ground": complex,
    "position": complex,
}
df = df.astype(conversions)
df.rename(
    columns={"depth": "depth_raw", "temperature": "temperature_raw"}, inplace=True
)

df["depth_filtered"] = np.convolve(df["depth_raw"], np.ones(10) / 10, mode="same")
df["temperature_filtered"] = np.convolve(
    df["temperature_raw"], np.ones(10) / 10, mode="same"
)

df["wind_apparent_speed_raw"] = np.absolute(df.wind)
df["wind_apparent_angle_raw"] = np.degrees(np.angle(df.wind))
df["wind_filtered"] = np.convolve(df["wind"], np.ones(50) / 50, mode="same")
df["wind_apparent_speed_filtered"] = np.absolute(df["wind_filtered"])
df["wind_apparent_angle_filtered"] = np.degrees(np.angle(df["wind_filtered"]))

print(df.info())

app = dash.Dash(__name__)

fields = df.select_dtypes(exclude=[complex]).columns
fields = fields.map(lambda x: x.rsplit("_", 1)[0]).unique()

app.layout = html.Div(
    [
        html.P("Date:"),
        dcc.Dropdown(
            id="date_dropdown",
            options=[
                {"label": x, "value": x}
                for x in df.index.map(pd.Timestamp.date).unique()
            ],
            value=df.index.map(pd.Timestamp.date).unique()[0],
            clearable=False,
        ),
        html.P("Field:"),
        dcc.Dropdown(
            id="field_dropdown",
            options=[{"label": x, "value": x} for x in fields],
            value=fields[0],
            clearable=False,
        ),
        dcc.Graph(id="graph"),
    ]
)


@app.callback(
    Output("graph", "figure"),
    [Input("date_dropdown", "value"), Input("field_dropdown", "value")],
)
def display_date(date, field):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            y=df.loc[date][field + "_raw"],
            x=df.loc[date].index,
            mode="markers",
        )
    )
    fig.add_trace(
        go.Scatter(
            y=df.loc[date][field + "_filtered"],
            x=df.loc[date].index,
            mode="lines",
        )
    )
    return fig


app.run_server(debug=True)
