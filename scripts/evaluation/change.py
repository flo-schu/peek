import pandas as pd
from matplotlib import pyplot as plt

data = pd.read_csv("data/measurements.csv", index_col="time", infer_datetime_format=True, parse_dates=["time"])


data

data["culex_small"] = data["culex_small"].fillna(0)
data["culex_manual"] = data.culex_larvae + data.culex_small


plt.scatter(data.temperature, data.culex_manual) # no effect
plt.scatter(data.temperature, data.culex_repro, alpha=.1)
plt.scatter(data.daphnia_count, data.culex_small + data.culex_larvae, alpha=.25 )
plt.ylim(0,200)
plt.xlim(0,200)
plt.xlabel("Daphnia")
plt.ylabel("Culex")