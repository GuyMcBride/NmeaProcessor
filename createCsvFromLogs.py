import pandas as pd
import numpy as np
import os
import logging

import InstrumentState2

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

instrument_path = r"C:\Users\guymc\OneDrive\Sailing\2020"
first = True
for filename in os.listdir(instrument_path):
    if filename.endswith(".log"):
        filename = os.path.join(instrument_path, filename)
        logging.info(f"Getting from {filename}")
        instruments = InstrumentState2.Instruments()
        with open(filename, "r") as log:
            for line in log:
                instruments.process_sentence(line)

        new_df = pd.DataFrame()
        new_df["timedate"] = instruments.datetime
        new_df["position"] = instruments.position
        new_df["depth"] = instruments.depth
        new_df["temperature"] = instruments.water_temperature
        new_df["ground"] = instruments.ground_velocity
        new_df["water"] = instruments.water_velocity
        new_df["wind"] = instruments.wind_apparent

        if first:
            df = new_df.copy()
            first = False
        else:
            df = df.append(new_df)

df.sort_values(by=["timedate"], inplace=True)
df.to_csv(r"InstrumentData2020.csv", index=False)
pass