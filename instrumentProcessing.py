import numpy as np
import pandas as pd

df = pd.DataFrame()


def get_instrument_data(filename):
    global df
    df = pd.read_csv(filename, index_col=0)
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
        columns={
            "depth": "depth_raw",
            "temperature": "temperature_raw",
            "wind": "wind_apparent_raw",
            "water": "water_raw",
            "ground": "ground_raw",
        },
        inplace=True,
    )
    create_polars()
    create_true_wind()
    create_filtereds(30)
    return df


def create_polars():
    global df
    for column in df.columns:
        if isinstance(df[column][0], complex):
            create_polar(column)
    return


def create_filtereds(points):
    global df
    for column in df.columns:
        create_filtered(column, points)
    return


def create_polar(field, bearing=False):
    global df
    parts = field.rsplit("_", 1)
    if len(parts) > 1:
        df[parts[0] + "_speed_" + parts[1]] = np.absolute(df[field])
        df[parts[0] + "_angle_" + parts[1]] = np.degrees(np.angle(df[field]))
        if bearing:
            df[parts[0] + "_angle_" + parts[1]].map(
                lambda x: x if x > 0 else 360 * x,
                inplace=True,
            )
    return


def create_filtered(field, points):
    global df
    parts = field.rsplit("_", 1)
    if len(parts) > 1:
        df[parts[0] + "_filtered"] = np.convolve(
            df[field], np.ones(points) / points, mode="same"
        )
    return


def create_true_wind():
    global df
    water_speed = np.absolute(df["water_speed_raw"])
    water_speed = water_speed.map(lambda x: complex(x, 0))
    df["wind_true_raw"] = df["wind_apparent_raw"] - water_speed
    create_polar("wind_true_raw")
    return