import pandas as pd

last_measurement = pd.read_csv("data/measurements.csv") \
    .groupby("id") \
    .last()

last_measurement.to_csv("data/groups/input_data.csv")