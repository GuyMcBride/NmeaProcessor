import numpy as np
import pandas as pd
import cufflinks as cf
import plotly
import plotly.offline as py
import plotly.graph_objs as go

import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

log.debug("initializing Cufflink...")
cf.go_offline()
log.debug("initializing Plotly...")
# py.init_notebook_mode()

log.debug("Reading csv...")
df = pd.read_csv("InstrumentData2020.csv")
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
