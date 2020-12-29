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

df["wind_apparent_raw_speed"] = np.absolute(df.wind)
df["wind_apparent_raw_angle"] = np.angle(df.wind)

print(df.info())

app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.P("Color:"),
        dcc.Dropdown(
            id="dropdown",
            options=[
                {"label": x, "value": x}
                for x in df.index.map(pd.Timestamp.date).unique()
            ],
            value=df.index.map(pd.Timestamp.date).unique()[0],
            clearable=False,
        ),
        dcc.Graph(id="graph"),
    ]
)


@app.callback(Output("graph", "figure"), [Input("dropdown", "value")])
def display_date(date):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            y=df.loc[date].wind_apparent_raw_speed,
            x=df.loc[date].index,
            mode="markers",
        )
    )
    return fig


app.run_server(debug=True)
