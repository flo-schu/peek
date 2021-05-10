import pandas as pd


def read(filename):
    return pd.read_csv(filename, index_col=["time","msr_id"])

match = read("data/measurements/match.txt")
temperature = read("data/measurements/temperature.txt")
oxygen = read("data/measurements/oxygen.txt")
nutrients = read("data/measurements/nutrients.txt")
turbidity = read("data/measurements/turbidity.txt")
conductivity = read("data/measurements/conductivity.txt")
pH = read("data/measurements/pH.txt")

data = match
data = data.merge(conductivity,  how="left", left_index=True, right_index=True)
data = data.merge(temperature,   how="left", left_index=True, right_index=True)
data = data.merge(oxygen,        how="left", left_index=True, right_index=True)
data = data.merge(nutrients,     how="left", left_index=True, right_index=True)
data = data.merge(turbidity,     how="left", left_index=True, right_index=True)
data = data.merge(pH,            how="left", left_index=True, right_index=True)

data.rename(columns={"nano_id":"id"}) \
    .reset_index() \
    .drop(columns="msr_id") \
    .set_index(["time","id"]) \
    .to_csv("data/measurements.csv")
