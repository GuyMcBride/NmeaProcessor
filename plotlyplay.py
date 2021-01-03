import numpy as np
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

import logging

import instrumentProcessing as inst

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

log.debug("Reading csv...")
inst.get_instrument_data("InstrumentData2020.csv")

print(inst.df.info())

app = dash.Dash(__name__)

fields = inst.df.select_dtypes(exclude=[complex]).columns
fields = fields.map(lambda x: x.rsplit("_", 1)[0]).unique()

app.layout = html.Div(
    [
        html.P("Date:"),
        dcc.Dropdown(
            id="date_dropdown",
            options=[
                {"label": x, "value": x}
                for x in inst.df.index.map(pd.Timestamp.date).unique()
            ],
            value=inst.df.index.map(pd.Timestamp.date).unique()[0],
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
            y=inst.df.loc[date][field + "_raw"],
            x=inst.df.loc[date].index,
            mode="markers",
        )
    )
    fig.add_trace(
        go.Scatter(
            y=inst.df.loc[date][field + "_filtered"],
            x=inst.df.loc[date].index,
            mode="lines",
        )
    )
    return fig


app.run_server(debug=True)
