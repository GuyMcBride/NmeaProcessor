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
conversions = {
    "wind": complex,
    "water": complex,
    "ground": complex,
    "position": complex,
}
df = df.astype(conversions)

print(df.info())

apparent_wind = pd.DataFrame(
    data={
        "datetime": df.datetime,
        "speed": np.absolute(df.wind),
        "angle": np.angle(df.wind),
    }
)

print(apparent_wind.info())
pass

app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.P("Color:"),
        dcc.Dropdown(
            id="dropdown",
            options=[
                {"label": x, "value": x}
                for x in ["Gold", "MediumTurquoise", "LightGreen"]
            ],
            value="Gold",
            clearable=False,
        ),
        dcc.Graph(id="graph"),
    ]
)


@app.callback(Output("graph", "figure"), [Input("dropdown", "value")])
def display_color(color):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            y=apparent_wind.speed,
            x=apparent_wind.datetime,
            mode="markers",
            marker_color=color,
        )
    )
    return fig


app.run_server(debug=True)
