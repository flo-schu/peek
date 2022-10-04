import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter  
from matplotlib.cm import get_cmap
from matplotlib.lines import Line2D


data = pd.read_csv("data/measurements.csv", infer_datetime_format=True, parse_dates=["time"])
data = data.set_index(["id", "time"]) \
    .sort_index() 




def interpolate(df, cols="all"):
    if cols == "all":
        cols = df.columns
    df = df.loc[:, cols] \
        .reset_index().set_index("time") \
        .groupby("id") \
        .apply(lambda g: g.interpolate("time", limit_direction="forward", limit=2)) \
        .reset_index().set_index(["id", "time"]) \
        .fillna(0) 

    return df


statevars = [
    "count_D_adult", "count_D_juvenile", "count_D_neo", 
    "culex_larvae", "culex_small", "culex_pupae", "culex_adults",
    "cell_vol_large", "oxygen"
]

states = interpolate(data, statevars).query("time > '2021-04-06'") \
    .assign(culex = lambda df: df.culex_larvae) \
    .assign(daphnia = lambda df: df.count_D_adult + df.count_D_juvenile + df.count_D_neo) \
    .rename(columns={"cell_vol_large":"food_concentration"}) \
    .loc[:, ["culex", "daphnia", "food_concentration", "oxygen"]]

svars = states.columns

esfen = data.xs("2021-06-03", level="time")["esfenvalerate"].to_frame()
esfen["esfenvalerate"] = np.where(esfen == 0, 0.01, esfen)
times = np.unique(states.index.get_level_values("time"))
nanos = np.unique(states.index.get_level_values("id"))

# ------------------------- Trajectories ---------------------------------------


# select colors and contruct legend
cmap = get_cmap("viridis")
colors = cmap(np.linspace(0,1, 5))
esf = pd.DataFrame([
    [0.01, 0.1, 1, 10, 100],
    colors,
    ["control", 0.1, 1, 10, 100]
]).T.rename(columns={0:"esfenvalerate", 1:"color", 2:"label"})

legend_elements = []
for c, l in zip(esf.color, esf.label):
    line = Line2D([0], [0], color=c, marker="o", alpha=.5, label=l, linestyle="-")
    legend_elements.append(line)

# plot figure
fig = plt.figure()
fig.set_size_inches(10,10)

ax = fig.add_subplot(projection="3d")

for n in nanos:
    treatment = esf.query("esfenvalerate == {}".format(esfen.loc[n, :].values))
    s = states.xs(n, level="id")
    td = (s.index-s.index[0]).astype("timedelta64[h]")/24
    td = np.array(td / max(td))

    for i in range(len(s)-2):
        d = s.iloc[i:i+2, :]
        
        step = ax.plot(d.daphnia, d.culex, d.food_concentration, color=treatment.color.values[0], marker="o", alpha=td[i])
    ax.set_xlabel("Daphnia abundance")
    ax.set_ylabel("Culex abundance")
    ax.set_zlabel("Food")
    ax.set_zscale("log")
    ax.set_xlim(0, 150)
    ax.set_ylim(0, 150)
    ax.set_zlim(0.01, 1)
    ax.legend(handles=legend_elements, loc='upper right')

plt.savefig("plots/analysis/trajectories.jpg", dpi=200)
